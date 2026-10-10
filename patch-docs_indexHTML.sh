#!/usr/bin/env bash
# patch-hide-code.sh — hide code by default in a marimo WASM export
# while KEEPING the "Show code" option in the triple-dot menu.
#
# Usage:
#   ./patch-hide-code.sh [path/to/index.html]     (default: docs/index.html)
#
# Prerequisite — export with --show-code so the menu option exists:
#   marimo export html-wasm notebook.py -o docs --mode run --show-code
#
# How it works:
#   marimo's mount config "view.showAppCode" controls BOTH the initial
#   code visibility AND whether the "Show code" menu item appears. So
#   --no-show-code hides the menu item entirely, and --show-code shows
#   code by default. The one knob that decouples them is the URL query
#   param "show-code": marimo reads it to decide the INITIAL state, while
#   the menu item stays gated only on showAppCode. This script injects a
#   tiny script that adds "?show-code=false" to the URL before marimo
#   mounts, giving: code hidden on load + "Show code" menu option present.
#
# Idempotent: safe to run repeatedly; skips if already patched.
set -euo pipefail

HTML="${1:-docs/index.html}"
MARKER="marimo-patch: hide-code-by-default"

if [[ ! -f "$HTML" ]]; then
  echo "error: $HTML not found" >&2
  exit 1
fi



# --- Remove an empty sandbox="" attribute from any <iframe> (runs every time,
#     even if the hide-code patch below was already applied) ---
python3 - "$HTML" <<'PY'
import re, sys

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    html = f.read()

count = 0

def strip(match):
    global count
    tag, n = re.subn(r"""\s+sandbox=(?:""|'')(?=[\s/>])""", "", match.group(0), flags=re.I)
    count += n
    return tag

new_html = re.sub(r"<iframe\b[^>]*>", strip, html, flags=re.I)
if count:
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
print(f'iframe sandbox="" removed: {count}')
PY



if grep -q "$MARKER" "$HTML"; then
  echo "already patched: $HTML"
  exit 0
fi

if ! grep -q '"showAppCode": true' "$HTML"; then
  echo "warning: $HTML does not contain \"showAppCode\": true." >&2
  echo "  Export with --show-code first, e.g.:" >&2
  echo "  marimo export html-wasm notebook.py -o docs --mode run --show-code" >&2
  exit 1
fi

python3 - "$HTML" "$MARKER" <<'PY'
import sys

html_path, marker = sys.argv[1], sys.argv[2]
with open(html_path, encoding="utf-8") as f:
    html = f.read()

patch = f"""<script>
  /* {marker} */
  (function () {{
    var params = new URLSearchParams(window.location.search);
    if (!params.has("show-code")) {{
      params.set("show-code", "false");
      var url = new URL(window.location.href);
      url.search = params.toString();
      history.replaceState(null, "", url.href);
    }}
  }})();
</script>
"""

anchor = '<div id="root"></div>'
if anchor not in html:
    print(f"error: anchor {anchor!r} not found in {html_path}", file=sys.stderr)
    sys.exit(1)

html = html.replace(anchor, anchor + "\n" + patch, 1)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"patched: {html_path} (code hidden by default; 'Show code' menu kept)")
PY