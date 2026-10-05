# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.28.1",
#     "marimo>=0.23.3",
#     "pandas>=3.0.6",
#     "pyarrow>=25.0.1",
#     "python-dotenv>=1.2.3",
#     "pyodide-http; sys_platform == 'emscripten'",
# ]
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App()


@app.cell
def _():
    ## _Note:_ Follow the instructions below to deploy this marimo notebook as an HTML-WASM webpage with a default API key served by Cloudflare worker:

    """
    1. To create a Cloudflare worker (e.g., call it my-work):
    | Left panel | Compute | Workers & Pages | Create applications | Start with Hello World! |
    cloudflare.acdryim.workers.dev | 

    2. To add worker.js and set ALLOWED_ORIGINS:
    | Left panel | Compute | Workers & Pages | trip-dot button (of the Worker) | View settings | 
    Edit code | 
    Then 
    - paste all content of worker.js
    - add your GitHub Pages origin to the const ALLOWED_ORIGINS in the pasted worker.js  
      (e.g. https://tlyim.github.io, no path, no trailing slash)
    - click `Deploy` button

    3. To set API key as a variable/secret:
    | Left panel | Compute | Workers & Pages | triple-dot button (of the Worker) | View settings | 
    + Add variable |
    Then
    - paste the OLLAMA_API_KEY as secret
    - click `Add 1 variable and deploy` button

    4. To verify the worker (called 'cloudflare' here) is up and running, use:
    https://cloudflare.acdryim.workers.dev/api/config

    5. To connect the Cloudflare worker to the marimo notebook:
    - copy the *.workers.dev URL (e.g., my-work.acdryim.workers.dev") to set WORKER_URL in the notebook 
    - re-export with the bash command:

    `marimo export html-wasm 4MinExample_LLMapi_Cloudflare.py -o docs --sandbox --mode run --show-code --force`

    6. To patch the docs/index.html so that it hides the code when first loaded, run the patch script as a bash command:

    ./patch-hide-code.sh docs/index.html

    """

    print() # To prevent the string above from being displayed in the notebook output 
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## **Minimal Example: LLM Access via API**

    **What is this notebook?**
    A 4-minute, hands-on demo of how to ask a large language model (LLM)
    to do research work *from Python code* — no chat website needed.

    **The big idea in one sentence:**
    Your Python code sends a question over the internet to an AI provider,
    and the provider sends back an answer — just like ordering food by delivery app.

    **This notebook has two parts:**

    - **Part 1 — Try it once:** probe all providers, pick a provider and model, type a prompt, click a button.
    - **Part 2 — Scale it up:** use the same technique (and the same provider/model choice) to summarize and classify
      many company-report notes (SEC 10-K filings) automatically.

    > No prior AI experience needed. Just run the cells top-to-bottom
    > and use the drop-downs and buttons.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **How to read this notebook (30 seconds)**

    - **Text cells** (like this one) explain ideas — you only read them.
    - **Code cells** do the work behind the scenes.
    - **Widgets** are the drop-downs, sliders, and buttons you can click.
      When you change a widget, marimo automatically re-runs the cells that need it.
    - You do **not** need to re-type any code to follow the demo.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Setup: load tools and secret keys

    Before contacting an LLM, we load several packages and read your
    secret API keys from a `.env` file (so keys never appear in the code).

    This notebook runs in **two modes**:

    - **Locally** (`marimo run`): keys come from `.env`; calls go straight to
      the providers.
    - **In the browser** (exported WASM app): the page is served by a
      Cloudflare Worker that holds the host's keys as secrets and proxies the
      calls (with rate limits). You can also paste your own key below.
    """)
    return


@app.cell
def _():
    import marimo as mo  # notebook helpers: text display + widgets
    import os  # read secret API keys from the environment
    import sys  # detect whether we run in the browser (WASM) or locally
    import uuid  # create a random session ID for this run
    import httpx  # talk to websites/APIs over the internet
    from dotenv import load_dotenv

    # Are we running in the browser (exported WASM app) or locally?
    IS_WASM = sys.platform == "emscripten"

    # In the browser, httpx must use the browser's fetch() instead of real sockets; 
    # pyodide-http (declared in the script block) provides the shim.
    if IS_WASM:
        import pyodide_http  # type: ignore
        pyodide_http.patch_all()

    # Load keys from the `.env` file in the notebook folder (local runs only;
    # in the browser there is no filesystem, so this is skipped).
    if not IS_WASM and (mo.notebook_dir() / ".env").exists():
        load_dotenv(mo.notebook_dir() / ".env")

    # In the browser, the notebook's location is the page URL (e.g. the
    # GitHub Pages origin). It is used only to fetch the bundled public/
    # data files — NOT for API calls (those go to WORKER_URL if set, or
    # directly to the provider for a visitor's own key).
    PAGE_BASE = str(mo.notebook_location()).rstrip("/") if IS_WASM else None
    return IS_WASM, PAGE_BASE, httpx, mo, os, uuid


@app.cell
def _():
    # HOST SETTING — paste your Cloudflare Worker URL here to enable a
    # DEFAULT API key for visitors (the key stays a Worker secret).
    # Leave "" for BYO-key-only: visitors paste their own key, which is
    # sent DIRECTLY to the provider and never touches the Worker.
    WORKER_URL = "https://cloudflare.acdryim.workers.dev"  
    # e.g. "https://my-worker.my-subdomain.workers.dev"
    return (WORKER_URL,)


@app.cell
async def _(IS_WASM, PAGE_BASE, WORKER_URL, fetch_server_config, mo):
    # In the browser, ask the Worker which providers hold a secret key and
    # what rate limit applies. Locally there is no server: this is None.
    server_config = await fetch_server_config()

    if IS_WASM and not WORKER_URL:
        server_status = mo.md(
            "***BYO-key only** — no Worker URL set. Visitors can paste their "
            "own API key (sent directly to the provider); no default key is "
            "available.*"
        )
    elif IS_WASM and server_config is not None and not server_config.get("ok"):
        # The Worker fetch failed — show the real reason (CORS vs network vs HTTP).
        err = server_config.get("error", "unknown error")
        hint = (
            " — this looks like a **CORS block**: add this page's origin "
            f"(`{PAGE_BASE}`) to `ALLOWED_ORIGINS` in `worker.js` and "
            "re-deploy the Worker."
            if server_config.get("cors")
            else " — check that the Worker is deployed and the URL is correct."
        )
        server_status = mo.callout(
            mo.md(f"**Worker unreachable** — `{err}`{hint}"),
            kind="danger",
        )
    elif IS_WASM:
        configured = [
            name
            for name, info in server_config.get("providers", {}).items()
            if info.get("configured")
        ]
        rl = server_config.get("rate_limit", {})
        server_status = mo.md(
            f"**Default key via Cloudflare Worker:** configured for "
            f"{', '.join(configured) or 'no providers'} · "
            f"rate limit {rl.get('chat_limit', '?')} chat / "
            f"{rl.get('models_limit', '?')} models per {rl.get('period', '?')}s "
            f"per visitor."
        )
    else:
        server_status = mo.md("*Local run: keys come from `.env`; no proxy needed.*")
    server_status
    return (server_config,)


@app.cell
def _(PROVIDERS, mo):
    # Optional: paste your own API key for ONE provider. It is sent
    # DIRECTLY to the provider from the browser (never through the Worker),
    # used only for the current request, and never stored or logged.
    byo_key_provider = mo.ui.dropdown(
        options=sorted(PROVIDERS.keys()),
        value="Ollama Cloud",
        label="Key for provider",
    )
    byo_key = mo.ui.text(
        label="Your own API key (optional)",
        kind="password",
        placeholder="sk-...",
        full_width=True,
    )

    mo.vstack([
        byo_key_provider,
        byo_key,
        mo.md(
            "**Privacy guarantee:** your key lives only in this browser tab's "
            "memory and is sent **directly to the provider** over HTTPS — it "
            "never touches the Cloudflare Worker, is **never stored or "
            "logged**, and disappears when you reload the page. It applies "
            "**only to the provider selected above**."
        ),
    ])
    return byo_key, byo_key_provider


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 0: Where can we send our question?

    An LLM **provider** is simply a company that rents out AI models over the internet.

    - Each provider has an internet address (`base_url`) — like a shop address.
    - Each provider needs its own secret password (`api_key_env`).
    - **Where do the keys come from?** Locally, from your `.env` file. In the
      exported web app, the host's keys are stored as Cloudflare Worker secrets
      (never shipped to the browser), and you can also paste your own key below
      (choose which provider it belongs to).
    - All providers below speak the same “OpenAI-style” language,
      so we can switch providers without rewriting our code.
    - **Google Gemini** is reached through Google's OpenAI-compatibility layer, so it
      needs no special code. It reuses `GOOGLE_API_KEY` — the same secret the rest of
      this project already uses — so if you have that set up, there is nothing new to do.
    """)
    return


