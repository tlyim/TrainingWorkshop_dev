#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname -- "$SCRIPT_DIR")"
R_LIBRARY="$WORKSPACE_DIR/R_library"
SENTINEL="$HOME/.lightning_studio/.setup_done"

cd "$WORKSPACE_DIR"
mkdir -p "$(dirname -- "$SENTINEL")" "$R_LIBRARY"

echo "Starting time: $(date +'%F %T')"

install_python_packages() {
  python3 -m pip install --break-system-packages uv 2>/dev/null || python3 -m pip install uv

  local site_packages
  site_packages="$(python3 -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null || true)"
  if [ -n "$site_packages" ] && [ -d "$site_packages" ]; then
    find "$site_packages" -maxdepth 1 -name '*.dist-info' -type d \
      ! -exec test -f '{}/METADATA' \; -exec rm -rf '{}' + 2>/dev/null || true
  fi

  uv pip install --system --python "$(command -v python3)" \
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
}

install_system_packages() {
  sudo sh -c "grep -rl 'dl.yarnpkg.com' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null | xargs -r rm -f"
  sudo apt update
  sudo apt install --no-install-recommends -y software-properties-common dirmngr

  if [ ! -f /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc ]; then
    wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc \
      | sudo tee /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc >/dev/null
  fi

  local cran_source
  cran_source="deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
  if ! grep -RqsF "$cran_source" /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null; then
    echo "$cran_source" | sudo tee /etc/apt/sources.list.d/cran.list >/dev/null
  fi

  sudo apt update
  sudo apt install --no-install-recommends -y \
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

  playwright install-deps chromium
}

install_quarto() {
  if ! command -v quarto >/dev/null 2>&1; then
    local quarto_deb="/tmp/quarto-linux-amd64.deb"
    curl -fsSL https://quarto.org/download/latest/quarto-linux-amd64.deb -o "$quarto_deb"
    sudo apt install -y "$quarto_deb"
    rm -f "$quarto_deb"
  fi
}

install_bun_opencode() {
  export BUN_INSTALL="/usr/local/bun"
  export PATH="$BUN_INSTALL/bin:$PATH"

  local bun_bin="$BUN_INSTALL/bin/bun"
  local bunx_bin="$BUN_INSTALL/bin/bunx"
  local opencode_bin="$BUN_INSTALL/bin/opencode"

  if [ ! -x "$bun_bin" ]; then
    sudo mkdir -p "$BUN_INSTALL"
    sudo chown -R "$(id -u):$(id -g)" "$BUN_INSTALL"
    curl -fsSL https://bun.sh/install | bash
  fi

  if [ ! -x "$bun_bin" ] || [ ! -x "$bunx_bin" ]; then
    echo "ERROR: Bun installation did not provide bun and bunx in $BUN_INSTALL/bin" >&2
    return 1
  fi

  if [ ! -x "$opencode_bin" ]; then
    "$bun_bin" add --global opencode-ai
  fi

  if [ ! -x "$opencode_bin" ]; then
    echo "ERROR: OpenCode installation did not provide $opencode_bin" >&2
    return 1
  fi

  sudo ln -sfn "$bun_bin" /usr/local/bin/bun
  sudo ln -sfn "$bunx_bin" /usr/local/bin/bunx
  sudo ln -sfn "$opencode_bin" /usr/local/bin/opencode

  sudo tee /etc/profile.d/bun.sh >/dev/null <<EOF
export BUN_INSTALL="$BUN_INSTALL"
export PATH="$BUN_INSTALL/bin:\$PATH"
EOF

  echo "Bun installed: $bun_bin ($("$bun_bin" --version))"
  echo "BunX installed: $bunx_bin"
  echo "OpenCode installed: $opencode_bin ($("$opencode_bin" --version))"
}

install_r_packages() {
  sudo Rscript -e "
    install.packages('pak', repos='https://r-lib.github.io/p/pak/stable/', quiet=TRUE);
    dir.create('$R_LIBRARY', recursive=TRUE, showWarnings=FALSE);
    .libPaths(c('$R_LIBRARY', .libPaths()));
    pak::pak(c('languageserver', 'httpgd'))
  "
}

install_extensions() {
  local extensions=(
    'ms-python.python'
    'ms-toolsai.jupyter'
    'marimo-team.vscode-marimo'
    'REditorSupport.r'
    'REditorSupport.r-syntax'
    'mechatroner.rainbow-csv'
    'bierner.markdown-mermaid'
    'shd101wyy.markdown-preview-enhanced'
    'sst-dev.opencode'
    'ltmoerdani.opencode-copilot-chat'
  )
  local installed ext
  installed="$(code-server --list-extensions 2>/dev/null | tr '[:upper:]' '[:lower:]')"
  for ext in "${extensions[@]}"; do
    if ! grep -qxF "${ext,,}" <<< "$installed"; then
      code-server --install-extension "$ext" || echo "WARNING: failed to install $ext" >&2
    fi
  done
}

if [ ! -f "$SENTINEL" ]; then
  echo "==> [on_start] First-run setup beginning..."
  install_python_packages
  playwright install chromium
  install_system_packages
  install_quarto
  git config --global core.editor nano
  install_r_packages
  touch "$SENTINEL"
  echo "==> [on_start] First-run setup complete."
else
  echo "==> [on_start] Setup already done (delete $SENTINEL to re-run)."
fi

if ! command -v nano >/dev/null 2>&1; then
  sudo apt update
  sudo apt install --no-install-recommends -y nano
fi

install_bun_opencode

find "$R_LIBRARY" -type d -name '00LOCK-*' -prune -exec rm -rf {} + 2>/dev/null || true

if [ -f "$WORKSPACE_DIR/.vscode/settings_Lightning.json" ]; then
  cp "$WORKSPACE_DIR/.vscode/settings_Lightning.json" "$WORKSPACE_DIR/.vscode/settings.json"
fi

if command -v radian >/dev/null 2>&1 && { [ ! -e /usr/local/bin/r ] || [ ! -x /usr/local/bin/r ]; }; then
  sudo sh -c 'printf "#!/bin/sh\nradian \"$@\"\ntrue\n" > /usr/local/bin/r && chmod +x /usr/local/bin/r'
fi

if command -v code-server >/dev/null 2>&1; then
  install_extensions
fi

git config --global user.name "Tl Yim (Lightning.ai)"
if [[ "${LIGHTNING_USERNAME:-}" == *tlyim* ]]; then
  git_email="$(curl -sf https://gist.githubusercontent.com/tlyim/ebbea2d6ac7e91a8f24505000df00271/raw/email_alias.txt || true)"
  if [ -n "$git_email" ]; then
    git config --global user.email "$git_email"
  else
    echo "WARNING: git user.email not set" >&2
  fi
fi

echo "==> [on_start] Studio ready."
echo "Ending time: $(date +'%F %T')"
