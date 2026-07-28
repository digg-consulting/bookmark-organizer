"""Tests for the duplicate detection module."""
from __future__ import annotations

from bookmark_organizer.dedup import group_by_normalized_url, group_duplicate_folders
from bookmark_organizer.models import (
    BookmarkNode,
    DuplicateFolderGroup,
    DuplicateLinkGroup,
    FolderNode,
)


def test_group_by_normalized_url_detects_duplicates():
    b1 = BookmarkNode(name="A", url="https://example.com/a", parent=None)
    b2 = BookmarkNode(name="B", url="https://example.com/a", parent=None)
    b3 = BookmarkNode(name="C", url="https://example.com/b", parent=None)
    groups: list[DuplicateLinkGroup] = group_by_normalized_url([b1, b2, b3])
    assert len(groups) == 1
    assert groups[0].normalized_url == "https://example.com/a"
    assert len(groups[0].items) == 2


def test_group_by_normalized_url_no_duplicates():
    bookmarks = [
        BookmarkNode(name="A", url="https://example.com/a", parent=None),
        BookmarkNode(name="B", url="https://example.com/b", parent=None),
    ]
    groups: list[DuplicateLinkGroup] = group_by_normalized_url(bookmarks)
    assert len(groups) == 0


def test_group_duplicate_folders_detects_duplicates():
    root = FolderNode(name="Root")
    f1 = FolderNode(name="News", parent=root)
    f2 = FolderNode(name="News", parent=root)
    root.children = [f1, f2]
    groups: list[DuplicateFolderGroup] = group_duplicate_folders([f1, f2])
    assert len(groups) == 1
    assert groups[0].name == "news"
    assert len(groups[0].items) == 2


def test_group_duplicate_folders_detects_cross_parent_duplicates():
    root1 = FolderNode(name="Bookmarks bar")
    root2 = FolderNode(name="Other bookmarks")
    f1 = FolderNode(name="AI", parent=root1)
    f2 = FolderNode(name="AI", parent=root2)
    groups: list[DuplicateFolderGroup] = group_duplicate_folders([f1, f2])
    assert len(groups) == 1
    assert groups[0].name == "ai"
    assert len(groups[0].items) == 2
    paths = {item.path for item in groups[0].items}
    assert "Bookmarks bar" in paths
    assert "Other bookmarks" in paths


def test_group_duplicate_folders_no_duplicates():
    root = FolderNode(name="Root")
    f1 = FolderNode(name="News", parent=root)
    f2 = FolderNode(name="Tech", parent=root)
    root.children = [f1, f2]
    groups: list[DuplicateFolderGroup] = group_duplicate_folders([f1, f2])
    assert len(groups) == 0
