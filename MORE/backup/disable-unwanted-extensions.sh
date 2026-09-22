#!/usr/bin/env bash

set -u

extension_dir="${HOME}/.vscode-server/extensions"
inventory_file="${TMPDIR:-/tmp}/vscode-extensions.txt"

if [[ -d "$extension_dir" ]]; then
  find "$extension_dir" -maxdepth 1 -type d \
    -name 'julialang.language-julia-*' -prune -exec rm -rf {} +

  find "$extension_dir" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' \
    | sort > "$inventory_file"
else
  printf '%s\n' "VS Code extension directory not found: $extension_dir" > "$inventory_file"
fi

printf '%s\n' "VS Code extension inventory: $inventory_file"