#!/usr/bin/env bash
set -euo pipefail

APP_NAME="bookmark-organizer"
INSTALL_DIR="${HOME}/.local/share/digg/bookmark-organizer"
BIN_DIR="${HOME}/.local/bin"
CLI_BIN="${BIN_DIR}/${APP_NAME}"

if [ ! -d "${INSTALL_DIR}" ] || [ ! -f "${INSTALL_DIR}/src/bookmark_organizer/cli.py" ]; then
    echo "Error: ${APP_NAME} is not installed at ${INSTALL_DIR}."
    echo "Run install.sh first."
    exit 1
fi

echo "Updating ${APP_NAME}..."
git -C "${INSTALL_DIR}" pull --ff-only

echo "Syncing dependencies with uv..."
cd "${INSTALL_DIR}"
uv sync

echo "Reinstalling CLI..."
uv tool uninstall "${APP_NAME}" 2>/dev/null || true
uv tool install --force -e .

echo "Update complete."
