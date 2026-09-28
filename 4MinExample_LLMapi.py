import marimo

__generated_with = "0.24.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---

    ## Minimum Example: LLM Access via API
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell
def _():
    import marimo as mo
    import os
    import uuid
    import httpx
    from dotenv import load_dotenv

    load_dotenv()
    return httpx, mo, os, uuid


@app.cell
def _():
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


@app.cell
def _(httpx, uuid):
    SESSION_ID = uuid.uuid4().hex
    USER_AGENT = "marimo-llm-example/0.1"

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

    async def fetch_models(
        base_url: str, api_key: str, timeout: float = 30.0
    ) -> list[str]:
        headers = {"User-Agent": USER_AGENT}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(
                f"{base_url.rstrip('/')}/models", headers=headers
            )
        check_response(r)
        return [m["id"] for m in r.json().get("data", [])]

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
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
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


@app.cell
def _(PROVIDERS, mo):
    provider_name = mo.ui.dropdown(
        options=list(PROVIDERS.keys()),
        value="Ollama Cloud",
        label="Provider",
    )
    provider_name
    return (provider_name,)


@app.cell
async def _(PROVIDERS, fetch_models, mo, os, provider_name):
    provider = PROVIDERS[provider_name.value]
    api_key = os.environ.get(provider["api_key_env"], "")
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
    status
    return api_key, models, provider


