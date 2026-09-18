#!/bin/bash
# .lightning_studio/on_start.sh
#
# Runs every time the Studio starts.
# Heavy one-time setup is gated behind a sentinel file so it only
# executes on the very first boot (or after you delete the sentinel).

echo "Starting time: $(date +'%F %T')"

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
    radian \
    marimo \
    ipykernel \
    pandas \
    plotly \
    statsmodels \
    micropip \
    groq \
    python-dotenv \
    dspy-ai \
    playwright \
    pymupdf \
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
  #pip install radian (now used uv to pip install)

  # 13. Install R packages into a local library (must install pak:: first)
  sudo Rscript -e "
    install.packages('pak', repos='https://r-lib.github.io/p/pak/stable/', quiet=TRUE);
    dir.create('R_library', showWarnings=FALSE);
    .libPaths(c('R_library', .libPaths()));
    pak::pak(c('languageserver', 'httpgd'))
  "

  # 17. Install VS Code extensions — skip already-installed ones, run in parallel
  # Note: Neither live preview / live server extensions are working well in Lightning.ai
  EXTENSIONS=(
    "ms-python.python"
    "ms-toolsai.jupyter"
    "marimo-team.vscode-marimo"
    "REditorSupport.r"
    "REditorSupport.r-syntax"
  #  "quarto.quarto"
    "mechatroner.rainbow-csv"
    "bierner.markdown-mermaid"
    "shd101wyy.markdown-preview-enhanced"
  #  "ms-vscode.live-server"
  #  "ritwickdey.LiveServer"
  )

  # Get installed extensions once (lowercase for case-insensitive compare)
  INSTALLED=$(code-server --list-extensions 2>/dev/null | tr '[:upper:]' '[:lower:]')

  pids=()
  for ext in "${EXTENSIONS[@]}"; do
    if echo "$INSTALLED" | grep -qi "^${ext}$"; then
      : # already installed, skip
    else
      echo "Installing missing extension: $ext"
      code-server --install-extension "$ext" \
        || echo "WARNING: failed to install $ext" &
      pids+=($!)
    fi
  done
  # Wait for any parallel installs to finish
  (( ${#pids[@]} > 0 )) && wait "${pids[@]}"

 
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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Copy settings.json for Lightning.ai Studio
cp .vscode/settings_Lightning.json .vscode/settings.json


      # # Note: settings.json will be further modified on every start outside this SENTINEL block 
      # # 18. Configure VS Code R settings
      # VSCODE_SETTINGS="$HOME/.local/share/code-server/User/settings.json"
      # mkdir -p "$(dirname "$VSCODE_SETTINGS")"

      # # dynamic lookup with a hardcoded fallback
      # R_PATH="$(which R || echo '/usr/bin/R')"
      # RADIAN_PATH="$(which radian || echo '/home/zeus/miniconda3/envs/cloudspace/bin/radian')"

      # python3 -c "
      # import json, os
      # settings_path = '$VSCODE_SETTINGS'
      # settings = {}
      # if os.path.exists(settings_path):
      #     try:
      #         with open(settings_path) as f:
      #             settings = json.load(f)
      #     except (json.JSONDecodeError, ValueError):
      #         print('Warning: settings.json was malformed, starting fresh.')

      # settings['r.rterm.linux'] = '$RADIAN_PATH'

      # with open(settings_path, 'w') as f:
      #     json.dump(settings, f, indent=2)
      # "


# 19. Create radian wrapper (idempotent, only writes if missing)
if [ ! -f /usr/local/bin/r ]; then
  sudo sh -c 'printf "#!/bin/sh\nradian \"\$@\"\ntrue\n" > /usr/local/bin/r && chmod +x /usr/local/bin/r'
fi

echo "==> [on_start] Studio ready."

# 20. Git identity
git config --global user.name "Tl Yim (Lightning.ai)"

# FIX: was using escaped quotes that printed literally
if echo "${LIGHTNING_USERNAME:-}" | grep -q "tlyim"; then
  GIT_EMAIL=$(curl -sf https://gist.githubusercontent.com/tlyim/ebbea2d6ac7e91a8f24505000df00271/raw/email_alias.txt)
  if [ -n "$GIT_EMAIL" ]; then
    git config --global user.email "$GIT_EMAIL"
    echo "git user.email set to: $(git config --global user.email)"
  else
    echo "WARNING: git user.email not set (curl returned empty)" >&2
  fi
fi


echo "Ending time: $(date +'%F %T')"
