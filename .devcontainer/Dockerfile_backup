# ============================================================
# rebuild source for Docker image ghcr.io/tlyim/rpython 
# ============================================================
# Dockerfile — Python + Marimo + R + Quarto environment
# Based on .devcontainer/devcontainer.json
# ============================================================
LABEL org.opencontainers.image.source https://github.com/tlyim/rpython 

FROM ubuntu:24.04

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# ── Tell uv it's allowed to touch the externally-managed system Python ──
ENV UV_BREAK_SYSTEM_PACKAGES=1

# ── System locale & base utilities ──────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        git \
        gnupg \
        lsb-release \
        software-properties-common \
        dirmngr \
        sudo \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── R 4.6 (CRAN repo) ───────────────────────────────────────
RUN wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc \
        | tee /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc \
    && add-apt-repository -y \
        "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/" \
    && apt-get update

# ── System packages (mirrors onCreateCommand) ───────────────
RUN apt-get install -y --no-install-recommends \
        tesseract-ocr \
        "r-base=4.6.*" \
        libharfbuzz-dev \
        libfribidi-dev \
        libcairo2-dev \
        libmagick++-dev \
        librsvg2-dev \
        libqpdf-dev \
        libxslt1-dev \
        pandoc \
        python3-pip \
        # Playwright system dependencies
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libdbus-1-3 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2t64 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Quarto ───────────────────────────────────────────────────
RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb \
    && apt-get install -y ./quarto-linux-amd64.deb \
    && rm quarto-linux-amd64.deb

# ── Python tooling ───────────────────────────────────────────
# Install uv (fast pip replacement used by the devcontainer)
RUN pip3 install --break-system-packages uv

# ── Core Python packages (onCreateCommand) ───────────────────
RUN uv pip install --system --python python3 \
        marimo \
        ipykernel

# ── Additional Python packages (postCreateCommand) ───────────
RUN uv pip install --system --python python3 \
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
        wordcloud \
        radian

# ── Playwright Chromium browser ──────────────────────────────
RUN playwright install-deps chromium \
    && playwright install chromium

# ── radian wrapper (R REPL) ──────────────────────────────────
RUN printf '#!/bin/sh\nradian "$@"\ntrue\n' > /usr/local/bin/r \
    && chmod +x /usr/local/bin/r

# ── R packages (languageserver + httpgd via pak) ─────────────
# pak must be installed first; then the target packages.
RUN Rscript -e "\
    install.packages('pak', repos = 'https://r-lib.github.io/p/pak/stable/', quiet = TRUE); \
    dir.create('R_library', showWarnings = FALSE); \
    .libPaths(c('R_library', .libPaths())); \
    pak::pak(c('languageserver', 'httpgd')) \
"

# ── Shell helpers (qpreview alias from postCreateCommand) ────
RUN grep -qxF 'qpreview() {' /etc/bash.bashrc || printf '\nqpreview() {\n    quarto preview "$1" --no-browser --no-watch-inputs\n}\n' \
        >> /etc/bash.bashrc

# ── Expose forwarded ports ────────────────────────────────────
# 2718 → Marimo app, 8000 → directory listing, 3000 → spare
# Note: This is merely a metadata hint; no effect runtime. 
# Still need the forwardPorts speciification in devcontainer.json
EXPOSE 2718 8000 3000

# ── Default working directory ─────────────────────────────────
WORKDIR /workspace

# ── Default command: launch Marimo ───────────────────────────
CMD ["marimo", "edit", "--host", "0.0.0.0", "--port", "2718", "--no-token"]

# Final step: use setup.sh to copy settings.json
# COPY .devcontainer/setup.sh /tmp/setup.sh
# RUN bash /tmp/setup.sh
