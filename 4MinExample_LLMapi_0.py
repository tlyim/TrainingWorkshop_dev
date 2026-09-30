# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.28.1",
#     "marimo>=0.23.3",
#     "pandas>=3.0.6",
#     "pyarrow>=25.0.1",
#     "python-dotenv>=1.2.3",
# ]
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---

    ## Minimal Example: LLM Access via API

    **What is this notebook?**
    A 4-minute, hands-on demo of how to ask a large language model (LLM)
    to do research work *from Python code* — no chat website needed.

    **The big idea in one sentence:**
    Your Python code sends a question over the internet to an AI provider,
    and the provider sends back an answer — just like ordering food by delivery app.

    **This notebook has two parts:**

    - **Part 1 — Try it once:** pick a provider and model, type a prompt, click a button.
    - **Part 2 — Scale it up:** use the same technique to summarize and classify
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
    """)
    return


@app.cell
def _():
    import marimo as mo  # notebook helpers: text display + widgets
    import os  # read secret API keys from the environment
    import uuid  # create a random session ID for this run
    import httpx  # talk to websites/APIs over the internet
    from dotenv import load_dotenv

    # Load keys from the `.env` file in the notebook folder.
    load_dotenv(mo.notebook_dir() / ".env")
    return httpx, mo, os, uuid


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 0: Where can we send our question?

    An LLM **provider** is simply a company that rents out AI models over the internet.

    - Each provider has an internet address (`base_url`) — like a shop address.
    - Each provider needs its own secret password (`api_key_env`) stored in `.env`.
    - All providers below speak the same “OpenAI-style” language,
      so we can switch providers without rewriting our code.
    """)
    return


@app.cell
def _():
    # A short menu of AI shops we can call. Keys are nicknames shown in the widget.
    PROVIDERS = {
        "Ollama Cloud": {
            "base_url": "https://ollama.com/v1",
            "api_key_env": "OLLAMA_API_KEY",
        },
        "Groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "api_key_env": "GROQ_API_KEY",
        },
        "OpenCode Go": {
            "base_url": "https://opencode.ai/zen/go/v1",
            "api_key_env": "OPENCODE_GO_API_KEY",
        },
    }
    return (PROVIDERS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Behind the scenes: two helper messengers

    The next code cell defines two assistants (you never call them directly):

    - `fetch_models(...)` — asks “what AI models do you have today?”
    - `chat_complete(...)` — sends your prompt and returns the AI’s reply.

    Think of them as envelopes + postmen: they format the request,
    handle network hiccups, and unwrap the answer.
    """)
    return


@app.cell
def _(httpx, uuid):
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

    # Ask a provider for its current model list.
    async def fetch_models(
        base_url: str, api_key: str, timeout: float = 30.0
    ) -> list[str]:
        headers = {"User-Agent": USER_AGENT}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"  # show password at the door
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(
                f"{base_url.rstrip('/')}/models", headers=headers
            )
        check_response(r)
        return [m["id"] for m in r.json().get("data", [])]

    # Send one chat-style prompt and return the text answer.
    async def chat_complete(
        base_url: str,
        api_key: str,
        model: str,
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: int = 512,
        timeout: float = 300.0,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "x-opencode-session": SESSION_ID,
        }
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
                    f"{base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers=headers,
                )
        except httpx.ConnectError as e:
            raise RuntimeError(
                f"cannot reach {base_url} (network/DNS failure): {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise RuntimeError(
                f"no response from {base_url} after {timeout:.0f}s — "
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

    return chat_complete, fetch_models


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
    # Drop-down menu of providers defined above.
    provider_name = mo.ui.dropdown(
        options=list(PROVIDERS.keys()),
        value="Ollama Cloud",
        label="Provider",
    )

    print("For example, use Ollama Cloud")

    provider_name  # display the widget
    return (provider_name,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Step 2: Check the connection.**

    The next cell quietly looks up your secret key, asks the provider
    for its model list, and reports back:

    - `set` = key found, `MISSING` = check your `.env` file.
    - A number like “20 model(s) available” means the internet call worked.
    """)
    return


