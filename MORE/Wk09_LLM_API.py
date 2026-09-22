import marimo

__generated_with = "0.24.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### __Note__

    * To initialise a Jupyter notebook (.ipynb file) in Codespaces simply double-click the file from the Explorer panel.
    * There is no equivalent to the marimo button to 'convert' the notebook.  The notebook is primed and ready for you to select the kernel.
    * To complete the initialisation, select a kernel in the top right of the main coding panel. Select an option which says 'Python' and either says 'Global env' next to it or is starred (e.g., "Python 3.12.1").
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## __Week 9: Introduction to programmatic prompting using LLM APIs__
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We first need to import several functions that we will use below.
    This includes importing the groq package which allows us to access the __GroqCloud__ platform which includes several LLM APIs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### __Imports packages__
    """)
    return


@app.cell
def _():
    # Imports all the relevant packages required

    import time
    import os
    import pandas as pd
    import numpy as np

    from groq import Groq
    import json
    from IPython.display import display

    return Groq, display, json, os, pd, time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### __A simple LLM API call__
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    * Accessing an LLM API can be relatively simple - just a few lines of code!

    * It should be noted that each LLM API has a slightly different setup.

    * The following example uses a very simple prompt using the API from the GroqCloud platform which offers access to several types of models (e.g., llama, GPT, Qwen). In this case, we use a llama model.
    """)
    return


@app.cell
def _(Groq, os):
    # Creates a Groq API client using your API key stored in GitHub Secrets
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Starts a request to the Groq API to generate a "chat completion" (LLM response)
    # It specifies the model to use for the completion (here, the Llama 3.1 8B Instant model).
    # Sets the prompt: a single message from the user asking the model to explain Tobin’s q.
    # Closes the API call
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Explain Tobin's q in one sentence."}]
    )

    # Prints the model’s response (the answer to the prompt) to the notebook output
    print(completion.choices[0].message.content)
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    However, this is a trivial example. In practice, additional code needs to be added to deal with several complexities. For example:
    * Specifying model __parameters__ (like top_p, temperature)
    * Running the prompt in a __loop__ to run the same prompt for multiple firms
    * Adapting a prompt to insert a __dynamic elements__ to the promopt (e.g., firm-specific information)
    * __Chaining__ together tasks
    * Adding __few-shot examples__
    * Managing inputs and outputs so that model __quotas__ are not breached
    * Managing __cost__
    * Logging __status__ updates / __debugging__ information

    .... as well as:
    * Data preparation
    * Error correction
    * Formating, checking and saving output.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### __File and folder management__
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Before we start setting up the prompt, we do some 'housekeeping' to specify the input files we will use, as well as the anmes of the output files we will generate.

    We __set each file and folder name to be a variable__, which we reference in the code below.

    These are explicitly created upfront so that they are easy to find, rather than having to look deep in the code.
    """)
    return


@app.cell
def _(os):
    # Assigning folder references
    cwd = os.getcwd()                        # current working directory
    public_dir = 'public'
    llm_dir = 'llm'

    # Firm-level forward-looking sentences (fls) file
    flspkl_filename = 'fls_sent.pkl'
    flspkl_path = os.path.join(cwd, public_dir, llm_dir, flspkl_filename)

    # Sentiment classification few-shot examples files
    pos_filename = 'positive_examples.txt'
    neg_filename = 'negative_examples.txt'
    neu_filename = 'neutral_examples.txt'

    pos_filepath = os.path.join(cwd, public_dir, llm_dir, pos_filename)
    neg_filepath = os.path.join(cwd, public_dir, llm_dir, neg_filename)
    neu_filepath = os.path.join(cwd, public_dir, llm_dir, neu_filename)

    # Output files
    output_pkl_filename = 'sentOutput.pkl'
    output_pkl_path = os.path.join(cwd, public_dir, llm_dir, output_pkl_filename)

    output_csv_filename = 'sentOutput.csv'
    output_csv_path = os.path.join(cwd, public_dir, llm_dir, output_csv_filename)
    return (
        flspkl_path,
        neg_filepath,
        neu_filepath,
        output_csv_filename,
        output_csv_path,
        output_pkl_filename,
        output_pkl_path,
        pos_filepath,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### __Load sample data__
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    * Lets have a look at our sample of nine firms from the UK FTSE.

    * The forward-looking sentences have been extracted from each firm's annual reports for 2024.
    * The data is stored in a __pickle file__

    Advantages of pickle files:

    * Can store complex Python objects (lists, dicts, DataFrames, custom classes) easily.
    * Fast to save and load compared to text formats.
    * Maintains Python object structure and types.
    * Useful for caching, saving intermediate results, or transferring data between Python programs.
    * Have unlimited storage capacity 'per cell', unlike formats like .CSV, .XLSX
    """)
    return


