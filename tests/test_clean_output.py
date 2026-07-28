"""Tests for the clean command output behavior."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from bookmark_organizer.cli import app

__all__ = ["test_clean_command_writes_to_output_flag"]


def test_clean_command_writes_to_output_flag(tmp_path: Path) -> None:
    """When --output is provided, cleaned bookmarks should be written to that file."""
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
    output_file = tmp_path / "cleaned.json"

    runner = CliRunner()
    with patch("bookmark_organizer.cli.Confirm.ask", return_value=True):
        result = runner.invoke(app, ["clean", "--browser", "chrome", "--auto", "--output", str(output_file), str(input_file)])
    assert result.exit_code == 0, result.output

    assert output_file.exists(), "Output file was not created"
    cleaned = json.loads(output_file.read_text(encoding="utf-8"))
    bar_children = cleaned["roots"]["bookmark_bar"]["children"]
    assert len(bar_children) == 1
    assert bar_children[0]["name"] == "A"

    original = json.loads(input_file.read_text(encoding="utf-8"))
    assert len(original["roots"]["bookmark_bar"]["children"]) == 2