@app.cell
def _():
    # A short menu of AI shops we can call. Keys are nicknames shown in the widget.
    PROVIDERS = {
        "Google Gemini": {
            # Google's OpenAI-compatibility layer speaks the same /models and
            # /chat/completions shape as the other shops, so nothing else changes.
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            # Reuses the repo-standard secret (see config.py / coding.py).
            "api_key_env": "GOOGLE_API_KEY",
            # Google lists embedding / image / video / live / audio / agentic /
            # music / robotics models on the same /models endpoint, but those
            # cannot answer a chat call — hide them.
            "exclude_model_fragments": (
                "embedding", "imagen", "image", "veo", "tts", "live",
                "transcribe", "lyria", "antigravity", "deep-research",
                "robotics", "computer-use", "omni", "nano-banana",
            ),
        },
        "Ollama Cloud": {
            "base_url": "https://ollama.com/v1",
            "api_key_env": "OLLAMA_API_KEY",
        },
        "OpenCode Go": {
            "base_url": "https://opencode.ai/zen/go/v1",
            "api_key_env": "OPENCODE_GO_API_KEY",
        },
    }

    # Preferred default model per provider, used to pre-select the model
    # dropdown when that model is present in the provider's model list.
    # (OpenCode Go's "Qwen3.8 Flash" is served as `qwen3.8-flash`.)
    DEFAULT_MODELS = {
        "Google Gemini": "gemini-3.5-flash-lite",
        "Ollama Cloud": "gpt-oss:120b",
        "OpenCode Go": "qwen3.8-flash",
    }
    return DEFAULT_MODELS, PROVIDERS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Are all providers reachable?**

    If your key is missing or a service is down, the button below tests
    every provider at once and lists their models. Useful for troubleshooting,
    but safe to skip.
    """)
    return


@app.cell
def _(mo):
    probe_button = mo.ui.run_button(label="Probe all providers")
    probe_button  # display the button
    return (probe_button,)


@app.cell
async def _(
    PROVIDERS,
    chat_models_for,
    cors_hint,
    fetch_models,
    key_route,
    mo,
    probe_button,
    resolve_key,
    server_config,
    validate_key,
):
    if not probe_button.value:
        probe_md = mo.md("*Click 'Probe all providers' to test reachability.*")
    else:
        sections = {}  # one collapsible section per provider
        for name, p in PROVIDERS.items():
            probe_key_source, key = resolve_key(name, server_config)
            probe_route = key_route(probe_key_source)
            if probe_route is None:
                sections[name] = mo.md(
                    f"SKIP — no API key (enter your own above, or set "
                    f"WORKER_URL for `{p['api_key_env']}`)"
                )
                continue
            try:
                # Some providers (Ollama Cloud, OpenCode Go) return model lists
                # to anyone, so a model list alone does NOT prove the key is
                # valid. Validate with a minimal chat call first.
                key_error = await validate_key(name, key, probe_route)
                if key_error is not None:
                    sections[name] = mo.md(
                        f"**FAIL — invalid API key** (no models listed): "
                        f"`{key_error}`"
                    )
                    continue
                probed = chat_models_for(
                    p, await fetch_models(name, key, probe_route)
                )
            except Exception as e:
                sections[name] = mo.md(
                    f"**FAIL** — `{type(e).__name__}: {e}`{cors_hint(e)}"
                )
                continue
            listing = "\n".join(sorted(probed)) if probed else "(none)"
            sections[name] = mo.vstack([
                mo.md(f"**{len(probed)} model(s)** — `{p['base_url']}`"),
                mo.md(f"```text\n{listing}\n```"),
            ])
        probe_md = mo.accordion(sections)
    probe_md  # display hints or the accordion of results
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Part 1 — Ask the AI one question

    **Step 1: Choose a provider** (which AI shop to call).
    If you are following the workshop, keep the default.
    """)
    return