@app.cell
def _(mo, models):
    model = mo.ui.dropdown(
        options=models,
        value=models[0] if models else None,
        label="Model",
    )
    temperature = mo.ui.slider(
        start=0.0, stop=2.0, step=0.1, value=0.1, label="Temperature"
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
    widgets
    return max_tokens, model, prompt, temperature


@app.cell
def _(mo):
    run_button = mo.ui.run_button(label="Run inference")
    run_button
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
    if not run_button.value:
        response_md = mo.md("*Click 'Run inference' to start.*")
    elif not models or not model.value:
        response_md = mo.md("*No model available — check provider / API key above.*")
    else:
        messages = [{"role": "user", "content": prompt.value}]
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
    response_md
    return


@app.cell
def _(mo):
    probe_button = mo.ui.run_button(label="Probe all providers")
    probe_button
    return (probe_button,)


@app.cell
async def _(PROVIDERS, fetch_models, mo, os, probe_button):
    if not probe_button.value:
        probe_md = mo.md("*Click 'Probe all providers' to test reachability.*")
    else:
        results = []
        for name, p in PROVIDERS.items():
            key = os.environ.get(p["api_key_env"], "")
            if not key:
                results.append(f"SKIP ({name}): no API key")
                continue
            try:
                probed_models = await fetch_models(p["base_url"], key)
                sample = ", ".join(probed_models[:3]) if probed_models else "none"
                results.append(
                    f"OK ({name}): {len(probed_models)} models — {sample}"
                )
            except Exception as e:
                results.append(f"FAIL ({name}): {type(e).__name__}: {e}")
        probe_md = mo.md("\n".join(f"- {r}" for r in results))
    probe_md
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---

    ## Application of LLM Access via API:
    ## Summarizing and Classifying Crypto Exposure in SEC 10-K Filings
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    Read the extracted notes from a single parquet file, then summarize and classify each note with selected provider/model. Output tokens are set to 4096 because reasoning models otherwise spend the budget on thinking and truncate the JSON. Each note gets up to 2 attempts (`RETRY_MAX_ATTEMPTS`) with an escalating token budget.
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


    #CODING_YEAR = 2021
    CODING_NOTES_PARQUET = "results/notes/parquet_2021-2021_top700.parquet"
    MAX_NOTE_CHARS = 262000
    MAX_OUTPUT_TOKENS = 4096
    CODING_MAX_ATTEMPTS = 2
    CODING_TEMPERATURE = 0.5
    CODING_CONCURRENCY = 1  # 4

    return (
        CODING_CONCURRENCY,
        CODING_MAX_ATTEMPTS,
        CODING_NOTES_PARQUET,
        CODING_PROMPT,
        CODING_TEMPERATURE,
        MAX_NOTE_CHARS,
        MAX_OUTPUT_TOKENS,
        NOTE_CATEGORIES,
    )


@app.cell
def _(CODING_NOTES_PARQUET):
    import pandas as pd

    notes_df = pd.read_parquet(CODING_NOTES_PARQUET)
    #notes_df = notes_df[notes_df["dl_year"] == CODING_YEAR].reset_index(drop=True)
    print(
        f"{len(notes_df)} notes | {notes_df['ticker'].nunique()} firms | "
        f"{CODING_NOTES_PARQUET}"
    )
    notes_df.drop(columns=["fullnote"])
    return notes_df, pd


@app.cell
def _(
    CODING_MAX_ATTEMPTS,
    CODING_PROMPT,
    MAX_NOTE_CHARS,
    NOTE_CATEGORIES,
    chat_complete,
):
    import asyncio
    import json
    import re

    def thought_strip(text: str) -> str:
        return re.sub(
            r"<thought[\s\S]*?</thought>", "", text or "", flags=re.IGNORECASE
        ).strip()

    def repair_json_escapes(s: str) -> str:
        return re.sub(r"\\([^\"\\/bfnrtu])", r"\1", s)

    def parse_coding_json(raw: str) -> dict:
        cand = thought_strip(raw or "").strip()
        cand = re.sub(r"^```(?:json)?\s*", "", cand.strip())
        cand = re.sub(r"\s*```$", "", cand.strip())
        start, end = cand.find("{"), cand.rfind("}")
        if start == -1 or end <= start:
            raise ValueError(f"Unparseable LLM JSON: {cand[:200]}")
        data = json.loads(repair_json_escapes(cand[start:end + 1]))
        cat = str(data.get("category", "other")).strip().lower()
        valid = {c.lower(): c for c in NOTE_CATEGORIES}
        if cat not in valid:
            for k in valid:
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

    async def code_note(
        row, *, base_url, api_key, model, temperature, max_tokens
    ) -> dict:
        body = str(row.get("fullnote") or "").replace("\\$", "$")
        if len(body) > MAX_NOTE_CHARS:
            body = (
                body[: int(0.75 * MAX_NOTE_CHARS)]
                + f"\n...[{len(body) - MAX_NOTE_CHARS} characters TRUNCATED]...\n"
                + body[-int(0.25 * MAX_NOTE_CHARS):]
            )
        prompt = CODING_PROMPT.format(
            title=str(row.get("title", "")), body=body, chars=MAX_NOTE_CHARS
        )
        last_error = "no attempts made"
        for attempt in range(CODING_MAX_ATTEMPTS):
            budget = max_tokens * (2 ** attempt)
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


@app.cell
def _(mo):
    run_coding = mo.ui.run_button(label="Run LLM coding")
    run_coding
    return (run_coding,)


@app.cell
async def _(
    CODING_CONCURRENCY,
    CODING_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
    api_key,
    llm_code_notes,
    mo,
    model,
    notes_df,
    pd,
    provider,
    provider_name,
    run_coding,
):
    if not run_coding.value:
        coding_output = mo.md(
            "*Click 'Run LLM coding' to summarize and classify the notes.*"
        )
    else:
        coded_rows = await llm_code_notes(
            notes_df.to_dict("records"),
            base_url=provider["base_url"],
            api_key=api_key,
            model=model.value,
            temperature=CODING_TEMPERATURE,
            max_tokens=MAX_OUTPUT_TOKENS,
            concurrency=CODING_CONCURRENCY,
        )
        coded_df = pd.DataFrame(coded_rows)
        preview_cols = [
            "ticker",
            "company_name",
            "title",
            "llm_summary",
            "llm_category",
            "llm_crypto_extent",
            "llm_crypto_salience",
            "llm_materiality",
            "llm_reasoning",
            "sanity_check",
        ]
        n_llm = int(coded_df["scorer"].astype(str).str.startswith("llm:").sum())
        n_invalid = int((coded_df["sanity_check"] == "invalid").sum())
        counts = coded_df["llm_category"].value_counts()
        counts_str = ", ".join(f"{k} ({v})" for k, v in counts.items())
        summary_md = mo.md(
            f"**{len(coded_df)} notes scored** via `{provider_name.value}` / "
            f"`{model.value}` — {n_llm} LLM, {len(coded_df) - n_llm} error, "
            f"{n_invalid} sanity-invalid. "
            f"Mean materiality **{coded_df['llm_materiality'].mean():.2f}**.  \n"
            f"**Categories:** {counts_str}"
        )
        coding_output = mo.vstack([summary_md, coded_df[preview_cols]])
    coding_output
    return


if __name__ == "__main__":
    app.run()
