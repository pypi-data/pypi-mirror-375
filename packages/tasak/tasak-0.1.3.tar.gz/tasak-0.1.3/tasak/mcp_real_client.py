"""Real MCP client implementation using official MCP SDK."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters
import logging
from .core.tool_service import ToolService

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

CACHE_EXPIRATION_SECONDS = 15 * 60  # 15 minutes
AUTH_FILE_PATH = Path.home() / ".tasak" / "auth.json"


class MCPRealClient:
    """Synchronous wrapper around async MCP client."""

    def __init__(self, app_name: str, app_config: Dict[str, Any]):
        self.app_name = app_name
        self.app_config = app_config
        # Check for dynamic config first (used by mcp-remote)
        if "_mcp_config" in app_config:
            self.mcp_config = app_config["_mcp_config"]
            # mcp-remote handles its own auth, don't check auth.json
            self.requires_auth = False
        else:
            self.mcp_config = self._load_mcp_config(app_config.get("config"))
            self.requires_auth = app_config.get("requires_auth", True)
        self.cache_path = self._get_cache_path(app_name)
        # Unified core service
        self._svc = ToolService()

    def _load_mcp_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load MCP configuration from file."""
        if not config_file:
            return {
                "transport": "sse",
                "url": "http://localhost:8080/sse",
                "headers": {},
            }

        config_path = Path(config_file)
        if not config_path.exists():
            print(f"Warning: Config file {config_file} not found", file=sys.stderr)
            return {
                "transport": "sse",
                "url": "http://localhost:8080/sse",
                "headers": {},
            }

        with open(config_path, "r") as f:
            return json.load(f)

    def _get_cache_path(self, app_name: str) -> Path:
        """Get cache path for tool definitions."""
        cache_dir = Path.home() / ".tasak" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{app_name}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is still valid."""
        if not cache_path.exists():
            return False

        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age < timedelta(seconds=CACHE_EXPIRATION_SECONDS)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions from server or cache using unified core."""
        import os

        debug = os.environ.get("TASAK_DEBUG") == "1"
        # Prefer existing file cache behavior
        if self._is_cache_valid(self.cache_path):
            print("Loading tool definitions from cache.", file=sys.stderr)
            if debug:
                print(
                    f"🔍 Debug: Cache hit for {self.app_name} at {self.cache_path}",
                    file=sys.stderr,
                )
            with open(self.cache_path, "r") as f:
                return json.load(f)

        if debug:
            print(
                "🔍 Debug: Cache miss or expired, fetching from server", file=sys.stderr
            )
        print(
            f"Fetching tool definitions for '{self.app_name}' from server...",
            file=sys.stderr,
        )
        tools = asyncio.run(self._svc.list_tools_async(self.app_name, self.app_config))
        if tools:
            with open(self.cache_path, "w") as f:
                json.dump(tools, f, indent=2)
            print(
                f"Successfully cached tool definitions to {self.cache_path}",
                file=sys.stderr,
            )
        return tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool using the unified core. Maintains legacy error behavior."""
        try:
            return asyncio.run(
                self._svc.call_tool_async(
                    self.app_name, self.app_config, tool_name, arguments
                )
            )
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(130)
        except Exception as e:
            error_msg = str(e)
            if "ConnectionRefused" in error_msg or "TaskGroup" in error_msg:
                print(
                    f"Error: Cannot connect to '{self.app_name}' server.",
                    file=sys.stderr,
                )
                print("Is the server running?", file=sys.stderr)
            else:
                print(f"Error executing tool '{tool_name}': {e}", file=sys.stderr)
            sys.exit(1)

    def _get_access_token(self) -> Optional[str]:
        """Get access token if authentication is required."""
        if not self.requires_auth:
            return None

        if not AUTH_FILE_PATH.exists():
            print(
                f"Error: Not authenticated for '{self.app_name}'. Please run 'tasak admin auth {self.app_name}' first.",
                file=sys.stderr,
            )
            sys.exit(1)

        with open(AUTH_FILE_PATH, "r") as f:
            all_tokens = json.load(f)

        token_data = all_tokens.get(self.app_name)
        if not token_data:
            print(
                f"Error: No authentication data found for '{self.app_name}'. Please run 'tasak admin auth {self.app_name}' first.",
                file=sys.stderr,
            )
            sys.exit(1)

        # For now, just return the access token
        # TODO: Add token refresh logic if needed
        return token_data.get("access_token")

    async def _fetch_tools_async(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Async function to fetch tools from MCP server."""
        transport = self.mcp_config.get("transport", "sse")

        try:
            if transport == "sse":
                # SSE transport (for GOK and remote servers)
                url = self.mcp_config.get("url", "http://localhost:8080/sse")

                async with sse_client(url, headers=headers) as (read, write):
                    async with ClientSession(read, write) as session:
                        # Initialize the session
                        await session.initialize()

                        # List available tools
                        response = await session.list_tools()

                        # Convert to our format
                        tools = []
                        for tool in response.tools:
                            tools.append(
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "input_schema": tool.inputSchema,
                                }
                            )

                        return tools

            elif transport == "stdio":
                # STDIO transport (for local servers)
                command = self.mcp_config.get("command", ["python", "server.py"])
                env = self.mcp_config.get("env", {})

                # Merge with current environment
                import os

                full_env = os.environ.copy()
                full_env.update(env)

                server_params = StdioServerParameters(
                    command=command[0],
                    args=command[1:] if len(command) > 1 else [],
                    env=full_env,
                )

                # Silence server stderr unless in debug/verbose mode
                import os as _os
                import sys as _sys

                _verbose = (_os.environ.get("TASAK_DEBUG") == "1") or (
                    _os.environ.get("TASAK_VERBOSE") == "1"
                )
                _err_sink = _sys.stderr if _verbose else open(_os.devnull, "w")
                async with stdio_client(server_params, errlog=_err_sink) as (
                    read,
                    write,
                ):
                    async with ClientSession(read, write) as session:
                        await session.initialize()

                        response = await session.list_tools()

                        tools = []
                        for tool in response.tools:
                            tools.append(
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "input_schema": tool.inputSchema,
                                }
                            )

                        return tools
            else:
                print(f"Unsupported transport: {transport}", file=sys.stderr)
                return []

        except (ConnectionError, TimeoutError, OSError):
            # Connection-specific errors - server likely not running
            print(
                f"Error: Cannot connect to '{self.app_name}' server.",
                file=sys.stderr,
            )
            print("Is the server running?", file=sys.stderr)
            return []
        except Exception as e:
            # Check if it's a TaskGroup error which usually means connection failed
            error_msg = str(e)
            if "TaskGroup" in error_msg or "ConnectionRefused" in error_msg.lower():
                print(
                    f"Error: Cannot connect to '{self.app_name}' server.",
                    file=sys.stderr,
                )
                print("Is the server running?", file=sys.stderr)
            else:
                # Other errors - log more details
                print(
                    f"Error fetching tools from '{self.app_name}': {e}",
                    file=sys.stderr,
                )
            return []

    async def _call_tool_async(
        self, tool_name: str, arguments: Dict[str, Any], headers: Dict[str, str]
    ) -> Any:
        """Async function to call a tool on the MCP server."""
        transport = self.mcp_config.get("transport", "sse")

        try:
            if transport == "sse":
                url = self.mcp_config.get("url", "http://localhost:8080/sse")

                async with sse_client(url, headers=headers) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()

                        # Call the tool
                        result = await session.call_tool(tool_name, arguments)

                        # Extract the result
                        if result.content and len(result.content) > 0:
                            content = result.content[0]
                            if hasattr(content, "text"):
                                return content.text
                            elif hasattr(content, "data"):
                                return content.data

                        return {
                            "status": "success",
                            "content": f"Tool {tool_name} executed",
                        }

            elif transport == "stdio":
                command = self.mcp_config.get("command", ["python", "server.py"])
                env = self.mcp_config.get("env", {})

                # Merge with current environment
                import os

                full_env = os.environ.copy()
                full_env.update(env)

                server_params = StdioServerParameters(
                    command=command[0],
                    args=command[1:] if len(command) > 1 else [],
                    env=full_env,
                )

                # Silence server stderr unless in debug/verbose mode
                import os as _os
                import sys as _sys

                _verbose = (_os.environ.get("TASAK_DEBUG") == "1") or (
                    _os.environ.get("TASAK_VERBOSE") == "1"
                )
                _err_sink = _sys.stderr if _verbose else open(_os.devnull, "w")
                async with stdio_client(server_params, errlog=_err_sink) as (
                    read,
                    write,
                ):
                    async with ClientSession(read, write) as session:
                        await session.initialize()

                        result = await session.call_tool(tool_name, arguments)

                        if result.content and len(result.content) > 0:
                            content = result.content[0]
                            if hasattr(content, "text"):
                                return content.text
                            elif hasattr(content, "data"):
                                return content.data

                        return {
                            "status": "success",
                            "content": f"Tool {tool_name} executed",
                        }
            else:
                return {"error": f"Unsupported transport: {transport}"}

        except (ConnectionError, TimeoutError, OSError):
            # Connection-specific errors - server likely not running
            print(
                f"Error: Cannot connect to '{self.app_name}' server.",
                file=sys.stderr,
            )
            print("Is the server running?", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            # Check if it's a TaskGroup error which usually means connection failed
            error_msg = str(e)
            if "TaskGroup" in error_msg or "ConnectionRefused" in error_msg.lower():
                print(
                    f"Error: Cannot connect to '{self.app_name}' server.",
                    file=sys.stderr,
                )
                print("Is the server running?", file=sys.stderr)
            else:
                # Other errors
                print(f"Error executing tool '{tool_name}': {e}", file=sys.stderr)
            sys.exit(1)

    def clear_cache(self):
        """Clear the cache for this app."""
        if self.cache_path.exists():
            self.cache_path.unlink()
            print(f"Cache for '{self.app_name}' cleared.", file=sys.stderr)
        else:
            print(f"No cache found for '{self.app_name}'.", file=sys.stderr)
