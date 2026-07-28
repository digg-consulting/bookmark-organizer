# bookmark-organizer

CLI utility to detect and clean up duplicate bookmarks in Brave and Chrome.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/digg-consulting/bookmark-organizer/main/install.sh | bash
```

## Update

```bash
curl -fsSL https://raw.githubusercontent.com/digg-consulting/bookmark-organizer/main/update.sh | bash
```

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/digg-consulting/bookmark-organizer/main/uninstall.sh | bash
```

## Usage

Scan for duplicate bookmarks without changing anything:

```bash
bookmark-organizer scan --browser brave
bookmark-organizer scan --browser chrome
```

Clean up duplicates interactively:

```bash
bookmark-organizer clean --browser brave --interactive
```

Auto-clean without prompts:

```bash
bookmark-organizer clean --browser brave --auto
```

Preview changes without writing:

```bash
bookmark-organizer clean --browser brave --dry-run
```

Remove empty folders after cleanup:

```bash
bookmark-organizer clean --browser brave --remove-empty
```

Scan only links or only folders:

```bash
bookmark-organizer scan --browser brave --links --no-folders
bookmark-organizer clean --browser brave --folders --no-links
```

## How it works

`bookmark-organizer` reads your browser's `Bookmarks` JSON file, analyzes it for duplicate entries, and optionally writes a cleaned version back to disk.

### Bookmark file format

Brave and Chrome export bookmarks as a single JSON file with this structure:

```json
{
  "roots": {
    "bookmark_bar": { "type": "folder", "name": "Bookmarks bar", "children": [...] },
    "other": { "type": "folder", "name": "Other bookmarks", "children": [...] },
    "synced": { ... }
  },
  "version": 1
}
```

The tool walks the three root trees (`bookmark_bar`, `other`, `synced`) and builds an in-memory representation of folders and URLs.

### Duplicate detection

**Links** are grouped by a normalized URL key. Normalization applies these rules:

- Scheme and host are lowercased.
- Default ports (`:80` for HTTP, `:443` for HTTPS) are stripped.
- The trailing slash is removed from the path.
- Query parameters are sorted alphabetically.
- Fragments are discarded.

Two bookmarks with the same normalized URL are considered duplicates, even if their titles differ or they live in different folders.

**Folders** are grouped by a case-insensitive name across all parent paths. Two folders with the same name anywhere in the bookmark tree are considered duplicates, even if they live under different parents.

### Cleanup process

When you run `clean`, the tool:

1. Loads the `Bookmarks` file into memory.
2. Finds duplicate link groups and duplicate folder groups.
3. Prompts you (interactive mode) or applies heuristics (auto mode) to decide which items to keep.
4. Optionally removes empty folders left behind after cleanup.
5. Writes the modified JSON back to the same file unless `--dry-run` is set.

In interactive mode, you can keep the first item, select a specific item to keep, delete all duplicates in a group, or quit and skip the rest. In auto mode, the first encountered item in each group is kept and all others are removed.

### File paths and defaults

By default, the CLI looks for the browser's live `Bookmarks` file:

- **Brave (macOS)**: `~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Bookmarks`
- **Chrome (macOS)**: `~/Library/Application Support/Google/Chrome/Default/Bookmarks`

You can also pass a custom JSON file path as a positional argument.

The app follows the XDG Base Directory specification for its own runtime files:

| Variable | Default path |
|----------|-------------|
| `XDG_CONFIG_HOME` | `~/.config/digg/bookmark-organizer` |
| `XDG_CACHE_HOME` | `~/.cache/digg/bookmark-organizer` |
| `XDG_DATA_HOME` | `~/.local/share/digg/bookmark-organizer` |

## Development

```bash
uv sync
uv run pytest tests/
```

A convenience development runner is included at the repo root:

```bash
./bookmark-organizer scan --browser brave
./bookmark-organizer clean --browser chrome --interactive
```

This runs the CLI via `uv run` from the project directory without needing a global install.