@app.cell
async def _(PROVIDERS, fetch_models, mo, os, provider_name):
    provider = PROVIDERS[provider_name.value]  # details of the chosen shop
    api_key = os.environ.get(provider["api_key_env"], "")  # secret password
    model_error = ""
    try:
        models = await fetch_models(provider["base_url"], api_key)
    except Exception as e:
        models = []
        model_error = f"{type(e).__name__}: {e}"
    lines = [
        f"**Base URL:** `{provider['base_url']}`  ",
        f"**API key:** {'set' if api_key else 'MISSING — set ' + provider['api_key_env']}",
    ]
    if model_error:
        lines.append(f"**Model list failed:** `{model_error}`")
    else:
        lines.append(f"**{len(models)} model(s) available**")
    status = mo.md("\n\n".join(lines))
    status  # display the status box
    return api_key, models, provider


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Step 3: Tune your question.**

    - **Model** — which AI brain to use (names/codes come from the provider).
    - **Temperature** — creativity: 0 = strict and factual, 2 = wild and random.
      For research, keep it low.
    - **Max tokens** — maximum reply length (a token ≈ half of a word).
    - **Prompt** — your question in plain English. Try editing it!
    """)
    return


@app.cell
def _(mo, models):
    model = mo.ui.dropdown(
        options=models,
        value=models[0] if models else None,
        label="Model",
    )
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
    widgets = mo.vstack([model, temperature, max_tokens, prompt])

    print("For example, use Ollama Cloud: gpt-oss:120b")

    widgets  # display all four input boxes stacked vertically
    return max_tokens, model, prompt, temperature


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Step 4: Run it.**

    Click **Run inference** (“inference” just means “ask the AI”).
    The answer appears in the next cell. Nothing runs until you click —
    so you can change the prompt first without cost or hurry.
    """)
    return


@app.cell
def _(mo):
    run_button = mo.ui.run_button(label="Run inference")
    run_button  # display the button
    return (run_button,)


@app.cell
async def _(
    api_key,
    chat_complete,
    max_tokens,
    mo,
    model,
    models,
    prompt,
    provider,
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
                base_url=provider["base_url"],
                api_key=api_key,
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
            response_md = mo.md(f"**ERROR:** `{type(e).__name__}: {e}`")
    response_md  # display the answer or hint text
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Optional: are all providers reachable?**

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
async def _(PROVIDERS, fetch_models, mo, os, probe_button):
    if not probe_button.value:
        probe_md = mo.md("*Click 'Probe all providers' to test reachability.*")
    else:
        sections = {}  # one collapsible section per provider
        for name, p in PROVIDERS.items():
            key = os.environ.get(p["api_key_env"], "")
            if not key:
                sections[name] = mo.md(f"SKIP — no API key (`{p['api_key_env']}`)")
                continue
            try:
                probed = await fetch_models(p["base_url"], key)
            except Exception as e:
                sections[name] = mo.md(f"**FAIL** — `{type(e).__name__}: {e}`")
                continue
            listing = "\n".join(probed) if probed else "(none)"
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

    CODING_NOTES_PARQUET = "4MinExample_Notes.parquet"  # input table of notes
    CODING_OUTPUT_PARQUET = "4MinExample_Coded.parquet"  # where coded results are saved
    MAX_NOTE_CHARS = 262000  # truncate very long notes to fit the model
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
    """)
    return


@app.cell
def _(CODING_NOTES_PARQUET):
    import pandas as pd  # standard table-handling toolbox

    notes_df = pd.read_parquet(CODING_NOTES_PARQUET)  # read rows into a DataFrame
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


@app.cell
def _(
    CODING_MAX_ATTEMPTS,
    CODING_PROMPT,
    MAX_NOTE_CHARS,
    NOTE_CATEGORIES,
    chat_complete,
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
        row, *, base_url, api_key, model, temperature, max_tokens
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
                    base_url=base_url,
                    api_key=api_key,
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
        base_url: str,
        api_key: str,
        model: str,
        temperature: float,
        max_tokens: int,
        concurrency: int = 1,
    ) -> list:
        sem = asyncio.Semaphore(max(1, int(concurrency)))

        async def _score(idx, row):
            async with sem:
                print(
                    f"[{idx}/{len(rows)}] {row.get('ticker', '?')}: "
                    f"{str(row.get('title', ''))[:50]} ...",
                    flush=True,
                )
                coded = await code_note(
                    row,
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                print(
                    f"  -> {coded['scorer']} materiality={coded['llm_materiality']}",
                    flush=True,
                )
                return coded

        return await asyncio.gather(
            *[_score(i + 1, row) for i, row in enumerate(rows)]
        )

    return (llm_code_notes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Choose the AI for the batch job

    Same idea as Part 1, but you can change to a different model for the full coding run.
    """)
    return


