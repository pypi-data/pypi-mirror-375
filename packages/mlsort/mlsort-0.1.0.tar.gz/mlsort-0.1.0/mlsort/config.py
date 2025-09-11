from __future__ import annotations

import os
import sys
from typing import Optional


def get_cache_root() -> str:
    # macOS: ~/Library/Caches
    # Linux: XDG_CACHE_HOME or ~/.cache
    # Windows: LOCALAPPDATA
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches")
    if os.name == "nt":
        return os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    return os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))


def get_artifacts_dir() -> str:
    return os.environ.get("MLSORT_ARTIFACTS_DIR", os.path.join(get_cache_root(), "mlsort"))


def get_env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


def get_seed(default: int = 42) -> int:
    try:
        return int(os.environ.get("MLSORT_SEED", str(default)))
    except Exception:
        return default

