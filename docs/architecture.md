# Architecture

## Overview

`bookmark-organizer` is a CLI tool built with `typer` and `rich` that detects and cleans up duplicate bookmarks in Brave and Chrome browsers.

## Project Structure

```
bookmark-organizer/
├── src/bookmark_organizer/
│   ├── __init__.py      # Package init, version
│   ├── cli.py           # Typer CLI entry point (scan, clean commands)
│   ├── models.py        # Dataclasses: BookmarkNode, FolderNode, etc.
│   ├── parser.py        # Load bookmarks JSON, build tree, find duplicates
│   ├── normalizer.py    # URL normalization (scheme, host, port, query, fragment)
│   ├── dedup.py         # Grouping logic for duplicate links and folders
│   ├── writer.py        # Write bookmarks back to JSON, remove nodes
│   ├── cleanup.py       # Interactive and auto cleanup logic
│   ├── reporter.py      # Rich table output for duplicate groups
│   └── xdg.py           # XDG Base Directory resolution (digg namespace)
├── tests/               # Pytest test suite
├── docs/                # Architecture and deployment guides
├── pyproject.toml       # Project config, dependencies, tool settings
├── install.sh           # Standalone installer
├── uninstall.sh         # Uninstaller
└── update.sh            # Self-update script
```

## Key Components

- **parser.py**: Loads the browser's `Bookmarks` JSON file and builds an in-memory tree of `FolderNode` and `BookmarkNode` objects. Provides `iter_bookmarks()` and `iter_folders()` to traverse the tree.
- **normalizer.py**: Normalizes URLs by lowercasing scheme/host, stripping default ports, sorting query parameters, and removing fragments. Used by dedup logic.
- **dedup.py**: Groups bookmarks by normalized URL and folders by case-insensitive name to find duplicates.
- **cleanup.py**: Implements interactive (prompt user) and automatic (keep first) cleanup strategies. Also handles empty folder removal.
- **writer.py**: Serializes the in-memory tree back to the Bookmarks JSON file and provides node removal utilities.
- **xdg.py**: Resolves XDG Base Directory paths under the `digg` namespace for config, cache, data, and bin directories.

## Data Flow

1. Load bookmarks JSON → `parser.load_bookmarks()`
2. Build tree → `parser._build_tree()`
3. Traverse tree → `parser.iter_bookmarks()` / `parser.iter_folders()`
4. Normalize URLs → `normalizer.normalize_url()`
5. Group duplicates → `dedup.group_by_normalized_url()` / `dedup.group_duplicate_folders()`
6. Cleanup → `cleanup.interactive_cleanup_links()` / `cleanup.auto_cleanup_links()` etc.
7. Write back → `writer.write_bookmarks()`