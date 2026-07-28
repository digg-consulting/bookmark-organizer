"""Rich table reporters for duplicate link and folder groups."""
from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .models import DuplicateFolderGroup, DuplicateLinkGroup

__all__ = ["print_duplicate_folders", "print_duplicate_links"]


console = Console()


def print_duplicate_links(groups: list[DuplicateLinkGroup]) -> None:
    if not groups:
        console.print("[green]No duplicate links found.[/green]")
        return
    table = Table(title="Duplicate Links")
    table.add_column("Group", style="cyan")
    table.add_column("Normalized URL", style="magenta")
    table.add_column("Name", style="white")
    table.add_column("Path", style="yellow")
    for i, group in enumerate(groups, 1):
        for item in group.items:
            table.add_row(str(i), group.normalized_url, item.name, item.path)
    console.print(table)
    console.print(f"[bold]Total duplicate link groups: {len(groups)}[/bold]")


def print_duplicate_folders(groups: list[DuplicateFolderGroup]) -> None:
    if not groups:
        console.print("[green]No duplicate folders found.[/green]")
        return
    table = Table(title="Duplicate Folders")
    table.add_column("Group", style="cyan")
    table.add_column("Folder Name", style="white")
    table.add_column("Parent Path", style="yellow")
    for i, group in enumerate(groups, 1):
        for item in group.items:
            table.add_row(str(i), group.name, group.parent_path)
    console.print(table)
    console.print(f"[bold]Total duplicate folder groups: {len(groups)}[/bold]")
