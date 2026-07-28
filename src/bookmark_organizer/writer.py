"""Bookmark file writer and tree manipulation utilities."""
from __future__ import annotations

import json
from pathlib import Path

from .models import BookmarkNode, FolderNode

__all__ = [
    "collect_empty_folders",
    "remove_bookmark",
    "remove_folder",
    "write_bookmarks",
]


def write_bookmarks(data: dict, path: Path) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")


def remove_bookmark(node: BookmarkNode) -> None:
    parent = node.parent
    if parent is not None:
        parent.children = [c for c in parent.children if c is not node]


def remove_folder(node: FolderNode) -> None:
    parent = node.parent
    if parent is not None:
        parent.children = [c for c in parent.children if c is not node]


def collect_empty_folders(node: FolderNode) -> list[FolderNode]:
    empty: list[FolderNode] = []
    stack = list(node.children)
    while stack:
        child = stack.pop(0)
        if isinstance(child, FolderNode):
            if not child.children:
                empty.append(child)
            else:
                stack.extend(child.children)
    return empty
