"""CLI commands for bookmark-organizer."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

from .dedup import group_by_normalized_url, group_duplicate_folders
from .models import auto_detect_browser, get_default_bookmarks_path
from .parser import (
    build_trees,
    collect_bookmarks,
    collect_folders,
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
_OUTPUT_OPTION = typer.Option(
    None,
    "--output",
    "-o",
    help="Write cleaned bookmarks to this file instead of the input file",
)


def _browser_callback(ctx: typer.Context, value: str) -> str:
    if value not in ("auto", "brave", "chrome", "chromium"):
        raise typer.BadParameter("Browser must be 'auto', 'brave', 'chrome', or 'chromium'")
    return value


def _resolve_path(input_path: Path | None, browser: str) -> Path:
    if browser == "auto" and input_path is None:
        detected = auto_detect_browser()
        if not detected:
            console.print("[red]No supported browser bookmarks found. Install Brave, Chrome, or Chromium, or pass --browser explicitly.[/red]")
            raise typer.Exit(1)
        browser = detected
        console.print(f"[yellow]Auto-detected browser: {detected}[/yellow]")
    path = input_path or get_default_bookmarks_path(browser)
    if not path.exists():
        console.print(f"[red]Bookmarks file not found: {path}[/red]")
        raise typer.Exit(1)
    return path


@app.command()
def scan(
    input_path: Path | None = _INPUT_PATH_SCAN,
    browser: str = typer.Option("auto", "--browser", "-b", help="Browser to scan: auto, brave, chrome, or chromium", callback=_browser_callback),
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
    browser: str = typer.Option("auto", "--browser", "-b", help="Browser to clean: auto, brave, chrome, or chromium", callback=_browser_callback),
    interactive: bool = typer.Option(True, "--interactive/--auto", help="Interactive cleanup mode"),
    remove_empty: bool = typer.Option(False, "--remove-empty", help="Remove empty folders after cleanup"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print changes without writing"),
    output: Path | None = _OUTPUT_OPTION,
    backup: bool = typer.Option(False, "--backup", help="Create Bookmarks.bak before writing changes"),
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

    # Build in-memory trees from all roots so cleanup mutations persist.
    root_folders = build_trees(data)

    bookmarks = collect_bookmarks(root_folders)
    folders = collect_folders(root_folders)

    link_groups = group_by_normalized_url(bookmarks)
    folder_groups = group_duplicate_folders(folders)

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
        for root_key, root_folder in root_folders:
            removed = remove_empty_folders(root_folder)
            if removed:
                console.print(f"Removed {len(removed)} empty folders.")

    # Sync cleaned trees back into the original JSON structure.
    for root_key, root_folder in root_folders:
        data["roots"][root_key]["children"] = [c.to_dict() for c in root_folder.children]

    if dry_run:
        console.print("[yellow]Dry run complete. No changes written.[/yellow]")
        raise typer.Exit(0)

    write_path = output or path
    if backup:
        backup_path = write_path.parent / "Bookmarks.bak"
        import shutil as _shutil
        _shutil.copy2(path, backup_path)
        console.print(f"[yellow]Backup saved to {backup_path}[/yellow]")

    if Confirm.ask(f"Write changes to {write_path}?", default=True):
        write_bookmarks(data, write_path)
        console.print(f"[green]Changes written to {write_path}[/green]")
    else:
        console.print("[yellow]Changes discarded.[/yellow]")


if __name__ == "__main__":
    app()