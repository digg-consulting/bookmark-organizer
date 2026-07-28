"""Duplicate detection: group bookmarks and folders by normalized keys."""
from __future__ import annotations

from collections import defaultdict

from .models import BookmarkNode, DuplicateFolderGroup, DuplicateLinkGroup, FolderNode
from .normalizer import normalize_url

__all__ = ["group_by_normalized_url", "group_duplicate_folders"]


def group_by_normalized_url(bookmarks: list[BookmarkNode]) -> list[DuplicateLinkGroup]:
    groups: dict[str, list[BookmarkNode]] = defaultdict(list)
    for bm in bookmarks:
        key = normalize_url(bm.url)
        groups[key].append(bm)
    return [
        DuplicateLinkGroup(normalized_url=key, items=items)
        for key, items in groups.items()
        if len(items) > 1
    ]


def group_duplicate_folders(folders: list[FolderNode]) -> list[DuplicateFolderGroup]:
    groups: dict[tuple[str, str], list[FolderNode]] = defaultdict(list)
    for folder in folders:
        key = (folder.path, folder.name.lower())
        groups[key].append(folder)
    return [
        DuplicateFolderGroup(name=name, parent_path=parent_path, items=items)
        for (parent_path, name), items in groups.items()
        if len(items) > 1
    ]
