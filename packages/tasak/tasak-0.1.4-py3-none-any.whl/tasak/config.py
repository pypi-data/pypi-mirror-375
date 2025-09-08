import os
from pathlib import Path
import yaml


def get_config_filename() -> str:
    """Returns the config filename to use (can be customized via environment)."""
    return os.environ.get("TASAK_CONFIG_NAME", "tasak.yaml")


def get_global_config_path() -> Path | None:
    """Returns the path to the global config file, if it exists."""
    home_dir = Path.home()
    config_name = get_config_filename()
    config_path = home_dir / ".tasak" / config_name
    return config_path if config_path.exists() else None


def find_local_config_paths() -> list[Path]:
    """Finds all local config files by traversing up the directory tree."""
    search_paths = []
    current_dir = Path.cwd()
    config_name = get_config_filename()

    while True:
        # Support both direct file and in .tasak directory
        direct_config = current_dir / config_name
        dot_tasak_config = current_dir / ".tasak" / config_name

        if dot_tasak_config.exists():
            search_paths.append(dot_tasak_config)

        if direct_config.exists():
            search_paths.append(direct_config)

        if current_dir.parent == current_dir:  # Reached the root
            break

        current_dir = current_dir.parent

    return list(reversed(search_paths))  # Return in order from root to cwd


def load_and_merge_configs() -> dict:
    """
    Loads all configs and merges them.
    The loading priority is as follows:
    1. If TASAK_CONFIG environment variable is set, load only that file.
    2. Otherwise, load global config (~/.tasak/tasak.yaml).
    3. Then, load local configs (tasak.yaml or .tasak/tasak.yaml) from the
       current directory up to the root, merging them in order.
    """
    # 1. Check for TASAK_CONFIG environment variable
    if config_path_str := os.environ.get("TASAK_CONFIG"):
        config_path = Path(config_path_str)
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        # If the env var points to a non-existent file, fall back to standard search
        # instead of returning an empty config (more resilient in CI environments).

    # If no env var, proceed with the original logic
    merged_config = {}

    # 2. Load global config (may be ignored later if isolation applies)
    global_config_path = get_global_config_path()
    global_config = None
    if global_config_path:
        with open(global_config_path, "r") as f:
            global_config = yaml.safe_load(f)

    # 3. Discover local configs and apply isolation semantics
    local_config_paths = find_local_config_paths()  # ordered from root -> cwd

    # Detect nearest isolation flag scanning from cwd backwards
    isolate_index: int | None = None
    for idx in range(len(local_config_paths) - 1, -1, -1):
        p = local_config_paths[idx]
        with open(p, "r") as f:
            data = yaml.safe_load(f) or {}
        apps_cfg = data.get("apps_config", {}) or {}
        if bool(apps_cfg.get("isolate", False)):
            isolate_index = idx
            break

    # Merge respecting isolation
    if isolate_index is None:
        # No isolation: include global then local (root -> cwd)
        if global_config:
            merged_config.update(global_config)
        for path in local_config_paths:
            with open(path, "r") as f:
                local_config = yaml.safe_load(f)
                if local_config:
                    merged_config.update(local_config)
    else:
        # Isolation found at local_config_paths[isolate_index]: ignore global and any parents above
        for path in local_config_paths[isolate_index:]:
            with open(path, "r") as f:
                local_config = yaml.safe_load(f)
                if local_config:
                    merged_config.update(local_config)

    return merged_config
