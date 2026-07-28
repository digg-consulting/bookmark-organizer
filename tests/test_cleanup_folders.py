"""Tests for interactive cleanup folder merge behavior."""
from __future__ import annotations

from bookmark_organizer.cleanup import interactive_cleanup_folders, prompt_keep_folder
from bookmark_organizer.models import BookmarkNode, DuplicateFolderGroup, FolderNode

__all__ = [
    "test_interactive_cleanup_folders_delete_with_children_delete",
    "test_interactive_cleanup_folders_delete_with_children_move",
    "test_interactive_cleanup_folders_merge",
    "test_prompt_keep_folder_keep_first",
    "test_prompt_keep_folder_merge",
]


def test_prompt_keep_folder_keep_first(monkeypatch) -> None:
    group = DuplicateFolderGroup(
        name="News",
        items=[
            FolderNode(name="News", parent=FolderNode(name="Root1")),
            FolderNode(name="News", parent=FolderNode(name="Root2")),
        ],
    )
    monkeypatch.setattr("bookmark_organizer.cleanup.Prompt.ask", lambda *args, **kwargs: "k")
    action, value = prompt_keep_folder(group)
    assert action == "keep"
    assert value == 1


def test_prompt_keep_folder_merge(monkeypatch) -> None:
    f1 = FolderNode(name="News", parent=FolderNode(name="Root1"))
    f2 = FolderNode(name="News", parent=FolderNode(name="Root2"))
    bm = BookmarkNode(name="Link", url="https://example.com", parent=f2)
    f2.children = [bm]
    group = DuplicateFolderGroup(
        name="News",
        items=[f1, f2],
    )
    responses = iter(["m", "1"])
    monkeypatch.setattr("bookmark_organizer.cleanup.Prompt.ask", lambda *args, **kwargs: next(responses))
    action, value = prompt_keep_folder(group)
    assert action == "merge"
    assert value == 1


def test_interactive_cleanup_folders_merge(monkeypatch) -> None:
    root1 = FolderNode(name="Root1")
    root2 = FolderNode(name="Root2")
    f1 = FolderNode(name="News", parent=root1)
    f2 = FolderNode(name="News", parent=root2)
    bm = BookmarkNode(name="Link", url="https://example.com", parent=f2)
    f2.children = [bm]
    root1.children = [f1]
    root2.children = [f2]

    group = DuplicateFolderGroup(
        name="News",
        items=[f1, f2],
    )
    responses = iter(["m", "1"])
    monkeypatch.setattr("bookmark_organizer.cleanup.Prompt.ask", lambda *args, **kwargs: next(responses))
    kept, deleted = interactive_cleanup_folders([group])

    assert len(kept) == 1
    assert kept[0] is f1
    assert len(deleted) == 1
    assert deleted[0] is f2
    assert f1.children == [bm]
    assert bm.parent is f1
    assert f2.children == []


def test_interactive_cleanup_folders_delete_with_children_delete(monkeypatch) -> None:
    root1 = FolderNode(name="Root1")
    root2 = FolderNode(name="Root2")
    f1 = FolderNode(name="News", parent=root1)
    f2 = FolderNode(name="News", parent=root2)
    bm = BookmarkNode(name="Link", url="https://example.com", parent=f2)
    f2.children = [bm]
    root1.children = [f1]
    root2.children = [f2]

    group = DuplicateFolderGroup(
        name="News",
        items=[f1, f2],
    )
    responses = iter(["d", "2", "d"])
    monkeypatch.setattr("bookmark_organizer.cleanup.Prompt.ask", lambda *args, **kwargs: next(responses))
    kept, deleted = interactive_cleanup_folders([group])

    assert len(kept) == 1
    assert kept[0] is f2
    assert len(deleted) == 1
    assert deleted[0] is f1
    assert f1.children == []
    assert f2.children == [bm]


def test_interactive_cleanup_folders_delete_with_children_move(monkeypatch) -> None:
    root1 = FolderNode(name="Root1")
    root2 = FolderNode(name="Root2")
    f1 = FolderNode(name="News", parent=root1)
    f2 = FolderNode(name="News", parent=root2)
    bm = BookmarkNode(name="Link", url="https://example.com", parent=f2)
    f2.children = [bm]
    root1.children = [f1]
    root2.children = [f2]

    group = DuplicateFolderGroup(
        name="News",
        items=[f1, f2],
    )
    responses = iter(["d", "2", "m"])
    monkeypatch.setattr("bookmark_organizer.cleanup.Prompt.ask", lambda *args, **kwargs: next(responses))
    kept, deleted = interactive_cleanup_folders([group])

    assert len(kept) == 1
    assert kept[0] is f2
    assert len(deleted) == 1
    assert deleted[0] is f1
    assert f1.children == []
    assert f2.children == [bm]