@app.cell
def _(display, flspkl_path, pd):
    # Loads firm-level data including forward-looking sentences

    cols_text = ['company_name', 'year', 'forward_looking_sentences']
    tot_sample = list(range(9))

    def load_sample(flspkl_path, sample, cols):
        df = pd.read_pickle(flspkl_path)
        return (
            df[cols]
            .iloc[sample]
            .reset_index(drop=True)
            .copy()
        )

    # Display the names of all the companies in the sample
    df_co = load_sample(flspkl_path, tot_sample, cols_text)
    for name in df_co['company_name'].unique():
        print(name)

    # Displays forward-looking sentences for 3 of the companies in the sample, without truncating the text
    eg_co = [0, 7, 8]
    df_dis = load_sample(flspkl_path, eg_co, cols_text)
    pd.set_option('display.max_colwidth', None)
    display(df_dis)
    pd.reset_option('display.max_colwidth')
    return load_sample, tot_sample


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### __Load few-shot examples__
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    * We learned in Week 8, the value of few-shot examples to guide/ train the LLM
    * These examples are stored in a structured input file, and need to be loaded into memory before they can be used by the scipt and loaded into each prompt
    """)
    return


@app.cell
def _(neg_filepath, neu_filepath, pos_filepath):
    # Creates helper to load the examples
    def load_sentences(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    # Maps example lists and their corresponding filepaths
    examples = {
        'positive_examples': pos_filepath,
        'neutral_examples':  neu_filepath,
        'negative_examples': neg_filepath,
    }

    # Loads all examples
    examples_dict = {}

    for example, filepath in examples.items():
        examples_dict[example] = load_sentences(filepath)

    # Extracts into separate lists
    positive_examples = examples_dict['positive_examples']
    neutral_examples  = examples_dict['neutral_examples']
    negative_examples = examples_dict['negative_examples']

    # Prints sample of training data
    print(f"{positive_examples}\n")
    print(f"{neutral_examples}\n")
    print(f"{negative_examples}\n")
    return negative_examples, neutral_examples, positive_examples


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### __Task: Classify forward-looking sentences__
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### ***Specifies user-defined functions***
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To chunk up the functionality of the code, we define several user-defined functions.

    These are defined in the next code cell, before being called by the workflow in the cell below that.

    Here, in summary, is what each one does:

    * __retrieve_apikey()__: This looks into your computer's hidden settings to find your private password (API key) for the AI service.

    * __normalise_forward_sentences()__: This cleans up the data, ensuring that whether a sentence is in a list or one long block of text, it gets turned into a clean list of individual sentences.

    * __sentiment_to_score()__: A simple translator that turns words into numbers (e.g., "positive" becomes $1$, "negative" becomes $-1$).

    * __extract_json_from_response()__: The AI often returns a lot of "chatter"; this function cuts through the noise to find the specific data table (JSON) we asked for.

    * __label_from_mean_score()__: This takes the final average number and decides if the firm, overall, is "positive" (score above 0.25), "negative" (below -0.25), or "neutral.

    * __build_prompt_for_sentences()__: This writes the "instructions" for the AI, including "few-shot" examples (teaching by example) to show it how we want it to think.

    * __classify_sentences_for_firm()__: This is the "messenger" that sends the sentences to the AI, waits for an answer, and tries again if the internet connection drops.

    * __process_firm_row()__: The "manager" function that coordinates the cleaning, classifying, and averaging for one single company.
    """)
    return


