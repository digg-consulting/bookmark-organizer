#!/usr/bin/env bash
set -euo pipefail

APP_NAME="bookmark-organizer"
REPO="digg-consulting/bookmark-organizer"
BRANCH="main"
INSTALL_DIR="${HOME}/.local/share/digg/bookmark-organizer"
INSTALL_PARENT="${HOME}/.local/share/digg"
BIN_DIR="${HOME}/.local/bin"
CLI_BIN="${BIN_DIR}/${APP_NAME}"

if [ ! -d "${INSTALL_DIR}" ] || [ ! -f "${INSTALL_DIR}/src/bookmark_organizer/cli.py" ]; then
    echo "Error: ${APP_NAME} is not installed at ${INSTALL_DIR}."
    echo "Run install.sh first."
    exit 1
fi

echo "Updating ${APP_NAME}..."

TMP_TARBALL="$(mktemp /tmp/bookmark-organizer-XXXXXX.tar.gz)"
curl -fsSL "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz" -o "${TMP_TARBALL}"
echo "==> Extracting..."
tar -xzf "${TMP_TARBALL}" -C "${INSTALL_PARENT}"
rm -f "${TMP_TARBALL}"
EXTRACTED_DIR="$(find "${INSTALL_PARENT}" -maxdepth 1 -type d -name "${APP_NAME}-*" | head -n 1)"
if [ -z "$EXTRACTED_DIR" ] || [ ! -d "$EXTRACTED_DIR" ]; then
    echo "Error: could not find extracted directory." >&2
    exit 1
fi
rm -rf "${INSTALL_DIR}"
mv "${EXTRACTED_DIR}" "${INSTALL_DIR}"

echo "Syncing dependencies with uv..."
cd "${INSTALL_DIR}"
uv sync

echo "Reinstalling CLI..."
uv tool uninstall "${APP_NAME}" 2>/dev/null || true
uv tool install --force .

echo "Update complete."