@app.cell
def _(PROVIDERS, mo):
    # Drop-down menu of providers defined above (sorted for easier browsing).
    provider_name = mo.ui.dropdown(
        options=sorted(PROVIDERS.keys()),
        value="Ollama Cloud",
        label="Provider",
    )

    print("For example, use Ollama Cloud")

    provider_name  # display the widget
    return (provider_name,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Step 2: Choose a model and tune your question.**

    The model list updates automatically when you change the provider.
    """)
    return


@app.cell
async def _(
    DEFAULT_MODELS,
    IS_WASM,
    PROVIDERS,
    chat_models_for,
    fetch_models,
    key_route,
    mo,
    provider_name,
    resolve_key,
    server_config,
):
    # Fetch the model list for the selected provider.
    provider = PROVIDERS[provider_name.value]
    model_key_source, api_key = resolve_key(provider_name.value, server_config)
    model_route = key_route(model_key_source)
    models = []
    if model_route is not None:
        try:
            models = chat_models_for(
                provider, await fetch_models(provider_name.value, api_key, model_route)
            )
        except Exception:
            models = []

    # Model dropdown (sorted for easier browsing), pre-selecting the
    # provider's preferred default model when it is available.
    default_model = DEFAULT_MODELS.get(provider_name.value)
    model = mo.ui.dropdown(
        options=sorted(models),
        value=(
            default_model
            if default_model in models
            else (sorted(models)[0] if models else None)
        ),
        label="Model",
    )

    # Tuning widgets.
    temperature = mo.ui.slider(
        start=0.0, stop=2.0, step=0.1, value=1, label="Temperature"
    )
    max_tokens = mo.ui.number(
        start=1, stop=4096, step=1, value=512, label="Max tokens"
    )
    prompt = mo.ui.text_area(
        value="Explain what a marimo notebook is in one sentence.",
        label="Prompt",
        full_width=True,
    )

    if model_key_source is None:
        print(
            "No API key for this provider — enter your own key above, or set "
            "WORKER_URL."
        )
    elif model_key_source == "user":
        print(f"Using your own key for {provider_name.value} (direct to provider).")
    elif IS_WASM:
        print(f"Using the default key via the Cloudflare Worker for {provider_name.value}.")
    else:
        print(f"Using the local .env key for {provider_name.value}.")

    mo.vstack([model, temperature, max_tokens, prompt])
    return api_key, max_tokens, model, model_route, models, prompt, temperature


@app.cell
def _(mo):
    run_button = mo.ui.run_button(label="Run inference")
    run_button  # display the button
    return (run_button,)


@app.cell
async def _(
    api_key,
    chat_complete,
    cors_hint,
    max_tokens,
    mo,
    model,
    model_route,
    models,
    prompt,
    provider_name,
    run_button,
    temperature,
):
    # Three cases: not clicked yet / no model / ready to ask the AI.
    if not run_button.value:
        response_md = mo.md("*Click 'Run inference' to start.*")
    elif not models or not model.value:
        response_md = mo.md("*No model available — check provider / API key above.*")
    else:
        messages = [{"role": "user", "content": prompt.value}]  # chat-style envelope
        try:
            result = await chat_complete(
                provider_name=provider_name.value,
                api_key=api_key,
                route=model_route,
                model=model.value,
                messages=messages,
                temperature=temperature.value,
                max_tokens=max_tokens.value,
            )
            response_md = mo.md(
                f"**Response** ({provider_name.value} - {model.value}, "
                f"temperature {temperature.value}, "
                f"max_tokens {max_tokens.value}):\n\n{result}"
            )
        except Exception as e:
            response_md = mo.md(
                f"**ERROR:** `{type(e).__name__}: {e}`{cors_hint(e)}"
            )
    response_md  # display the answer or hint text
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ---

    ## Application of LLM Access via API:
    ## Summarizing and Classifying Crypto Exposure in SEC 10-K Filings

    **From one question to many documents.**
    In Part 1 you asked a single question by hand. Real research often means
    repeating the same judgment over *hundreds* of documents — too tedious to do manually.

    **Our example research task:**
    US listed firms file annual reports (Form 10-K) with financial statements and many notes to the statements. We pre-screened and extracted the notes likely to contain crypto-related keywords and ask an LLM to summarize each note, assign a crypto category,
    and score how material the crypto content is — like a tireless research assistant.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    **What happens next (roadmap):**

    1. Define the categories and the instruction (`CODING_PROMPT`) sent to the AI.
    2. Load the notes from a table file (`4MinExample_Notes.parquet` — think Excel for big data).
    3. Send each note to the AI, clean up the JSON answer, and save results to `4MinExample_Coded.parquet`.

    Output tokens are set to 4096 because reasoning models otherwise spend the budget on thinking and truncate the JSON. Each note gets up to 2 attempts (`CODING_MAX_ATTEMPTS`) with an escalating token budget.

    > **Note on Google Gemini:** its OpenAI-compatibility layer silently ignores request
    > parameters it does not implement, so a call can succeed while quietly dropping an
    > option. It also counts *thinking* tokens against `max_tokens` on Gemini 3.x models —
    > exactly the truncation risk the escalating retry above is designed to absorb.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Settings for the batch job: what to ask, and how

    - `NOTE_CATEGORIES` — the fixed labels the AI must choose from (like sorting mail into pigeonholes).
    - `CODING_PROMPT` — a detailed instruction with placeholders for each note’s title and text.
    - `MAX_OUTPUT_TOKENS`, `CODING_TEMPERATURE`, etc. — length, creativity, and speed controls.
      Beginners: you can leave these as-is; just notice they exist.
    """)
    return


@app.cell
def _():
    NOTE_CATEGORIES = [
        "custody",
        "trading/exchange",
        "payments/stablecoin",
        "tokenization/RWA",
        "blockchain-infrastructure",
        "mining/validator-infra",
        "investment/holding/treasury",
        "investment-products/etf",
        "risk/disclosure-only",
        "other",
    ]
    return (NOTE_CATEGORIES,)