@app.cell
def _(
    MODEL_NAME,
    ast,
    client,
    json,
    negative_examples,
    neutral_examples,
    os,
    pd,
    positive_examples,
    time,
):
    # This cell contains the functions required in the rest of this notebook

    # ---------------------------------------------------------
    # Retrieves the API key
    # ---------------------------------------------------------

    def retrieve_apikey(key_name: str) -> str:
        """
        Retrieve an API key directly from environment variables (GitHub Secrets).

        Parameters
        ----------
        key_name : str
            Name of the secret/environment variable (e.g., 'GROQ_API_KEY').

        Returns
        -------
        str
            The API key value.

        Raises
        ------
        KeyError
            If the secret is not found in the environment.
        """
        # Direct lookup in the environment variables
        api_key = os.environ.get(key_name)

        if not api_key:
            raise KeyError(
                f"The secret '{key_name}' was not found. "
                "Make sure it is added to your 'Codespaces secrets' in GitHub settings "
                "and that you have restarted your Codespace to apply changes."
            )

        return api_key

    # ---------------------------------------------------------
    # Text normalisation
    # ---------------------------------------------------------

    def normalise_forward_sentences(cell):
        """
        Ensure we always work with a clean list[str] of forward-looking sentences.
        Handles:
          - list of strings
          - stringified list (e.g. "['a', 'b']")
          - single long string with newlines
        """
        if isinstance(cell, list):
            return [str(s).strip() for s in cell if str(s).strip()]

        if isinstance(cell, str):
            text = cell.strip()
            # Try to interpret as a Python list first
            if text.startswith("[") and text.endswith("]"):
                try:
                    parsed = ast.literal_eval(text)
                    if isinstance(parsed, list):
                        return [str(s).strip() for s in parsed if str(s).strip()]
                except Exception:
                    pass
            # Fallback: split on newlines
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            return lines

        # Anything else: treat as empty
        return []

    # ---------------------------------------------------------
    # Converts sentiment labels to scores (1, 0, -1)
    # ---------------------------------------------------------

    def sentiment_to_score(sentiment: str) -> int:
        """
        Map sentence-level sentiment label to numeric score.
        Defaults to 0 if label is missing/unknown.
        """
        if not isinstance(sentiment, str):
            return 0

        s = sentiment.strip().lower()
        mapping = {"positive": 1, "neutral": 0, "negative": -1}
        return mapping.get(s, 0)


    # ---------------------------------------------------------
    # Labels the mean sentence-level sentiment scores 
    # ---------------------------------------------------------

    def label_from_mean_score(mean_score: float) -> str:
        """
        Map the firm-level mean sentiment score to a categorical label.
        """
        if mean_score >= 0.25:
            return "positive"
        if mean_score <= -0.25:
            return "negative"
        return "neutral"


    # ---------------------------------------------------------
    # Extracts the JSON from the response
    # ---------------------------------------------------------

    def extract_json_from_response(text: str):
        """
        Extract a JSON object from the model response text.
        Assumes the first '{' starts the JSON.
        """
        if not isinstance(text, str):
            raise ValueError("Model response is not text.")

        # If the model wrapped JSON in ```json ... ``` fences, strip them
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        # Find the first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No valid JSON object found in model response.")

        json_str = text[start : end + 1]
        return json.loads(json_str)


    # ---------------------------------------------------------
    # Build the classification prompt for a single firm
    # ---------------------------------------------------------

    def build_prompt_for_sentences(sentences):
        """
        Build a prompt instructing the model to classify each forward-looking
        sentence as positive, neutral, or negative, while also providing a 
        brief rationale for each classification.
        """
        few_shot_block = []

        few_shot_block.append("POSITIVE EXAMPLES (forward-looking, sentiment = positive):")
        for s in positive_examples:
            few_shot_block.append(f"- {s} | sentiment: positive")

        few_shot_block.append("")
        few_shot_block.append("NEGATIVE EXAMPLES (forward-looking, sentiment = negative):")
        for s in negative_examples:
            few_shot_block.append(f"- {s} | sentiment: negative")

        few_shot_block.append("")
        few_shot_block.append("NEUTRAL EXAMPLES (forward-looking, sentiment = neutral):")
        for s in neutral_examples:
            few_shot_block.append(f"- {s} | sentiment: neutral")

        few_shot_text = "\n".join(few_shot_block)

        sentences_block = []
        for idx, sent in enumerate(sentences, start=1):
            sentences_block.append(f"{idx}. {sent}")

        sentences_text = "\n".join(sentences_block)

        prompt = f"""
    You are an expert in analysing forward-looking statements made by UK-listed companies in their annual reports.

    ## Task
    For each of the forward-looking sentences below, classify the sentiment as:
      - "positive"
      - "neutral"
      - "negative"

    For each sentence, you must:
      - Carefully consider the tone, direction, and implications.
      - Provide a brief rationale (in less than 15 words) explaining why the sentence has that sentiment, focusing on expectations, direction, and strength of language.

    ## Few-shot examples
    The following examples illustrate how to classify forward-looking sentences by sentiment:

    {few_shot_text}

    ## Output format
    Return ONLY a JSON object with this exact structure:

    {{
      "sentences": [
        {{
          "index": 1,
          "sentiment": "positive" | "neutral" | "negative",
          "rationale": "a brief explanation of why this sentiment label and score are appropriate"
        }},
        ...
      ]
    }}

    Do NOT include any additional keys outside this structure. Do NOT add commentary outside the JSON object.

    ## Sentences to classify
    {sentences_text}
        """.strip()

        return prompt

    # ---------------------------------------------------------
    # Call Groq to classify sentences for a single firm
    # ---------------------------------------------------------

    def classify_sentences_for_firm(sentences, max_retries=3, retry_sleep=2.0):
        """
        Given a list of forward-looking sentences for one firm, query the Groq API
        (model: openai/gpt-oss-120b) and return:
          - a list of integer scores (1, 0, -1) aligned with the input order; and
          - a list of rationales aligned with the same order.
        """
        if not sentences:
            return [], []

        prompt = build_prompt_for_sentences(sentences)

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                chat_completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    top_p=1,
                )

                raw_text = chat_completion.choices[0].message.content
                parsed = extract_json_from_response(raw_text)

                items = parsed.get("sentences", [])
                scores_by_index = {}
                rationales_by_index = {}

                for item in items:
                    try:
                        idx = int(item.get("index"))

                        # --- NEW: map label -> score in Python ---
                        sent_label = item.get("sentiment", "")
                        score = sentiment_to_score(sent_label)

                        # keep rationale from the model
                        rationale = item.get("rationale", "")

                        scores_by_index[idx] = score
                        rationales_by_index[idx] = str(rationale)

                    except Exception:
                        # If parsing fails for one item, skip it.
                        continue

                # Align scores and rationales to original sentence order.
                aligned_scores = []
                aligned_rationales = []
                for i in range(1, len(sentences) + 1):
                    aligned_scores.append(scores_by_index.get(i, 0))
                    aligned_rationales.append(rationales_by_index.get(i, ""))

                return aligned_scores, aligned_rationales

            except Exception as e:
                last_error = e
                print(f"Error calling Groq on attempt {attempt}: {e}")
                if attempt < max_retries:
                    time.sleep(retry_sleep)

        # If all retries fail, fall back to neutral scores and empty rationales.
        print(
            "All attempts to classify sentences for this firm failed. "
            "Defaulting to neutral (0) for all sentences and empty rationales."
        )
        return [0] * len(sentences), [""] * len(sentences)

    # ---------------------------------------------------------
    # Processes data to generate firm-level sentiment scores
    # ---------------------------------------------------------

    def process_firm_row(row):
        """
        For a single row (firm), classify each forward-looking sentence and
        compute the firm-level mean sentiment and label.
        Returns a Series with new columns, including sentence-level rationales.
        """
        sentences = normalise_forward_sentences(row.get("forward_looking_sentences"))
        if not sentences:
            mean_score = 0.0
            label = label_from_mean_score(mean_score)
            return pd.Series(
                {
                    "sentence_sentiment_scores": [],
                    "sentence_sentiment_rationales": [],
                    "firm_mean_sentiment": mean_score,
                    "firm_sentiment_label": label,
                }
            )

        scores, rationales = classify_sentences_for_firm(sentences)
        if not scores:
            mean_score = 0.0
        else:
            mean_score = sum(scores) / float(len(scores))

        label = label_from_mean_score(mean_score)

        return pd.Series(
            {
                "sentence_sentiment_scores": scores,
                "sentence_sentiment_rationales": rationales,
                "firm_mean_sentiment": mean_score,
                "firm_sentiment_label": label,
            }
        )

    return process_firm_row, retrieve_apikey


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### ***Executes workflow incorporating user-defined functions***
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    __STEP 1. Initialisation and Security__
    * __Secure Authentication__: The script begins by calling retrieve_apikey() to fetch your credentials.
    * This ensures your private keys aren't hard-coded (written plainly) in the script - which is a security risk (someone could intercept your API key).

    * __Model Configuration__: We define how "strict" the AI should be.

    MODEL_NAME = "openai/gpt-oss-120b"
    TEMPERATURE = 0

    Ensures the AI creates deterministic outcomes


    __STEP 2. The Main Processing Loop__ (firm-by-firm)

    For each firm, the following sequence occurs:
     * __Data Preparation__: We pass the raw data into ___normalise_forward_sentences()___ to ensure the text is in a format the AI can digest.
     * __The "Manager" Call__: The script triggers ___process_firm_row()___, which acts as the conductor for the following sub-steps:
        * ___Construct the Request___: The script calls ___build_prompt_for_sentences()___. This creates a string that includes the instructions and the specific sentences for that company.
        * ___API Communication___: The ___classify_sentences_for_firm()___ function is called. This sends the prompt and handles any technical "hiccups.
        * ___Advanced Note___: This function uses a for attempt in range(1, max_retries + 1): loop. This is a "robustness" feature; if the server is busy, it waits and tries again rather than crashing.

    * __Data Extraction__: Once the AI replies, the script uses ___extract_json_from_response()___ to isolate the data table from the AI's conversational text.


    __STEP 3. Scoring and Aggregation__

    Once the AI provides the labels (e.g., "positive"), we turn that into something which can be processed numerically:
    * __Numerical Mapping__: For every sentence, ___sentiment_to_score()___ is applied:

    Pythonmapping = {"positive": 1, "neutral": 0, "negative": -1}

    * __Firm-Level Averaging__: We calculate the mean. If a company has three sentences from the scores.

    * __Final Categorisation__: We call ___label_from_mean_score()___ to give the company a final overall sentiment score based on that average:

    e.g. if mean_score >= 0.25: return "positive"

    A threshold of 0.25 chosen to ensure that firms who's sentences are close to 0, are not included as positive.
    This ensures that only firms who's sentences are score greater than zero are labelled as "positive".


    __STEP 4. Data Export__

    * __Merging__: All new columns (Scores, Rationales, and Mean Sentiment) are combined with the original data.
    * __Saving__: The final dataframe is saved in two formats:CSV: For viewing in Excel. Pickle: A Python-specific format.
    """)
    return


@app.cell
def _(
    Groq,
    display,
    flspkl_path,
    load_sample,
    negative_examples,
    neutral_examples,
    output_csv_filename,
    output_csv_path,
    output_pkl_filename,
    output_pkl_path,
    pd,
    positive_examples,
    process_firm_row,
    retrieve_apikey,
    tot_sample,
):
    # ---------------------------------------------------------
    # Loads source data - firm-level forward-looking sentences
    cols = ['company_name', 'year', 'forward_looking_sentences']
    df2 = load_sample(flspkl_path, tot_sample, cols)
    api_key = retrieve_apikey('GROQ_API_KEY')
    if not api_key:
        raise ValueError('GROQ_API_KEY not found in environment variables.')
    client_1 = Groq(api_key=api_key)
    # Groq configuration
    MODEL_NAME = 'openai/gpt-oss-120b'
    generation_config = {'temperature': 0, 'top_p': 1}
    TEMPERATURE = 0.0
    TOP_P = 1.0
    positive_examples_1 = positive_examples
    negative_examples_1 = negative_examples
    neutral_examples_1 = neutral_examples
    results = []
    n = len(df2)
    for i, (idx, row) in enumerate(df2.iterrows(), start=1):
        out = process_firm_row(row)
        results.append(out)
        print(f'Processed firm {i} of {n}')
    sentiment_results = pd.DataFrame(results).set_index(df2.index)
    df_out = pd.concat([df2, sentiment_results], axis=1)
    df_out['firm_mean_sentiment'] = df_out['firm_mean_sentiment'].astype(str).str.strip().replace('', pd.NA)
    df_out['firm_mean_sentiment'] = pd.to_numeric(df_out['firm_mean_sentiment'], errors='coerce')
    # Few-shot examples [10 per class]
    df_out.to_pickle(output_pkl_path)
    df_out.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(df_out.shape)
    cols_out = ['company_name', 'year', 'sentence_sentiment_scores', 'firm_mean_sentiment', 'firm_sentiment_label']
    df_out2 = df_out[cols_out]
    display(df_out2)
    # Applies to the dataframe: runs the helpers to generate sentence-level and firm-level sentiment
    # Save outputs (pickle + CSV)
    print(f"Sentiment classification complete. Data saved to '{output_pkl_filename}' and '{output_csv_filename}'.")
    return (MODEL_NAME,)


if __name__ == "__main__":
    app.run()
