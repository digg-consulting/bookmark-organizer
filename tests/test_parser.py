"""Tests for the bookmark parser module."""
from __future__ import annotations

import json
from pathlib import Path

from bookmark_organizer.parser import load_bookmarks


def test_load_bookmarks_simple(tmp_path: Path) -> None:
    sample = {
        "roots": {
            "bookmark_bar": {
                "children": [
                    {"type": "url", "name": "A", "url": "https://a.com"},
                    {"type": "url", "name": "B", "url": "https://b.com"},
                ]
            },
            "other": {"children": []},
            "synced": {"children": []},
        },
        "version": 1,
    }
    p = tmp_path / "bookmarks.json"
    p.write_text(json.dumps(sample), encoding="utf-8")
    data = load_bookmarks(p)
    assert data["version"] == 1
    assert len(data["roots"]["bookmark_bar"]["children"]) == 2
