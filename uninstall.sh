#!/usr/bin/env bash
set -euo pipefail

APP_NAME="bookmark-organizer"
INSTALL_DIR="${HOME}/.local/share/digg/bookmark-organizer"
BIN_DIR="${HOME}/.local/bin"
CLI_BIN="${BIN_DIR}/${APP_NAME}"
CONFIG_DIR="${HOME}/.config/digg/bookmark-organizer"

echo "Uninstalling ${APP_NAME}..."

echo "==> Removing CLI tool..."
uv tool uninstall "${APP_NAME}" 2>/dev/null || true

if [ -f "${CLI_BIN}" ]; then
    echo "==> Removing wrapper script..."
    rm -f "${CLI_BIN}"
fi

if [ -d "${INSTALL_DIR}" ]; then
    echo "==> Removing installation directory ${INSTALL_DIR}..."
    rm -rf "${INSTALL_DIR}"
else
    echo "Installation directory not found at ${INSTALL_DIR}. Skipping."
fi

if [ -d "${CONFIG_DIR}" ]; then
    if [ -t 0 ]; then
        read -p "Remove config directory ${CONFIG_DIR}? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "${CONFIG_DIR}"
            echo "Config removed."
        else
            echo "Config kept at ${CONFIG_DIR}."
        fi
    else
        echo "Config directory exists at ${CONFIG_DIR}. Remove manually if desired."
    fi
fi

echo "Uninstall complete."
