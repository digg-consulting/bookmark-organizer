"""Tests for browser auto-detection."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from bookmark_organizer.models import auto_detect_browser

__all__ = [
    "test_auto_detect_brave",
    "test_auto_detect_chrome",
    "test_auto_detect_chromium",
    "test_auto_detect_none",
]


def test_auto_detect_brave(tmp_path: Path) -> None:
    with patch("bookmark_organizer.models.Path.home", return_value=tmp_path):
        (tmp_path / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser" / "Default").mkdir(parents=True)
        (tmp_path / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser" / "Default" / "Bookmarks").write_text("{}", encoding="utf-8")
        assert auto_detect_browser() == "brave"


def test_auto_detect_chrome(tmp_path: Path) -> None:
    with patch("bookmark_organizer.models.Path.home", return_value=tmp_path):
        (tmp_path / "Library" / "Application Support" / "Google" / "Chrome" / "Default").mkdir(parents=True)
        (tmp_path / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "Bookmarks").write_text("{}", encoding="utf-8")
        assert auto_detect_browser() == "chrome"


def test_auto_detect_chromium(tmp_path: Path) -> None:
    with patch("bookmark_organizer.models.Path.home", return_value=tmp_path):
        (tmp_path / ".config" / "chromium" / "Default").mkdir(parents=True)
        (tmp_path / ".config" / "chromium" / "Default" / "Bookmarks").write_text("{}", encoding="utf-8")
        assert auto_detect_browser() == "chromium"


def test_auto_detect_none(tmp_path: Path) -> None:
    with patch("bookmark_organizer.models.Path.home", return_value=tmp_path):
        assert auto_detect_browser() is None
