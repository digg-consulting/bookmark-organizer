"""Interactive and automatic cleanup logic for duplicate bookmarks."""
from __future__ import annotations

from rich.console import Console
from rich.prompt import Prompt

from .models import BookmarkNode, DuplicateFolderGroup, DuplicateLinkGroup, FolderNode
from .writer import collect_empty_folders, remove_bookmark, remove_folder

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


def prompt_keep_choice(group: DuplicateLinkGroup) -> int | None:
    console.print(f"\n[bold cyan]Link group:[/bold cyan] {group.normalized_url}")
    for idx, item in enumerate(group.items, 1):
        marker = " [green](keep)[/green]" if idx == 1 else ""
        console.print(f"  {idx}. {item.name} — {item.path}{marker}")
    console.print("  [bold]Actions:[/bold] [K]eep first  [S]elect  [D]elete all  [Q]uit")
    choice = Prompt.ask("Choose action", choices=["k", "s", "d", "q"], default="k").lower()
    if choice == "k":
        return 1
    if choice == "d":
        return 0
    if choice == "s":
        console.print("Select which to keep (enter number):")
        for idx, item in enumerate(group.items, 1):
            console.print(f"  {idx}. {item.name} — {item.path}")
        sel = Prompt.ask("Keep #", choices=[str(i) for i in range(1, len(group.items) + 1)])
        return int(sel)
    return None


def interactive_cleanup_links(
    groups: list[DuplicateLinkGroup],
) -> tuple[list[BookmarkNode], list[BookmarkNode]]:
    kept: list[BookmarkNode] = []
    deleted: list[BookmarkNode] = []
    for group in groups:
        keep_idx = prompt_keep_choice(group)
        if keep_idx is None:
            console.print("[yellow]Skipped remaining groups.[/yellow]")
            break
        for idx, item in enumerate(group.items, 1):
            if idx == keep_idx:
                kept.append(item)
            else:
                remove_bookmark(item)
                deleted.append(item)
    return kept, deleted


def prompt_keep_folder(group: DuplicateFolderGroup) -> int | None:
    console.print(f"\n[bold cyan]Folder group:[/bold cyan] '{group.name}' under '{group.parent_path}'")
    for idx, item in enumerate(group.items, 1):
        marker = " [green](keep)[/green]" if idx == 1 else ""
        console.print(f"  {idx}. {item.name}{marker}")
    console.print("  [bold]Actions:[/bold] [K]eep first  [S]elect  [D]elete all  [Q]uit")
    choice = Prompt.ask("Choose action", choices=["k", "s", "d", "q"], default="k").lower()
    if choice == "k":
        return 1
    if choice == "d":
        return 0
    if choice == "s":
        console.print("Select which to keep (enter number):")
        for idx, item in enumerate(group.items, 1):
            console.print(f"  {idx}. {item.name}")
        sel = Prompt.ask("Keep #", choices=[str(i) for i in range(1, len(group.items) + 1)])
        return int(sel)
    return None


def interactive_cleanup_folders(
    groups: list[DuplicateFolderGroup],
) -> tuple[list[FolderNode], list[FolderNode]]:
    kept: list[FolderNode] = []
    deleted: list[FolderNode] = []
    for group in groups:
        keep_idx = prompt_keep_folder(group)
        if keep_idx is None:
            console.print("[yellow]Skipped remaining groups.[/yellow]")
            break
        for idx, item in enumerate(group.items, 1):
            if idx == keep_idx:
                kept.append(item)
            else:
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
