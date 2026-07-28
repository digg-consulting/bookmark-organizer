"""Bookmark parser: load JSON, build tree, find duplicates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from .models import BookmarkNode, DuplicateFolderGroup, DuplicateLinkGroup, FolderNode

__all__ = [
    "build_trees",
    "collect_bookmarks",
    "collect_folders",
    "find_duplicate_folders",
    "find_duplicate_links",
    "load_bookmarks",
]


def load_bookmarks(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    return cast(dict[str, Any], json.loads(text))


def _get_root(data: dict[str, Any], key: str) -> dict[str, Any] | None:
    root = data.get("roots", {}).get(key)
    if not root:
        return None
    return cast(dict[str, Any], root)


def _build_tree(node: dict, parent: FolderNode | None = None) -> FolderNode | BookmarkNode | None:
    node_type = node.get("type")
    if node_type == "folder":
        folder = FolderNode(
            name=node.get("name", ""),
            date_added=node.get("date_added"),
            parent=parent,
        )
        for child in node.get("children", []):
            built = _build_tree(child, parent=folder)
            if built is not None:
                folder.children.append(built)
        return folder
    if node_type == "url":
        return BookmarkNode(
            name=node.get("name", ""),
            url=node.get("url", ""),
            date_added=node.get("date_added"),
            parent=parent,
        )
    return None


def build_trees(data: dict[str, Any]) -> list[tuple[str, FolderNode]]:
    """Build in-memory folder trees for all bookmark roots."""
    root_folders: list[tuple[str, FolderNode]] = []
    for root_key in ("bookmark_bar", "other", "synced"):
        root = _get_root(data, root_key)
        if root:
            root_folder = _build_tree(root, parent=None)
            if isinstance(root_folder, FolderNode):
                root_folders.append((root_key, root_folder))
    return root_folders


def collect_bookmarks(root_folders: list[tuple[str, FolderNode]]) -> list[BookmarkNode]:
    """Collect all bookmark nodes from the given root trees."""
    bookmarks: list[BookmarkNode] = []
    for _, root_folder in root_folders:
        _collect_bookmarks(root_folder, bookmarks)
    return bookmarks


def collect_folders(root_folders: list[tuple[str, FolderNode]]) -> list[FolderNode]:
    """Collect all folder nodes from the given root trees."""
    folders: list[FolderNode] = []
    for _, root_folder in root_folders:
        _collect_folders(root_folder, folders)
    return folders


def _collect_bookmarks(node: FolderNode, out: list[BookmarkNode]) -> None:
    stack = [node]
    while stack:
        current = stack.pop(0)
        for child in current.children:
            if isinstance(child, BookmarkNode):
                out.append(child)
            elif isinstance(child, FolderNode):
                stack.append(child)


def _collect_folders(node: FolderNode, out: list[FolderNode]) -> None:
    stack = [node]
    while stack:
        current = stack.pop(0)
        for child in current.children:
            if isinstance(child, FolderNode):
                out.append(child)
                stack.append(child)


def iter_bookmarks(data: dict) -> list[BookmarkNode]:
    bookmarks: list[BookmarkNode] = []
    for root_key in ("bookmark_bar", "other", "synced"):
        root = _get_root(data, root_key)
        if not root:
            continue
        root_folder = _build_tree(root, parent=None)
        if isinstance(root_folder, FolderNode):
            _collect_bookmarks(root_folder, bookmarks)
    return bookmarks


def iter_folders(data: dict) -> list[FolderNode]:
    folders: list[FolderNode] = []
    for root_key in ("bookmark_bar", "other", "synced"):
        root = _get_root(data, root_key)
        if not root:
            continue
        root_folder = _build_tree(root, parent=None)
        if isinstance(root_folder, FolderNode):
            _collect_folders(root_folder, folders)
    return folders


def find_duplicate_links(data: dict) -> list[DuplicateLinkGroup]:
    from .dedup import group_by_normalized_url
    bookmarks = iter_bookmarks(data)
    return group_by_normalized_url(bookmarks)


def find_duplicate_folders(data: dict) -> list[DuplicateFolderGroup]:
    from .dedup import group_duplicate_folders
    folders = iter_folders(data)
    return group_duplicate_folders(folders)