@app.cell
def _():

    CODING_PROMPT = """You are a financial analyst summarizing crypto disclosures.
    For the given financial-statement note (title + text), return ONLY JSON:

    {{
      "summary": "<1-2 sentence meaningful summary of the nature of the note>",
      "relevant_excerpts": [
        "<verbatim short excerpt (max ~15 words) marking the START of a crypto-relevant passage>",
        "..."
      ],
      "category": "<one of: custody, trading/exchange, payments/stablecoin, tokenization/RWA, blockchain-infrastructure, mining/validator-infra, investment/holding/treasury, investment-products/etf, risk/disclosure-only, other>",
      "category_other": "<if category is 'other', a short free-text label for what this actually is; else empty string>",
      "crypto_extent": 0.00,
      "crypto_salience": 0.00,
      "materiality": 0.00,
      "reasoning": "<1 to 2 sentences explaining your materiality judgment, referencing extent and salience>"
    }}

    Field definitions:
    - relevant_excerpts: For each distinct passage in the note that discusses crypto/blockchain/
      digital-asset matters, quote the first ~10-15 words verbatim so the passage can be located in
      the source text. If crypto is mentioned in multiple separate places in the note (e.g., in both
      a fair-value section and a subsequent-events section), include one excerpt per location. If
      there is no genuine crypto-relevant content (e.g., only a boilerplate risk-factor mention),
      return an empty list.
    - category: Use "blockchain-infrastructure" for generic blockchain/DLT/smart-contract usage
      NOT tied to asset tokenization (e.g., internal record-keeping, supply-chain tracking). Use
      "tokenization/RWA" only when the note discusses tokenizing real-world or financial assets, or
      issuing security/digital tokens representing ownership or value. Use "investment-products/etf"
      for disclosures about bitcoin/ether ETFs, spot crypto ETPs, or crypto investment products
      offered/referenced by the firm, as distinct from "investment/holding/treasury" (the firm
      directly holding crypto assets on its own balance sheet). Use "mining/validator-infra" for crypto mining operations (hash rate, mining rigs, proof-of-work) and for protocol-level staking such as running validator nodes or infrastructure. Use "custody" for staking offered as a client-facing custodial service.
    - crypto_extent: What fraction of THIS note's substantive content concerns crypto-related
      matters, judged qualitatively by the depth and specificity of the crypto-relevant excerpts
      relative to the note's overall subject matter -- not by counting words. A short note that is
      entirely about crypto should score near 1.00 even though it is short. A long note where a
      substantial, detailed subsection is devoted to crypto should also score high, even if that
      subsection is a minority of the note's total length -- judge substantiveness, not proportion.
    - crypto_salience: Independent of how much of the note discusses crypto, how strategically
      central does the crypto activity described appear to be to the firm's business (e.g., a core
      product line vs. a passing mention of accepting crypto as one of several payment methods).
    - materiality: Your overall judgment of how significant this note is as a crypto disclosure,
      synthesizing crypto_extent and crypto_salience. A note can have high extent but low salience
      (e.g., a detailed but clearly peripheral disclosure) or vice versa (e.g., a brief but
      unambiguous statement that crypto is a strategic priority).

    Numerical scoring guidance (all continuous, 0.00-1.00, two decimal places):
    - crypto_extent: 0.00 = no substantive crypto content (name-drop only); 1.00 = the note is
      entirely or almost entirely about crypto matters, OR contains a detailed, self-contained
      section substantively devoted to crypto even if that section is a minority of the note's
      total length.
    - crypto_salience: 0.00 = crypto activity described is clearly incidental to the firm's
      business (e.g., one of many payment methods accepted); 1.00 = crypto activity described is a
      core strategic initiative or primary business line.
    - materiality: 0.00 = purely peripheral mention; 1.00 = core strategic initiative. Should
      reflect both crypto_extent and crypto_salience but is not a simple average of the two -- a
      note can be highly material on the strength of salience alone even with modest extent.

    Base your assessment only on the note text provided. Do not assume relevance from the note
    having been selected for review.

    NOTE TITLE: {title}
    NOTE TEXT (truncated {chars} chars):
    {body}
    """
    return (CODING_PROMPT,)


@app.cell
def _():

    CODING_NOTES_PARQUET = "4MinExample_Notes.parquet"  # input table of notes (bundled in public/)
    CODING_OUTPUT_PARQUET = "4MinExample_Coded.parquet"  # coded results (saved to public/ so exports bundle it)
    MAX_NOTE_CHARS = 262000  # truncate very long notes to fit the model
    # Gemini 3.x counts thinking + content tokens against max_tokens, so a modest cap
    # can truncate the JSON mid-response; code_note's doubling retry absorbs that.
    MAX_OUTPUT_TOKENS = 4096  # generous reply length so JSON is not cut off
    CODING_MAX_ATTEMPTS = 2  # retry once with doubled budget if parsing fails
    CODING_TEMPERATURE = 0.5  # a little creativity, but still consistent
    CODING_CONCURRENCY = 1 # 2  # 4  # Use 4 workers in parallel only for paid endpoints
    return (
        CODING_CONCURRENCY,
        CODING_MAX_ATTEMPTS,
        CODING_NOTES_PARQUET,
        CODING_OUTPUT_PARQUET,
        CODING_TEMPERATURE,
        MAX_NOTE_CHARS,
        MAX_OUTPUT_TOKENS,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Load the input table

    A **parquet file** is just a fast, compact spreadsheet for large datasets.
    Here each row = one note (firm `ticker` + `title` + full text).
    We hide the long `fullnote` column when previewing so the table stays readable.

    The file lives in `public/`, so the exported web app can fetch it from the
    same origin (no CORS).
    """)
    return


@app.cell
async def _(CODING_NOTES_PARQUET, IS_WASM, PAGE_BASE, fetch_bytes, mo):
    import pandas as pd  # standard table-handling toolbox
    import io  # read fetched bytes into a buffer

    if IS_WASM:
        # In the browser there is no filesystem: fetch the bundled parquet
        # from the page origin (public/ is copied into the export).
        notes_df = pd.read_parquet(
            io.BytesIO(
                await fetch_bytes(f"{PAGE_BASE}/public/{CODING_NOTES_PARQUET}")
            )
        )
    else:
        notes_df = pd.read_parquet(
            mo.notebook_dir() / "public" / CODING_NOTES_PARQUET
        )
    print(
        f"{len(notes_df)} notes | {notes_df['ticker'].nunique()} firms | "
        f"{CODING_NOTES_PARQUET}"
    )
    notes_df.drop(columns=["fullnote"])  # preview without the long text column
    return notes_df, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Cleaning and batch-sending: what the next code cell does

    LLMs sometimes add chatty wrappers (```json fences, thinking tags) around the JSON we asked for.
    The next cell therefore:

    - strips wrappers and fixes stray backslashes,
    - checks the category is one of our allowed labels and scores are 0–1,
    - retries with a bigger token budget if the answer is broken,
    - sends notes one-by-one (`llm_code_notes`) with a progress printout.

    You don’t need to memorize this — just know *why* it exists: to turn messy AI text into tidy table columns.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Choose the AI for the batch job

    The batch job uses the **same provider and model** you selected in Part 1.
    Change them there — both parts stay in sync automatically.
    """)
    return


