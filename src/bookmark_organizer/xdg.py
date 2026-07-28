"""XDG Base Directory paths for bookmark-organizer (digg namespace)."""

from __future__ import annotations

import os
from pathlib import Path


def _home() -> Path:
    return Path.home()


def xdg_config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", _home() / ".config")).expanduser()


def xdg_cache_home() -> Path:
    return Path(os.environ.get("XDG_CACHE_HOME", _home() / ".cache")).expanduser()


def xdg_data_home() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME", _home() / ".local" / "share")).expanduser()


def app_config_dir() -> Path:
    return xdg_config_home() / "digg" / "bookmark-organizer"


def app_cache_dir() -> Path:
    return xdg_cache_home() / "digg" / "bookmark-organizer"


def app_data_dir() -> Path:
    return xdg_data_home() / "digg" / "bookmark-organizer"


def app_bin_dir() -> Path:
    return _home() / ".local" / "bin"


def ensure_xdg_dirs() -> None:
    for path in (
        app_config_dir(),
        app_cache_dir(),
        app_data_dir(),
        app_bin_dir(),
    ):
        path.mkdir(parents=True, exist_ok=True)


__all__ = [
    "app_bin_dir",
    "app_cache_dir",
    "app_config_dir",
    "app_data_dir",
    "ensure_xdg_dirs",
    "xdg_cache_home",
    "xdg_config_home",
    "xdg_data_home",
]