@app.cell
def _(PROVIDERS, mo):
    # Drop-down for the batch-coding provider (independent from Part 1).
    coding_provider_name = mo.ui.dropdown(
        options=list(PROVIDERS.keys()),
        value="Ollama Cloud",
        label="Coding provider",
        searchable=True,
        full_width=True,
    )
    coding_provider_name  # display the widget
    return (coding_provider_name,)


@app.cell
async def _(PROVIDERS, coding_provider_name, fetch_models, mo, os):
    coding_provider = PROVIDERS[coding_provider_name.value]
    coding_api_key = os.environ.get(coding_provider["api_key_env"], "")

    coding_models = []  # fill with live model list, or leave empty on error
    coding_model_error = ""
    try:
        coding_models = await fetch_models(
            coding_provider["base_url"], coding_api_key
        )
    except Exception as e:
        coding_model_error = f"{type(e).__name__}: {e}"

    coding_model = mo.ui.dropdown(
        options=coding_models,
        value=coding_models[0] if coding_models else None,
        label="Coding model",
        searchable=True,
        full_width=True,
    )

    mo.vstack([
        mo.md(
            f"**Coding key:** "
            f"{'set' if coding_api_key else 'MISSING — set ' + coding_provider['api_key_env']}"
            + (
                f"\n\n**Model list failed:** `{coding_model_error}`"
                if coding_model_error
                else ""
            )
        ),
        coding_model,
    ])  # display key status + model menu stacked vertically
    return coding_api_key, coding_model, coding_provider


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Run the batch coding and see results

    Click **Run LLM coding**. The notebook will:

    1. send each note to the chosen AI,
    2. save all answers to `4MinExample_Coded.parquet`,
    3. show a short summary (how many notes, mean materiality, category counts)
       plus a preview table — new columns starting with `llm_` hold the AI’s work.
    """)
    return


@app.cell
def _(mo):
    run_coding = mo.ui.run_button(label="Run LLM coding")
    run_coding  # display the button
    return (run_coding,)


@app.cell
async def _(
    CODING_CONCURRENCY,
    CODING_OUTPUT_PARQUET,
    CODING_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
    coding_api_key,
    coding_model,
    coding_provider,
    coding_provider_name,
    llm_code_notes,
    mo,
    notes_df,
    pd,
    run_coding,
):
    if not run_coding.value:
        coding_output = mo.md(
            "*Click 'Run LLM coding' to summarize and classify the notes.*"
        )
    elif not coding_model.value:
        coding_output = mo.md(
            "*No coding model selected — pick one in the coding parameters above.*"
        )
    else:
        # Send all notes to the LLM (this is the slow, API-calling step).
        coded_rows = await llm_code_notes(
            notes_df.to_dict("records"),
            base_url=coding_provider["base_url"],
            api_key=coding_api_key,
            model=coding_model.value,
            temperature=CODING_TEMPERATURE,
            max_tokens=MAX_OUTPUT_TOKENS,
            concurrency=CODING_CONCURRENCY,
        )
        coded_df = pd.DataFrame(coded_rows)

        # Save to disk so results persist after the notebook closes.
        coded_path = mo.notebook_dir() / CODING_OUTPUT_PARQUET
        coded_df.to_parquet(coded_path, index=False)
        print(f"wrote {len(coded_df)} rows -> {coded_path}")

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
            f"**{len(coded_df)} notes scored** via `{coding_provider_name.value}` / "
            f"`{coding_model.value}` — {n_llm} LLM, {len(coded_df) - n_llm} error, "
            f"{n_invalid} sanity-invalid. "
            f"Mean materiality **{coded_df['llm_materiality'].mean():.2f}**.  \n"
            f"**Categories:** {counts_str}"
        )

        coding_output = mo.vstack([summary_md, display_df])

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


if __name__ == "__main__":
    app.run()