@app.cell
def _(mo, model, provider_name):
    # The batch job uses the same provider/model widgets from Part 1.
    # Just display them again here for convenience.
    mo.vstack([
        mo.md("**Coding provider and model** (shared with Part 1)"),
        provider_name,
        model,
    ])  # display the shared widgets
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Run the batch coding and see results

    Click **Run LLM coding**. The notebook will:

    1. send each note to the chosen AI,
    2. save all answers to `4MinExample_Coded.parquet` (locally to `public/`;
       in the browser, a download button appears instead),
    3. show a short summary (how many notes, mean materiality, category counts)
       plus a preview table — new columns starting with `llm_` hold the AI’s work.

    While it runs, a progress bar (with rate and time estimate) and a streamed
    per-note log appear below — in the app view as well as the editor — so you can
    tell the job is still working. When it finishes, the log stays available in a
    collapsible section above the results table.
    """)
    return


@app.cell
def _(
    IS_WASM,
    PROVIDERS,
    key_route,
    mo,
    model,
    provider_name,
    resolve_key,
    server_config,
):

    # The batch job uses the same provider/model widgets from Part 1.
    # Just display the current selection status.
    coding_provider = PROVIDERS[provider_name.value]
    status_key_source, coding_api_key = resolve_key(provider_name.value, server_config)
    coding_route = key_route(status_key_source)

    if status_key_source is None:
        key_status = "MISSING — enter your own key above or set WORKER_URL"
    elif status_key_source == "user":
        key_status = "your own key (direct to provider)"
    elif IS_WASM:
        key_status = "default key via Cloudflare Worker"
    else:
        key_status = "local .env"

    mo.vstack([
        mo.md(
            f"**Coding provider:** `{provider_name.value}`  \n"
            f"**Coding model:** `{model.value}`  \n"
            f"**API key:** {key_status}"
        ),
    ])  # display current selection status

    run_coding = mo.ui.run_button(label="Run LLM coding")
    run_coding  # display the button
    return coding_api_key, coding_route, run_coding


@app.cell
async def _(
    coding_api_key,
    coding_route,
    mo,
    model,
    notes_df,
    provider_name,
    run_batch_coding,
    run_coding,
):
    if not run_coding.value:
        coding_output = mo.md(
            "*Click 'Run LLM coding' to summarize and classify the notes.*"
        )
    elif not model.value:
        coding_output = mo.md(
            "*No coding model selected — pick one in the coding parameters above.*"
        )
    else:
        coding_output = await run_batch_coding(
            notes_df=notes_df,
            provider_name=provider_name.value,
            api_key=coding_api_key,
            route=coding_route,
            model=model.value,
        )

    coding_output  # display hints, or summary + results table
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Takeaway

    You just saw the full pattern researchers reuse everywhere:

    **collect text → ask the AI with a clear instruction → clean the answers → save a coded table.**

    Try changing the Part 1 prompt, or the category list in Part 2, and re-run.
    That “tweak-and-re-run” loop is the core AI-assisted research skill from this workshop.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Behind the scenes: helper functions in the code cells below

    The next code cell defines two assistants (you never call them directly):

    - `fetch_models(...)` — asks “what AI models do you have today?”
    - `chat_complete(...)` — sends your prompt and returns the AI’s reply.

    Think of them as envelopes + postmen: they format the request,
    handle network hiccups, and unwrap the answer.
    """)
    return


