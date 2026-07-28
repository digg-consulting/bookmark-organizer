"""Tests for the clean command backup behavior."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from bookmark_organizer.cli import app

__all__ = ["test_clean_command_creates_backup"]


def test_clean_command_creates_backup(tmp_path: Path) -> None:
    """When --backup is provided, a Bookmarks.bak should be created."""
    sample = {
        "roots": {
            "bookmark_bar": {
                "type": "folder",
                "name": "Bookmarks bar",
                "children": [
                    {"type": "url", "name": "A", "url": "https://example.com", "date_added": "1"},
                    {"type": "url", "name": "B", "url": "https://example.com", "date_added": "2"},
                ],
            },
            "other": {"type": "folder", "name": "Other bookmarks", "children": []},
            "synced": {"type": "folder", "name": "Synced", "children": []},
        },
        "version": 1,
    }
    input_file = tmp_path / "bookmarks.json"
    input_file.write_text(json.dumps(sample), encoding="utf-8")
    backup_file = tmp_path / "Bookmarks.bak"

    runner = CliRunner()
    with patch("bookmark_organizer.cli.Confirm.ask", return_value=True):
        result = runner.invoke(app, ["clean", "--browser", "chrome", "--auto", "--backup", str(input_file)])
    assert result.exit_code == 0, result.output

    assert backup_file.exists(), "Backup file was not created"
    backup_data = json.loads(backup_file.read_text(encoding="utf-8"))
    assert len(backup_data["roots"]["bookmark_bar"]["children"]) == 2

    cleaned = json.loads(input_file.read_text(encoding="utf-8"))
    assert len(cleaned["roots"]["bookmark_bar"]["children"]) == 1
