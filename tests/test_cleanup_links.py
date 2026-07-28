"""Tests for interactive cleanup link deletion behavior."""
from __future__ import annotations

from bookmark_organizer.cleanup import prompt_keep_choice
from bookmark_organizer.models import BookmarkNode, DuplicateLinkGroup, FolderNode

__all__ = [
    "test_prompt_keep_choice_delete_all",
    "test_prompt_keep_choice_delete_specific",
    "test_prompt_keep_choice_keep_first",
]


def test_prompt_keep_choice_keep_first(monkeypatch) -> None:
    group = DuplicateLinkGroup(
        normalized_url="https://example.com",
        items=[
            BookmarkNode(name="A", url="https://example.com", parent=FolderNode(name="Root")),
            BookmarkNode(name="B", url="https://example.com", parent=FolderNode(name="Root")),
        ],
    )
    monkeypatch.setattr("bookmark_organizer.cleanup.Prompt.ask", lambda *args, **kwargs: "k")
    action, value = prompt_keep_choice(group)
    assert action == "keep"
    assert value == 1


def test_prompt_keep_choice_delete_specific(monkeypatch) -> None:
    group = DuplicateLinkGroup(
        normalized_url="https://example.com",
        items=[
            BookmarkNode(name="A", url="https://example.com", parent=FolderNode(name="Root")),
            BookmarkNode(name="B", url="https://example.com", parent=FolderNode(name="Root")),
        ],
    )
    responses = iter(["d", "2"])
    monkeypatch.setattr("bookmark_organizer.cleanup.Prompt.ask", lambda *args, **kwargs: next(responses))
    action, value = prompt_keep_choice(group)
    assert action == "delete"
    assert value == 2


def test_prompt_keep_choice_delete_all(monkeypatch) -> None:
    group = DuplicateLinkGroup(
        normalized_url="https://example.com",
        items=[
            BookmarkNode(name="A", url="https://example.com", parent=FolderNode(name="Root")),
            BookmarkNode(name="B", url="https://example.com", parent=FolderNode(name="Root")),
        ],
    )
    monkeypatch.setattr("bookmark_organizer.cleanup.Prompt.ask", lambda *args, **kwargs: "a")
    action, value = prompt_keep_choice(group)
    assert action == "all"
    assert value is None
