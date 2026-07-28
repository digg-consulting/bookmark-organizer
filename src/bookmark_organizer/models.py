"""Data models for bookmark-organizer."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .xdg import app_data_dir

__all__ = [
    "BookmarkNode",
    "DuplicateFolderGroup",
    "DuplicateLinkGroup",
    "FolderNode",
    "auto_detect_browser",
    "get_default_bookmarks_path",
]


@dataclass
class BookmarkNode:
    name: str
    url: str
    date_added: str | None = None
    parent: FolderNode | None = None

    @property
    def path(self) -> str:
        parts: list[str] = []
        p = self.parent
        while p is not None:
            parts.append(p.name)
            p = p.parent
        parts.reverse()
        return "/".join(parts) if parts else "(root)"

    def to_dict(self) -> dict:
        return {
            "type": "url",
            "name": self.name,
            "url": self.url,
            "date_added": self.date_added,
        }


@dataclass
class FolderNode:
    name: str
    children: list[BookmarkNode | FolderNode] = field(default_factory=list)
    date_added: str | None = None
    parent: FolderNode | None = None

    @property
    def path(self) -> str:
        parts: list[str] = []
        p = self.parent
        while p is not None:
            parts.append(p.name)
            p = p.parent
        parts.reverse()
        return "/".join(parts) if parts else "(root)"

    def to_dict(self) -> dict:
        return {
            "type": "folder",
            "name": self.name,
            "children": [c.to_dict() for c in self.children],
            "date_added": self.date_added,
        }


@dataclass
class DuplicateLinkGroup:
    normalized_url: str
    items: list[BookmarkNode] = field(default_factory=list)


@dataclass
class DuplicateFolderGroup:
    name: str
    items: list[FolderNode] = field(default_factory=list)


def get_default_bookmarks_path(browser: str = "brave") -> Path:
    if browser.lower() == "auto":
        browser = auto_detect_browser() or "brave"
    if os.name == "posix":
        candidates = []
        if browser.lower() == "brave":
            candidates = [
                Path.home() / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser" / "Default" / "Bookmarks",
                Path.home() / ".config" / "BraveSoftware" / "Brave-Browser" / "Default" / "Bookmarks",
            ]
        elif browser.lower() == "chrome":
            candidates = [
                Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "Bookmarks",
                Path.home() / ".config" / "google-chrome" / "Default" / "Bookmarks",
                Path.home() / ".config" / "chromium" / "Default" / "Bookmarks",
            ]
        for c in candidates:
            if c.exists():
                return c
    return app_data_dir() / "default_bookmarks.json"


def auto_detect_browser() -> str | None:
    """Return 'brave', 'chrome', or 'chromium' if a Bookmarks file is found."""
    checks = [
        ("brave", Path.home() / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser" / "Default" / "Bookmarks"),
        ("brave", Path.home() / ".config" / "BraveSoftware" / "Brave-Browser" / "Default" / "Bookmarks"),
        ("chrome", Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "Bookmarks"),
        ("chrome", Path.home() / ".config" / "google-chrome" / "Default" / "Bookmarks"),
        ("chromium", Path.home() / ".config" / "chromium" / "Default" / "Bookmarks"),
    ]
    for browser, path in checks:
        if path.exists():
            return browser
    return None
