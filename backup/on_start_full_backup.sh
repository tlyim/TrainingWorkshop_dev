#!/bin/bash
# .lightning_studio/on_start.sh
#
# Runs every time the Studio starts.
# Heavy one-time setup is gated behind a sentinel file so it only
# executes on the very first boot (or after you delete the sentinel).

set -euo pipefail

SENTINEL="$HOME/.lightning_studio/.setup_done"

# ── One-time setup ────────────────────────────────────────────────────────────
if [ ! -f "$SENTINEL" ]; then
  echo "==> [on_start] First-run setup beginning..."

  # 1. Install uv
  python3 -m pip install uv

  # 2. Clean broken dist-info to prevent uv errors (retained from original)
  find /home/zeus/miniconda3/envs/cloudspace/lib/python3.12/site-packages/ \
    -maxdepth 1 -name "*.dist-info" -type d \
    ! -exec test -f "{}/METADATA" \; -exec rm -rf "{}" \; 2>/dev/null || true

  # 3. Install Python packages via uv
  uv pip install --system --python python3 \
    marimo \
    ipykernel \
    pandas \
    plotly \
    statsmodels \
    micropip \
    groq \
    dotenv \
    dspy \
    playwright \
    pymupdf \
    fitz \
    pillow \
    pytesseract \
    nltk \
    spacy \
    wordcloud

  # 4. Install Playwright browser
  playwright install chromium

  # 5. Remove broken yarn apt source that can block apt updates
  sudo sh -c "grep -rl 'dl.yarnpkg.com' /etc/apt/sources.list \
    /etc/apt/sources.list.d 2>/dev/null | xargs -r rm -f"

  # 6. Update apt and install dependencies for adding repositories
  sudo apt update
  sudo apt install --no-install-recommends -y software-properties-common dirmngr

  # 7. Add CRAN repository for R 4.6.*
  wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
  sudo add-apt-repository -y "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"

  # 8. Update apt to fetch new CRAN packages
  sudo apt update

  # 9. Install Playwright OS dependencies
  playwright install-deps

  # 10. Install system packages including R 4.6.*
  sudo apt install -y --no-install-recommends \
    tesseract-ocr \
    'r-base=4.6.*' \
    libharfbuzz-dev \
    libfribidi-dev \
    libcairo2-dev \
    libmagick++-dev \
    librsvg2-dev \
    libqpdf-dev \
    libxslt1-dev \
    pandoc \
    nano

  # Set nano as dafault git editor (instead of vim which can be confusing for new users)
  git config --global core.editor "nano"

  # 11. Install Quarto
  curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb
  sudo apt install -y ./quarto-linux-amd64.deb
  rm quarto-linux-amd64.deb

  # 12. Install radian (R console) via pip
  pip install radian

  # 13. Install R packages into a local library
  sudo Rscript -e "dir.create('R_library', showWarnings=FALSE); .libPaths(c('R_library', .libPaths())); pak::pak(c('languageserver', 'httpgd'))"
 # sudo Rscript -e "dir.create('R_library', showWarnings=FALSE); .libPaths(c('R_library', .libPaths())); install.packages(c("pak"), lib = 'R_library', repos='https://packagemanager.posit.co/cran/__linux__/noble/latest', dependencies=TRUE); pak::pak(c('languageserver', 'httpgd'))"

  # 14. Create a thin /usr/local/bin/r wrapper that delegates to radian
  #sudo sh -c 'printf "#!/bin/sh\nradian \"\$@\"\ntrue\n" > /usr/local/bin/r && chmod +x /usr/local/bin/r'

    #   # 15. Configure VS Code tasks
    #   VSCODE_TASKS="$HOME/.vscode/tasks.json"
    #   mkdir -p "$(dirname "$VSCODE_TASKS")"

    #   cat > "$VSCODE_TASKS" << 'EOF'
    # {
    #   "version": "2.0.0",
    #   "tasks": [
    #     {
    #       "label": "Serve workspace (python3 -m http.server ??? 8000)",
    #       "type": "shell",
    #       "command": "python3 -m http.server 8000 --bind 0.0.0.0",
    #       "options": {
    #         "cwd": "${workspaceFolder}"
    #       },
    #       "isBackground": true,
    #       "problemMatcher": []
    #     }
    #   ]
    # }
    # EOF

  # Mark setup as complete
  touch "$SENTINEL"
  echo "==> [on_start] First-run setup complete."

