# Code Agent Plan: bookmark-organizer Improvements

## Context
The install verification failure has been fixed in commit `68b9ed5`. The repo is clean and all tests pass. This plan covers additional improvements a code agent can execute autonomously.

---

## Plan

### 1. Add install script regression test
- Create `tests/test_install.py` with a test that:
  - Creates a temp directory
  - Copies the project files
  - Runs `bash install.sh` with `FORCE_INSTALL=1`
  - Verifies the CLI binary exists at `~/.local/bin/bookmark-organizer`
  - Verifies `bookmark-organizer --help` exits 0
  - Cleans up installed artifacts after test
- Add `test_install` to CI workflow (`.github/workflows/ci.yml`) to run on macOS and Ubuntu

### 2. Improve duplicate folder reporting with full paths per item
- In `src/bookmark_organizer/reporter.py`, modify `print_duplicate_folders` to show each duplicate folder's full resolved path (not just the group parent path)
- Each row should include: group number, folder name, full path
- Update `DuplicateFolderGroup` model if needed to store per-item paths

### 3. Add `--output` flag to `clean` command
- Allow users to specify an output file path instead of overwriting the input `Bookmarks` file
- Default behavior remains in-place overwrite
- Add test for `--output` flag writing to correct path

### 4. Harden `clean` command with backup option
- Add `--backup` flag to `clean` that copies the original `Bookmarks` file to `Bookmarks.bak` before writing
- Ensure backup is written before any modifications
- Add test verifying backup file creation

### 5. Add browser auto-detection
- When `--browser` is not specified, auto-detect available browser profiles on the system
- Check for Brave first, then Chrome, then Chromium
- Fall back to a clear error message if none found
- Add tests for auto-detection logic

---

## Execution Order
1. Start with task 1 (install regression test) — validates the fix and prevents regressions
2. Then tasks 2-5 in any order — each is independent
3. After each task: run `pytest`, `ruff check`, `mypy`, and push

## Acceptance Criteria
- All tests pass (`pytest tests/ -v`)
- Lint passes (`ruff check src/ tests/`)
- Type check passes (`mypy src/ tests/`)
- Shell scripts pass syntax check (`bash -n install.sh uninstall.sh update.sh`)
- All changes committed and pushed to `origin/main`
