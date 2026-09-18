#!/usr/bin/env bash

# Compatibility entry point. Keep one authoritative Lightning bootstrap.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/on_start.sh" "$@"