@app.cell
def _(
    DEFAULT_MODELS,
    IS_WASM,
    PROVIDERS,
    WORKER_URL,
    byo_key,
    byo_key_provider,
    httpx,
    os,
    uuid,
):
    SESSION_ID = uuid.uuid4().hex  # random ID so the provider can group our calls
    USER_AGENT = "marimo-llm-example/0.1"  # polite name tag identifying our notebook

    # Turn an HTTP error into a short, readable message.
    def check_response(r: httpx.Response) -> None:
        if not r.is_error:
            return
        detail = r.text.strip()[:300] or "no response body"
        try:
            err = r.json().get("error")
            if isinstance(err, dict) and err.get("message"):
                detail = err["message"]
            elif isinstance(err, str):
                detail = err
        except Exception:
            pass
        raise RuntimeError(f"HTTP {r.status_code}: {detail}")

    # In the browser, POST a JSON payload to the Cloudflare Worker proxy
    # (which holds the provider secrets and enforces rate limits).
    async def _post_proxy(path: str, payload: dict, timeout: float = 60.0) -> dict:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(f"{WORKER_URL}{path}", json=payload)
        check_response(r)
        return r.json()

    # In the browser, ask the Worker which providers hold a secret key and
    # what rate limit applies. Locally there is no server: return None.
    async def fetch_server_config() -> dict | None:
        if not IS_WASM or not WORKER_URL:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{WORKER_URL}/api/config")
            check_response(r)
            return {"ok": True, **r.json()}
        except Exception as e:
            return {
                "ok": False,
                "error": str(e)[:200],
                "cors": cors_hint(e) != "",
            }

    # Which key should we use for a provider?
    #   ("user", key)   -> the visitor pasted their own key (memory only)
    #   ("server", "")  -> the Cloudflare Worker holds a secret (WASM) or the
    #                      local .env has one (local run)
    #   (None, "")      -> no key available
    def resolve_key(
        provider_name: str, server_config: dict | None
    ) -> tuple[str | None, str]:
        key = (byo_key.value or "").strip()
        # The visitor's key applies ONLY to the provider chosen in the
        # "Key for provider" dropdown — never to the other providers.
        if key and byo_key_provider.value == provider_name:
            return ("user", key)
        if IS_WASM:
            configured = bool(
                server_config
                and server_config.get("providers", {})
                .get(provider_name, {})
                .get("configured")
            )
            return ("server", "") if (WORKER_URL and configured) else (None, "")
        env_key = os.environ.get(PROVIDERS[provider_name]["api_key_env"], "")
        return ("server", env_key) if env_key else (None, "")

    # Which route should a request take?
    #   "direct" -> call the provider from the browser/local (visitor's own
    #               key, or a local .env key)
    #   "proxy"  -> call the Cloudflare Worker, which holds the secret
    #   None     -> no key available
    def key_route(key_source: str | None) -> str | None:
        if key_source is None:
            return None
        if key_source == "user":
            return "direct"
        return "proxy" if IS_WASM else "direct"

    # Friendly hint when a direct browser call fails due to CORS.
    def cors_hint(e: Exception) -> str:
        msg = str(e)
        if "Failed to fetch" in msg or "NetworkError" in msg or "CORS" in msg.upper():
            return (
                " (this provider may not allow direct browser calls — "
                "use the default key via the Worker, or check the provider's "
                "CORS policy)"
            )
        return ""

    # Verify a key actually works by making a minimal chat call. Some
    # providers (Ollama Cloud, OpenCode Go) return model lists to anyone,
    # so a model list alone does NOT prove the key is valid.
    async def validate_key(
        provider_name: str, api_key: str | None, route: str | None, timeout: float = 60.0
    ) -> str | None:
        model = DEFAULT_MODELS.get(provider_name)
        if not model:
            return "no default model to validate against"
        try:
            await chat_complete(
                provider_name=provider_name,
                api_key=api_key,
                route=route,
                model=model,
                messages=[{"role": "user", "content": "Reply with: OK"}],
                temperature=0.0,
                max_tokens=1,
                timeout=timeout,
            )
            return None
        except Exception as e:
            return str(e)[:200] + cors_hint(e)

    # Fetch raw bytes from a URL (used for the bundled parquet in the browser).
    async def fetch_bytes(url: str, timeout: float = 60.0) -> bytes:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url)
        check_response(r)
        return r.content

    # Ask a provider for its current model list.
    async def fetch_models(
        provider_name: str, api_key: str | None, route: str | None, timeout: float = 30.0
    ) -> list[str]:
        if route == "proxy":
            # In the browser, the Worker proxies the request (holds the secret).
            data = await _post_proxy(
                "/api/models",
                {"provider": provider_name, "api_key": api_key or None},
                timeout=timeout,
            )
            return [m["id"] for m in data.get("data", [])]
        # Direct: talk to the provider from the browser (visitor's own key)
        # or locally (.env key).
        provider = PROVIDERS[provider_name]
        headers = {"User-Agent": USER_AGENT}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"  # show password at the door
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(
                f"{provider['base_url'].rstrip('/')}/models", headers=headers
            )
        check_response(r)
        return [m["id"] for m in r.json().get("data", [])]

    # Keep only the models that can actually answer a chat call.
    # Some providers (e.g. Google) also list embedding / image / video / live
    # models on the same /models endpoint; those would fail on /chat/completions.
    def chat_models_for(provider: dict, model_ids: list[str]) -> list[str]:
        drop = tuple(
            f.lower() for f in provider.get("exclude_model_fragments", ())
        )
        if not drop:
            return list(model_ids)  # no filter configured -> list unchanged
        kept = []
        for mid in model_ids:
            name = str(mid)
            if name.startswith("models/"):  # native-style id -> bare id
                name = name[len("models/"):]
            if any(f in name.lower() for f in drop):
                continue
            kept.append(name)
        return kept or list(model_ids)  # never hand back an empty menu

    # Send one chat-style prompt and return the text answer.
    async def chat_complete(
        provider_name: str,
        api_key: str | None,
        route: str | None,
        model: str,
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: int = 512,
        timeout: float = 300.0,
    ) -> str:
        if route == "proxy":
            # In the browser, the Worker proxies the request (holds the secret).
            data = await _post_proxy(
                "/api/chat/completions",
                {
                    "provider": provider_name,
                    "api_key": api_key or None,
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "session_id": SESSION_ID,
                },
                timeout=timeout,
            )
            choices = data.get("choices", [])
            if not choices:
                return "[empty response: API returned no choices]"
            msg = choices[0].get("message", {})
            content = (msg.get("content") or "").strip()
            if content:
                return content
            # Some reasoning models spend the budget thinking; surface that thinking.
            reasoning = (
                msg.get("reasoning") or msg.get("reasoning_content") or ""
            ).strip()
            if reasoning:
                return (
                    "[no final answer: token budget spent on reasoning — "
                    "raise Max tokens]\n\n" + reasoning
                )
            return "[empty response: raise Max tokens?]"
        # Direct: talk to the provider from the browser (visitor's own key)
        # or locally (.env key).
        provider = PROVIDERS[provider_name]
        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        # Only OpenCode Go needs the session header. Sending it to other
        # providers breaks CORS preflight in the browser: Google only allows
        # "authorization,content-type", so a request carrying
        # x-opencode-session is blocked before it is sent.
        if provider_name == "OpenCode Go":
            headers["x-opencode-session"] = SESSION_ID
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        payload = {
            "model": model,
            "messages": messages,  # e.g. [{"role": "user", "content": "..."}]
            "temperature": temperature,  # creativity dial (low = factual)
            "max_tokens": max_tokens,  # max length of the reply
        }
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(
                    f"{provider['base_url'].rstrip('/')}/chat/completions",
                    json=payload,
                    headers=headers,
                )
        except httpx.ConnectError as e:
            raise RuntimeError(
                f"cannot reach {provider['base_url']} (network/DNS failure): {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise RuntimeError(
                f"no response from {provider['base_url']} after {timeout:.0f}s — "
                "large models can take minutes; "
                "retry or pick a faster model"
            ) from e
        check_response(r)
        choices = r.json().get("choices", [])
        if not choices:
            return "[empty response: API returned no choices]"
        msg = choices[0].get("message", {})
        content = (msg.get("content") or "").strip()
        if content:
            return content
        # Some reasoning models spend the budget thinking; surface that thinking.
        reasoning = (
            msg.get("reasoning") or msg.get("reasoning_content") or ""
        ).strip()
        if reasoning:
            return (
                "[no final answer: token budget spent on reasoning — "
                "raise Max tokens]\n\n" + reasoning
            )
        return "[empty response: raise Max tokens?]"

    return (
        chat_complete,
        chat_models_for,
        cors_hint,
        fetch_bytes,
        fetch_models,
        fetch_server_config,
        key_route,
        resolve_key,
        validate_key,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### More helper functions below:
    """)
    return


@app.cell
def _(
    CODING_CONCURRENCY,
    CODING_MAX_ATTEMPTS,
    CODING_OUTPUT_PARQUET,
    CODING_PROMPT,
    CODING_TEMPERATURE,
    IS_WASM,
    MAX_NOTE_CHARS,
    MAX_OUTPUT_TOKENS,
    NOTE_CATEGORIES,
    chat_complete,
    mo,
    pd,
):
    import asyncio  # run network calls efficiently
    import json  # parse the AI's JSON answer
    import re  # small text clean-ups with patterns

    # Remove <thought>...</thought> wrappers some models add.
    def thought_strip(text: str) -> str:
        return re.sub(
            r"<thought[\s\S]*?</thought>", "", text or "", flags=re.IGNORECASE
        ).strip()

    # Fix lone backslashes (e.g. \$) that would otherwise break JSON parsing.
    def repair_json_escapes(s: str) -> str:
        return re.sub(r"\\([^\"\\/bfnrtu])", r"\1", s)

    # Extract {...} from the reply and validate category + scores.
    def parse_coding_json(raw: str) -> dict:
        cand = thought_strip(raw or "").strip()
        cand = re.sub(r"^```(?:json)?\s*", "", cand.strip())  # drop opening fence
        cand = re.sub(r"\s*```$", "", cand.strip())  # drop closing fence
        start, end = cand.find("{"), cand.rfind("}")
        if start == -1 or end <= start:
            raise ValueError(f"Unparseable LLM JSON: {cand[:200]}")
        data = json.loads(repair_json_escapes(cand[start:end + 1]))
        cat = str(data.get("category", "other")).strip().lower()
        valid = {c.lower(): c for c in NOTE_CATEGORIES}  # allowed labels
        if cat not in valid:
            for k in valid:  # accept close variants, else fall back to "other"
                if k in cat or cat in k:
                    cat = k
                    break
            else:
                cat = "other"
        else:
            cat = valid[cat]
        return {
            "summary": str(data.get("summary", "")).strip(),
            "category": cat,
            "category_other": str(data.get("category_other", "")).strip(),
            "relevant_excerpts": data.get("relevant_excerpts", []),
            "crypto_extent": round(float(data.get("crypto_extent", 0) or 0), 2),
            "crypto_salience": round(float(data.get("crypto_salience", 0) or 0), 2),
            "materiality": round(
                float(data.get("materiality", data.get("score", 0)) or 0), 2
            ),
            "reasoning": str(data.get("reasoning", "")).strip(),
        }

    # Code one note: trim long text, ask the AI, retry with bigger budget if needed.
    async def code_note(
        row, *, provider_name, api_key, route, model, temperature, max_tokens
    ) -> dict:
        body = str(row.get("fullnote") or "").replace("\\$", "$")
        if len(body) > MAX_NOTE_CHARS:
            body = (
                body[: int(0.75 * MAX_NOTE_CHARS)]  # keep head ...
                + f"\n...[{len(body) - MAX_NOTE_CHARS} characters TRUNCATED]...\n"
                + body[-int(0.25 * MAX_NOTE_CHARS):]  # ... and tail
            )
        prompt = CODING_PROMPT.format(
            title=str(row.get("title", "")), body=body, chars=MAX_NOTE_CHARS
        )
        last_error = "no attempts made"
        for attempt in range(CODING_MAX_ATTEMPTS):
            budget = max_tokens * (2 ** attempt)  # double budget on retry
            try:
                raw = await chat_complete(
                    provider_name=provider_name,
                    api_key=api_key,
                    route=route,
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=budget,
                )
                parsed = parse_coding_json(raw)
                extent = parsed["crypto_extent"]
                salience = parsed["crypto_salience"]
                materiality = parsed["materiality"]
                nums_ok = all(
                    0.0 <= v <= 1.0 for v in (extent, salience, materiality)
                )
                return {
                    **row,
                    "llm_summary": parsed["summary"],
                    "llm_category": parsed["category"],
                    "llm_category_other": parsed["category_other"],
                    "llm_excerpts": parsed["relevant_excerpts"],
                    "llm_crypto_extent": extent,
                    "llm_crypto_salience": salience,
                    "llm_materiality": materiality,
                    "llm_reasoning": parsed["reasoning"],
                    "llm_model": model,
                    "scorer": f"llm:{model}",
                    "sanity_check": "" if nums_ok else "invalid",
                }
            except Exception as e:
                last_error = str(e)[:300]
                if attempt + 1 < CODING_MAX_ATTEMPTS:
                    print(
                        f"  retry {attempt + 2}/{CODING_MAX_ATTEMPTS} for "
                        f"{row.get('ticker', '?')} with max_tokens={budget * 2}: "
                        f"{last_error[:80]}",
                        flush=True,
                    )
                    await asyncio.sleep(3.0)
        # All attempts failed: keep the row, but mark it as an error.
        return {
            **row,
            "llm_summary": "",
            "llm_category": "other",
            "llm_category_other": "",
            "llm_excerpts": [],
            "llm_crypto_extent": 0.0,
            "llm_crypto_salience": 0.0,
            "llm_materiality": 0.0,
            "llm_reasoning": last_error,
            "llm_model": model,
            "scorer": "error",
            "sanity_check": "",
        }

    # Loop over all rows with limited parallelism (1 = one at a time, polite to free tiers).
    async def llm_code_notes(
        rows: list,
        *,
        provider_name: str,
        api_key: str,
        route: str | None,
        model: str,
        temperature: float,
        max_tokens: int,
        concurrency: int = 1,
        on_progress=None,
    ) -> list:
        sem = asyncio.Semaphore(max(1, int(concurrency)))
        total = len(rows)
        completed = 0

        async def _score(idx, row):
            nonlocal completed
            async with sem:
                print(
                    f"[{idx}/{total}] {row.get('ticker', '?')}: "
                    f"{str(row.get('title', ''))[:50]} ...",
                    flush=True,
                )
                coded = await code_note(
                    row,
                    provider_name=provider_name,
                    api_key=api_key,
                    route=route,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                completed += 1
                print(
                    f"  -> {coded['scorer']} materiality={coded['llm_materiality']}",
                    flush=True,
                )
                if on_progress is not None:
                    on_progress(completed, total, idx, row, coded)
                return coded

        return await asyncio.gather(
            *[_score(i + 1, row) for i, row in enumerate(rows)]
        )

    # Run the full batch coding job and return the output.
    async def run_batch_coding(
        notes_df,
        *,
        provider_name,
        api_key,
        route,
        model,
    ) -> mo.Html:
        """Run the batch coding job and return the output."""
        _records = notes_df.to_dict("records")
        _total = len(_records)
        _progress_log = []

        # Pre-compute per-ticker note counts for progress messages.
        _ticker_counts = notes_df["ticker"].value_counts().to_dict()
        _ticker_current = {}

        # Why this block is written the way it is (two marimo gotchas):
        #
        # 1. `with ... as _bar:` is required, not `_bar = mo.status.progress_bar(...)`.
        #    The context manager enters the progress bar and returns the updatable
        #    ProgressBar object; the bare constructor returns a wrapper that has no
        #    `.update()` method (AttributeError on the first progress callback).
        #
        # 2. `_on_progress` must be defined INSIDE the with-block, i.e. after `_bar`
        #    is bound. marimo mangles underscore-prefixed names at compile time: a
        #    reference to `_bar` that appears before its assignment in source order
        #    is treated as a "forward reference" and rewritten to
        #    `_cell_<cell-id>_bar`, which is never defined -> NameError on the first
        #    callback. Defining the closure after `_bar` keeps the name raw and lets
        #    it resolve as a normal Python closure.
        with mo.status.progress_bar(
            total=_total,
            title="LLM coding",
            subtitle=f"starting — {_total} notes",
            completion_title="LLM coding finished",
            remove_on_exit=False,
        ) as _bar:

            def _on_progress(done, total, idx, row, coded):
                ticker = row.get("ticker", "?")
                _ticker_current[ticker] = _ticker_current.get(ticker, 0) + 1
                note_num = _ticker_current[ticker]
                note_total = _ticker_counts.get(ticker, "?")
                _line = (
                    f"[{done}/{total}] **{ticker}** "
                    f"{str(row.get('title', ''))[:60]} — "
                    f"{coded['scorer']} · materiality={coded['llm_materiality']}"
                )
                _progress_log.append(_line)
                _bar.update(
                    subtitle=(
                        f"[{done}/{total}] {ticker} note {note_num}/{note_total}: "
                        f"{str(row.get('title', ''))[:60]}"
                    )
                )
                mo.output.append(mo.md(_line))

            try:
                coded_rows = await llm_code_notes(
                    _records,
                    provider_name=provider_name,
                    api_key=api_key,
                    route=route,
                    model=model,
                    temperature=CODING_TEMPERATURE,
                    max_tokens=MAX_OUTPUT_TOKENS,
                    concurrency=CODING_CONCURRENCY,
                    on_progress=_on_progress,
                )
            except Exception as _e:
                return mo.callout(
                    mo.md(
                        f"**LLM coding failed after {len(_progress_log)}/{_total} "
                        f"notes.**  \n`{type(_e).__name__}: {_e}`"
                    ),
                    kind="danger",
                )

        coded_df = pd.DataFrame(coded_rows)

        if IS_WASM:
            # In the browser there is no filesystem: offer the results as a
            # download instead of writing to disk.
            download_widget = mo.download(
                data=lambda: coded_df.to_parquet(index=False),
                filename=CODING_OUTPUT_PARQUET,
                mimetype="application/vnd.apache.parquet",
                label=f"Download {CODING_OUTPUT_PARQUET}",
            )
            print(
                f"results ready — click the download button to save "
                f"{CODING_OUTPUT_PARQUET}"
            )
        else:
            # Save to disk (public/ so exports bundle the fresh results).
            coded_path = mo.notebook_dir() / "public" / CODING_OUTPUT_PARQUET
            coded_df.to_parquet(coded_path, index=False)
            print(f"wrote {len(coded_df)} rows -> {coded_path}")
            download_widget = None

        # Make excerpts readable: list -> newline-separated text.
        display_df = coded_df.drop(columns=["fullnote"]).assign(
            llm_excerpts=lambda d: d["llm_excerpts"].apply(
                lambda v: "\n".join(map(str, v))
                if not isinstance(v, str) and hasattr(v, "__iter__")
                else str(v)
            )
        )

        # Small summary statistics for a quick sanity check.
        n_llm = int(coded_df["scorer"].astype(str).str.startswith("llm:").sum())
        n_invalid = int((coded_df["sanity_check"] == "invalid").sum())
        counts = coded_df["llm_category"].value_counts()
        counts_str = ", ".join(f"{k} ({v})" for k, v in counts.items())
        summary_md = mo.md(
            f"**{len(coded_df)} notes scored** via `{provider_name}` / "
            f"`{model}` — {n_llm} LLM, {len(coded_df) - n_llm} error, "
            f"{n_invalid} sanity-invalid.  \n"
            f"Saved to `{CODING_OUTPUT_PARQUET}`.  \n"
            f"Mean materiality **{coded_df['llm_materiality'].mean():.2f}**.  \n"
            f"**Categories:** {counts_str}"
        )

        _log_md = mo.md("\n\n".join(_progress_log) or "_no notes_")
        stack_items = [
            summary_md,
            mo.accordion({"Progress log (per note)": _log_md}),
            display_df,
        ]
        if download_widget is not None:
            stack_items.append(download_widget)
        return mo.vstack(stack_items)

    return (run_batch_coding,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ---

    ## Details about the **privacy guarantee** on the **BYO key method** for LLM access

    Here are the exact code lines a user can review (via **Show code**) to verify the BYO key is never stored and only ever goes directly to the provider. The evidence is a chain of four pieces:

    ### 1. The key is a browser-only widget — never written anywhere

    The BYO key cell (the "Your own API key" cell):

    ```python
    byo_key = mo.ui.text(
        label="Your own API key (optional)",
        kind="password",          # masked input
        placeholder="sk-...",
        full_width=True,
    )
    ```

    `mo.ui.text` is a marimo UI element — its value lives **only in the browser tab's memory**. There is no `open(...)`, no `write`, no `to_parquet` anywhere that touches `byo_key.value`. The only disk writes in the notebook are the LLM *results* parquet (`coded_df.to_parquet(...)`), which contain no key.

    ### 2. The key is scoped to one provider — never reused for others

    `resolve_key`:

    ```python
    def resolve_key(provider_name, server_config):
        key = (byo_key.value or "\").strip()
        # The visitor's key applies ONLY to the provider chosen in the
        # "Key for provider" dropdown — never to the other providers.
        if key and byo_key_provider.value == provider_name:
            return ("user", key)
        ...
    ```

    The user key is returned **only** for the provider selected in the dropdown. For every other provider, the code falls through to the server/`.env` branch — the user key is never sent to them.

    ### 3. The key is routed "direct" — never through the Worker

    `key_route`:

    ```python
    def key_route(key_source):
        if key_source is None:
            return None
        if key_source == "user":
            return "direct"          # ← user key → DIRECT to provider
        return "proxy" if IS_WASM else "direct"
    ```

    A `("user", key)` always gets route `"direct"`. The `"proxy"` route (which sends the key to the Cloudflare Worker) is only ever returned for `("server", ...)` keys — i.e., the host's secrets, never a visitor's.

    ### 4. The direct call puts the key only in the `Authorization` header to the provider's own URL

    `chat_complete` (direct path):

    ```python
    # Direct: talk to the provider from the browser (visitor's own key)
    # or locally (.env key).
    provider = PROVIDERS[provider_name]
    headers = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    # Only OpenCode Go needs the session header. ...
    if provider_name == "OpenCode Go":
        headers["x-opencode-session"] = SESSION_ID
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"   # ← key goes here
    ...
    r = await client.post(
        f"{provider['base_url'].rstrip('/')}/chat/completions",  # ← provider's URL
        json=payload,
        headers=headers,
    )
    ```

    The key appears in exactly one place: the `Authorization` header of a request to `provider['base_url']/chat/completions` — the provider's own endpoint. Same pattern in `fetch_models` (direct path): `Authorization` header to `provider['base_url']/models`.

    ### The contrast that proves it: `_post_proxy`

    ```python
    async def _post_proxy(path, payload, timeout=60.0):
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(f"{WORKER_URL}{path}", json=payload)
    ```

    This is the **only** function that sends anything to the Worker. It is called **only** when `route == "proxy"` — which, per `key_route`, happens **only for server keys**. A visitor's key can never reach `_post_proxy`, so it can never reach the Worker.

    ---

    **The one-line summary a user can verify by reading the code:** the key is read from a browser-only password widget (`byo_key`), scoped to one provider (`resolve_key`), forced onto the `"direct"` route (`key_route`), and placed only in the `Authorization` header of a request to the provider's own URL (`chat_complete`/`fetch_models`) — while the only code path that touches the Worker (`_post_proxy`) is unreachable for user keys.
    """)
    return


if __name__ == "__main__":
    app.run()