else
  echo "==> [on_start] Setup already done (delete $SENTINEL to re-run)."
fi

# ── Every-start steps (fast, safe to repeat) ─────────────────────────────────

# 16. Clean up any leftover R package lock folders
find "$HOME/R_library" -type d -name "00LOCK-*" \
  -exec rm -rf {} + 2>/dev/null || true

# 17. Install VS Code extensions via code-server
# Fixed syntactical commas in the Bash array strings.
EXTENSIONS=(
  "ms-python.python"
  "ms-toolsai.jupyter"  # (not on Open-VSX; install separately from VSIX below)
  "marimo-team.vscode-marimo"
  "shd101wyy.markdown-preview-enhanced"
  "ms-vscode.live-server"
  "mechatroner.rainbow-csv"
  "bierner.markdown-mermaid"
  "REditorSupport.r"
  "REditorSupport.r-syntax"
  "quarto.quarto"
)
for ext in "${EXTENSIONS[@]}"; do
  code-server --install-extension "$ext" || echo "WARNING: failed to install $ext 111"
done

# Install ms-toolsai.jupyter from VSIX (not on Open-VSX)
  # JUPYTER_VSIX="$HOME/.lightning_studio/jupyter.vsix"
  # JUPYTER_URL="https://github.com/microsoft/vscode-jupyter/releases/download/v2025.3.0/ms-toolsai.jupyter-2025.3.0.vsix"
  # if [ ! -f "$JUPYTER_VSIX" ]; then
  #   curl -L "$JUPYTER_URL" -o "$JUPYTER_VSIX"
  # fi
  # code-server --install-extension "$JUPYTER_VSIX" || echo "WARNING: failed to install jupyter vsix 222"

# 18. Configure VS Code R settings
VSCODE_SETTINGS="$HOME/.local/share/code-server/User/settings.json"
mkdir -p "$(dirname "$VSCODE_SETTINGS")"

# dynamic lookup with a hardcoded fallback
R_PATH="$(which R || echo '/usr/bin/R')"
RADIAN_PATH="$(which radian || echo '/home/zeus/miniconda3/envs/cloudspace/bin/radian')"

python3 -c "
import json, os
settings_path = '$VSCODE_SETTINGS'
settings = {}
if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
settings['r.rpath.linux'] = '$R_PATH'
settings['r.rterm.linux'] = '$RADIAN_PATH'
settings['r.bracketedPaste'] = True
settings['quarto.render.previewType'] = 'external'
settings['livePreview.hostIP'] = '0.0.0.0'
settings['livePreview.openPreviewTarget'] = 'External Browser'
settings['extensions.autoUpdate'] = True
settings['extensions.ignoreRecommendations'] = False
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
"

# 14. Create a thin /usr/local/bin/r wrapper that delegates to radian
sudo sh -c 'printf "#!/bin/sh\nradian \"\$@\"\ntrue\n" > /usr/local/bin/r && chmod +x /usr/local/bin/r'

echo "==> [on_start] Studio ready."

git config --global user.name "Tl Yim (Lightning.ai)"
#git config --global user.email "10102234+tlyim@users.noreply.github.com"
if echo "${LIGHTNING_USERNAME:-}" | grep -q "tlyim"; then GIT_COMMITTER_EMAIL=$(curl -s https://gist.githubusercontent.com/tlyim/ebbea2d6ac7e91a8f24505000df00271/raw/email_alias.txt); [ -n \"$GIT_COMMITTER_EMAIL\" ] && git config --global user.email \"$GIT_COMMITTER_EMAIL\" || echo \"WARNING: git user.email not set\" >&2; fi && CONFIGURED=$(git config --global user.email 2>/dev/null); if [ -n \"$CONFIGURED\" ]; then echo \"git user.email set to: $CONFIGURED\"; else echo \"WARNING: git user.email is not set - required for commits\" >&2; fi 

# Add qpreview function to ~/.bashrc if not already there
grep -qxF 'qpreview() {' ~/.bashrc || cat >> ~/.bashrc << 'EOF'
qpreview() {
    quarto preview "$1" --host 0.0.0.0 --port 9000
}
EOF

# Other services...
#marimo edit --port 2718 --headless &
#python3 -m http.server 8000 --bind 0.0.0.0 &

#wait
