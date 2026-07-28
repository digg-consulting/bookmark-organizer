"""Interactive and automatic cleanup logic for duplicate bookmarks."""
from __future__ import annotations

from typing import Literal

from rich.console import Console
from rich.prompt import Prompt

from .models import BookmarkNode, DuplicateFolderGroup, DuplicateLinkGroup, FolderNode
from .writer import collect_empty_folders, move_children, remove_bookmark, remove_folder

__all__ = [
    "auto_cleanup_folders",
    "auto_cleanup_links",
    "interactive_cleanup_folders",
    "interactive_cleanup_links",
    "prompt_keep_choice",
    "prompt_keep_folder",
    "remove_empty_folders",
]


console = Console()
_Action = Literal["keep", "delete", "all", "quit", "merge"]


def prompt_keep_choice(group: DuplicateLinkGroup) -> tuple[_Action, int | None]:
    console.print(f"\n[bold cyan]Link group:[/bold cyan] {group.normalized_url}")
    for idx, item in enumerate(group.items, 1):
        console.print(f"  {idx}. {item.name} — {item.path}")
    console.print("  [bold]Actions:[/bold] [K]eep first  [S]elect keep  [D]elete  [A]ll  [Q]uit")
    choice = Prompt.ask("Choose action", choices=["k", "s", "d", "a", "q"], default="k").lower()
    if choice == "k":
        return "keep", 1
    if choice == "a":
        return "all", None
    if choice == "d":
        console.print("Delete which (enter number):")
        for idx, item in enumerate(group.items, 1):
            console.print(f"  {idx}. {item.name} — {item.path}")
        sel = Prompt.ask("Delete #", choices=[str(i) for i in range(1, len(group.items) + 1)])
        return "delete", int(sel)
    if choice == "s":
        console.print("Select which to keep (enter number):")
        for idx, item in enumerate(group.items, 1):
            console.print(f"  {idx}. {item.name} — {item.path}")
        sel = Prompt.ask("Keep #", choices=[str(i) for i in range(1, len(group.items) + 1)])
        return "keep", int(sel)
    return "quit", None


def interactive_cleanup_links(
    groups: list[DuplicateLinkGroup],
) -> tuple[list[BookmarkNode], list[BookmarkNode]]:
    kept: list[BookmarkNode] = []
    deleted: list[BookmarkNode] = []
    for group in groups:
        action, value = prompt_keep_choice(group)
        if action == "quit":
            console.print("[yellow]Skipped remaining groups.[/yellow]")
            break
        if action == "all":
            for item in group.items:
                remove_bookmark(item)
                deleted.append(item)
            continue
        if action == "keep":
            for idx, item in enumerate(group.items, 1):
                if idx == value:
                    kept.append(item)
                else:
                    remove_bookmark(item)
                    deleted.append(item)
        elif action == "delete":
            for idx, item in enumerate(group.items, 1):
                if idx == value:
                    remove_bookmark(item)
                    deleted.append(item)
                else:
                    kept.append(item)
    return kept, deleted


def _prompt_delete_folder_with_children(folder_to_delete: FolderNode, kept_folder: FolderNode) -> None:
    """Prompt user about bookmarks in a folder being deleted."""
    child_count = sum(1 for _ in _iter_bookmark_nodes(folder_to_delete))
    if child_count == 0:
        return
    console.print(f"[yellow]Warning: '{folder_to_delete.name}' contains {child_count} bookmark(s).[/yellow]")
    console.print("  [bold]What should happen to these bookmarks?[/bold]")
    console.print("  [D]elete them with the folder")
    console.print("  [M]ove them into the kept folder")
    choice = Prompt.ask("Choose action", choices=["d", "m"], default="d").lower()
    if choice == "m":
        move_children(folder_to_delete, kept_folder)


def _iter_bookmark_nodes(node: FolderNode):
    """Iterate all bookmark nodes under a folder."""
    stack = list(node.children)
    while stack:
        child = stack.pop(0)
        if isinstance(child, BookmarkNode):
            yield child
        elif isinstance(child, FolderNode):
            stack.extend(child.children)


