# bookmark-organizer

CLI utility to detect and clean up duplicate bookmarks in Brave and Chrome.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/digg-consulting/bookmark-organizer/main/install.sh | bash
```

## Usage

Scan for duplicate bookmarks:

```bash
bookmark-organizer scan --browser brave
bookmark-organizer scan --browser chrome
```

Clean up duplicates interactively:

```bash
bookmark-organizer clean --browser brave --interactive
```

Or auto-clean without prompts:

```bash
bookmark-organizer clean --browser brave --auto
```

## Features

- Detect duplicate links (same URL, different names)
- Detect duplicate folders (same name under same parent)
- Interactive or automatic cleanup
- Remove empty folders after cleanup
- Dry-run mode to preview changes

## Development

```bash
uv sync
uv run pytest tests/
```