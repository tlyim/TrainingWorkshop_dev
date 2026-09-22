#!/bin/bash
# .devcontainer/setup.sh

# This is a placeholder for any setup commands you want to run when the container is created.


SENTINEL="$PWD/.devcontainer/.setup_done"

if [ ! -f "$SENTINEL" ]; then
  echo "USER is ${USER:-} (sbbg070); CODESPACES is ${CODESPACES:-} (true); LIGHTNING_USER_ID is ${LIGHTNING_USER_ID:-} ()"
  # One-time setup
  if [ -n "${WSL_DISTRO_NAME:-}" ]; then
  #if [ "${WSL_DISTRO_NAME:-}" = "Ubuntu" ]; then
    cp .vscode/settings_WSL.json .vscode/settings.json
    echo "Info: Using WSL VS Code"
  elif [ "${CODESPACES:-}" = "true" ]; then
    cp .vscode/settings_GitHub.json .vscode/settings.json
    echo "Info: Using a GitHub Codespace"
  elif [ -n "${LIGHTNING_USER_ID:-}" ]; then
    echo "Info: Using a Lightning.ai Studio"
    # Do NOT cp again as the radian location might not be set correctly
    #cp .vscode/settings_Lightning.json .vscode/settings.json
  fi

  touch "$SENTINEL"
  echo "==> [setup] First-run setup complete."
else
  echo "==> [setup] Already done (delete $SENTINEL to re-run)."
fi

# Fast idempotent steps here (if any) — run every open
