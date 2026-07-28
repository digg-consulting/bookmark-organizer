"""Tests for writer utilities."""
from __future__ import annotations

from bookmark_organizer.models import BookmarkNode, FolderNode
from bookmark_organizer.writer import move_children

__all__ = ["test_move_children"]


def test_move_children() -> None:
    source = FolderNode(name="Source")
    dest = FolderNode(name="Destination")
    bm = BookmarkNode(name="Link", url="https://example.com", parent=source)
    sub = FolderNode(name="Sub", parent=source)
    source.children = [bm, sub]

    move_children(source, dest)

    assert source.children == []
    assert len(dest.children) == 2
    assert bm.parent is dest
    assert sub.parent is dest
    assert dest.children == [bm, sub]