def prompt_keep_folder(group: DuplicateFolderGroup) -> tuple[_Action, int | None]:
    console.print(f"\n[bold cyan]Folder group:[/bold cyan] '{group.name}'")
    for idx, item in enumerate(group.items, 1):
        console.print(f"  {idx}. {item.name} — {item.path}")
    console.print("  [bold]Actions:[/bold] [K]eep first  [S]elect keep  [D]elete  [M]erge  [Q]uit")
    choice = Prompt.ask("Choose action", choices=["k", "s", "d", "m", "q"], default="k").lower()
    if choice == "k":
        return "keep", 1
    if choice == "m":
        console.print("Select which folder to keep (contents from others will be merged into this one):")
        for idx, item in enumerate(group.items, 1):
            console.print(f"  {idx}. {item.name} — {item.path}")
        sel = Prompt.ask("Keep #", choices=[str(i) for i in range(1, len(group.items) + 1)])
        return "merge", int(sel)
    if choice == "a":
        return "all", None
    if choice == "d":
        console.print("Delete which (enter number):")
        for idx, item in enumerate(group.items, 1):
            console.print(f"  {idx}. {item.name} — {item.path}")
        sel = Prompt.ask("Delete #", choices=[str(i) for i in range(1, len(group.items) + 1)])
        return "delete", int(sel)
    if choice == "s":
        console.print("Select which to keep (enter number):")
        for idx, item in enumerate(group.items, 1):
            console.print(f"  {idx}. {item.name} — {item.path}")
        sel = Prompt.ask("Keep #", choices=[str(i) for i in range(1, len(group.items) + 1)])
        return "keep", int(sel)
    return "quit", None


def interactive_cleanup_folders(
    groups: list[DuplicateFolderGroup],
) -> tuple[list[FolderNode], list[FolderNode]]:
    kept: list[FolderNode] = []
    deleted: list[FolderNode] = []
    for group in groups:
        action, value = prompt_keep_folder(group)
        if action == "quit":
            console.print("[yellow]Skipped remaining groups.[/yellow]")
            break
        if action == "all":
            for item in group.items:
                remove_folder(item)
                deleted.append(item)
            continue
        if action == "merge":
            assert value is not None
            for idx, item in enumerate(group.items, 1):
                if idx == value:
                    kept.append(item)
                else:
                    move_children(item, group.items[value - 1])
                    remove_folder(item)
                    deleted.append(item)
            continue
        if action in ("keep", "delete"):
            assert value is not None
            for idx, item in enumerate(group.items, 1):
                if idx == value:
                    kept.append(item)
                else:
                    _prompt_delete_folder_with_children(item, group.items[value - 1])
                    remove_folder(item)
                    deleted.append(item)
    return kept, deleted


def auto_cleanup_links(groups: list[DuplicateLinkGroup]) -> tuple[list[BookmarkNode], list[BookmarkNode]]:
    kept: list[BookmarkNode] = []
    deleted: list[BookmarkNode] = []
    for group in groups:
        for idx, item in enumerate(group.items, 1):
            if idx == 1:
                kept.append(item)
            else:
                remove_bookmark(item)
                deleted.append(item)
    return kept, deleted


def auto_cleanup_folders(groups: list[DuplicateFolderGroup]) -> tuple[list[FolderNode], list[FolderNode]]:
    kept: list[FolderNode] = []
    deleted: list[FolderNode] = []
    for group in groups:
        for idx, item in enumerate(group.items, 1):
            if idx == 1:
                kept.append(item)
            else:
                remove_folder(item)
                deleted.append(item)
    return kept, deleted


def remove_empty_folders(root: FolderNode) -> list[FolderNode]:
    removed: list[FolderNode] = []
    changed = True
    while changed:
        changed = False
        empty = collect_empty_folders(root)
        for folder in empty:
            remove_folder(folder)
            removed.append(folder)
            changed = True
    return removed
