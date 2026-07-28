"""CLI commands for bookmark-organizer."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

from .models import FolderNode, get_default_bookmarks_path
from .parser import (
    _build_tree,
    _get_root,
    find_duplicate_folders,
    find_duplicate_links,
    load_bookmarks,
)
from .reporter import print_duplicate_folders, print_duplicate_links
from .writer import write_bookmarks

__all__ = ["app"]

app = typer.Typer(help="Detect and clean up duplicate bookmarks in Brave and Chrome")
console = Console()

_INPUT_PATH_SCAN = typer.Argument(
    None,
    help="Path to Bookmarks JSON file. Defaults to live browser profile if available.",
)
_INPUT_PATH_CLEAN = typer.Argument(
    None,
    help="Path to Bookmarks JSON file. Defaults to live browser profile if available.",
)


def _browser_callback(ctx: typer.Context, value: str) -> str:
    if value not in ("brave", "chrome"):
        raise typer.BadParameter("Browser must be 'brave' or 'chrome'")
    return value


def _resolve_path(input_path: Path | None, browser: str) -> Path:
    path = input_path or get_default_bookmarks_path(browser)
    if not path.exists():
        console.print(f"[red]Bookmarks file not found: {path}[/red]")
        raise typer.Exit(1)
    return path


@app.command()
def scan(
    input_path: Path | None = _INPUT_PATH_SCAN,
    browser: str = typer.Option("brave", "--browser", "-b", help="Browser to scan: brave or chrome", callback=_browser_callback),
    links: bool = typer.Option(True, "--links/--no-links", help="Scan for duplicate links"),
    folders: bool = typer.Option(True, "--folders/--no-folders", help="Scan for duplicate folders"),
) -> None:
    path = _resolve_path(input_path, browser)
    data = load_bookmarks(path)
    if links:
        link_groups = find_duplicate_links(data)
        print_duplicate_links(link_groups)
    if folders:
        folder_groups = find_duplicate_folders(data)
        print_duplicate_folders(folder_groups)


@app.command()
def clean(
    input_path: Path | None = _INPUT_PATH_CLEAN,
    browser: str = typer.Option("brave", "--browser", "-b", help="Browser to clean: brave or chrome", callback=_browser_callback),
    interactive: bool = typer.Option(True, "--interactive/--auto", help="Interactive cleanup mode"),
    remove_empty: bool = typer.Option(False, "--remove-empty", help="Remove empty folders after cleanup"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print changes without writing"),
) -> None:
    from .cleanup import (
        auto_cleanup_folders,
        auto_cleanup_links,
        interactive_cleanup_folders,
        interactive_cleanup_links,
        remove_empty_folders,
    )

    path = _resolve_path(input_path, browser)
    data = load_bookmarks(path)
    link_groups = find_duplicate_links(data)
    folder_groups = find_duplicate_folders(data)

    if not link_groups and not folder_groups:
        console.print("[green]No duplicates found.[/green]")
        raise typer.Exit(0)

    console.print(f"[bold]Found {len(link_groups)} duplicate link groups and {len(folder_groups)} duplicate folder groups.[/bold]")

    if interactive:
        if link_groups:
            kept_links, deleted_links = interactive_cleanup_links(link_groups)
            console.print(f"Kept {len(kept_links)} links, deleted {len(deleted_links)} links.")
        if folder_groups:
            kept_folders, deleted_folders = interactive_cleanup_folders(folder_groups)
            console.print(f"Kept {len(kept_folders)} folders, deleted {len(deleted_folders)} folders.")
    else:
        if link_groups:
            kept_links, deleted_links = auto_cleanup_links(link_groups)
            console.print(f"Kept {len(kept_links)} links, deleted {len(deleted_links)} links.")
        if folder_groups:
            kept_folders, deleted_folders = auto_cleanup_folders(folder_groups)
            console.print(f"Kept {len(kept_folders)} folders, deleted {len(deleted_folders)} folders.")

    if remove_empty:
        root_folder = None
        for root_key in ("bookmark_bar", "other", "synced"):
            root = _get_root(data, root_key)
            if root:
                root_folder = _build_tree(root, parent=None)
                if isinstance(root_folder, FolderNode):
                    removed = remove_empty_folders(root_folder)
                    console.print(f"Removed {len(removed)} empty folders.")
                    break

    if dry_run:
        console.print("[yellow]Dry run complete. No changes written.[/yellow]")
        raise typer.Exit(0)

    if Confirm.ask("Write changes to file?", default=True):
        write_bookmarks(data, path)
        console.print(f"[green]Changes written to {path}[/green]")
    else:
        console.print("[yellow]Changes discarded.[/yellow]")


if __name__ == "__main__":
    app()