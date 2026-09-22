# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.23.3",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:24px;">
      <div>
        <h1>Training Workshop on Data Science and AI Tools for Beginners</h1>
        <p><strong>30 September 2026 · Bayes Business School, City St George's, University of London</strong></p>
      </div>
      <img
        src="public/BayesCityStGeorge's_logoNoBkgd.png"
        alt="Bayes City St George's logo"
        style="width:160px; height:auto; object-fit:contain;"
      />
    </div>
    """
    )
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <!--
    # Training Workshop on Data Science and AI Tools for Beginners

    **30 September 2026 · Bayes Business School, City St George's, University of London**
    -->

    ## Why These Tools Matter

    This workshop introduces a connected toolkit for modern research. Here's what you'll explore and how each piece fits together:

    - **Python** — A beginner-friendly, general-purpose programming language and the backbone of most data science work. It's the language used to write web scrapers, run NLP analyses, and build the demo code you'll see throughout the day.
    - **R** — A language built specifically for statistics and data analysis. Many researchers use it alongside Python; learning both gives you flexibility depending on your discipline's conventions.
    - **GitHub Copilot** — An AI coding assistant that suggests code as you type. It lowers the barrier to writing Python/R by helping you self-learn syntax and troubleshoot, making it the ideal companion for beginners tackling the other tools on this list.
    - **Web scraping** — The practice of automatically extracting data from websites, typically written in Python. It's often the first step in a research pipeline, feeding raw text into later NLP analysis.
    - **Web crawling** — A related technique for systematically navigating and collecting pages across a website (rather than a single page), often used to gather large datasets before scraping extracts the specific content you need.
    - **Natural Language Processing (NLP)** — A field of techniques for analysing text data, frequently applied *after* scraping/crawling has collected raw material. Concepts like n-grams and lemmatization (below) are core NLP building blocks.
    - **N-grams** — Sequences of adjacent words (or characters) used to capture patterns in text, a foundational technique within NLP for tasks like language modelling or text classification.
    - **Lemmatization** — The process of reducing words to their base/dictionary form (e.g., "running" → "run"), a common text pre-processing step in NLP that improves the accuracy of downstream analysis.
    - **marimo/Jupyter** — Jupyter is an interactive notebook environment for writing and running Python/R code alongside notes and outputs, widely used for exploratory data science and demos. marimo is a newer, reactive alternative to Jupyter, designed to make notebooks more robust and reproducible, addressing various limitations of Jupyter.
    - **VS Code** — A popular code editor that integrates with GitHub Copilot, Jupyter notebooks, and cloud environments like Codespaces, making it a natural hub for the whole workflow.
    - **GitHub** — A platform for storing, sharing, and version-controlling code, and the account you'll need to access GitHub Copilot and Codespaces.
    - **Codespaces** — GitHub's cloud-based development environment, letting you run VS Code, Python/R, and your scraping/NLP code entirely in the browser, without installing anything locally.
    - **Lightning.ai** — A cloud computing platform providing free-tier compute for running your code, useful when your laptop isn't powerful enough for larger data science or AI tasks.

    Together, these tools form a pipeline: **write and edit code (VS Code, Jupyter/marimo) → get AI assistance (GitHub Copilot) → run it in the cloud (Codespaces, Lightning.ai) → collect data (web scraping/crawling) → analyse it (NLP, n-grams, lemmatization) → manage and share it all (GitHub, Python/R)**.

    ---

    ## Training Workshop on Data Science and AI Tools for Beginners

    ### 30 September 2026

    Curious about **Python**, **R**, **GitHub Copilot**, **web scraping**, natural language processing (NLP) or related tools/techniques — but haven't had a chance to try them out yet? Maybe you've also heard of tools/platforms like **Jupyter**, **marimo**, **VS Code**, **Codespaces**, **GitHub**, **Lightning.ai**, or techniques and concepts like **web crawling**, **n-grams**, **lemmatization** but they still feel a bit out of reach?

    Then this *beginner-friendly, hands-on* workshop is for you! In just one day, you'll get to explore some of these tools and techniques that can facilitate your research. *No prior experience with Python or R is required* — just curiosity and a willingness to try something new!

    We'll guide you through with demo code and show you how AI coding assistants (like GitHub Copilot) can help you along the way. By the end of the day, you'll have taken your first steps into using these tools to support your research.

    ### Workshop Arrangement

    This one-day workshop is organised and delivered by [Dr Andrew Yim](#), Bayes Business School, City St George's, University of London and supported by the Pathway and Thematic training funding from the SeNSS/SENSS Student Cohort Development Fund (SCDF). Attendees are required to **bring their own laptops**. The workshop will be held in the Bayes Business School Building at 106 Bunhill Row, London.

    Attendees will have hands-on experience in using various data science and AI tools through cloud computing environments. They are required to do advanced preparation, including signing up for **free-tier** accounts on the following platforms (**at least a week before** the workshop):

    - [education.github.com/pack](https://education.github.com/pack)
      - Follow the sequence: Sign up for Student Developer Pack → Create an account → Sign up for GitHub (using school email address). Do **NOT** use the 'Continue with Google/Apple' options to sign up, because a school email address facilitates claiming GitHub Education benefits.
      - See details at [docs.github.com/en/education/about-github-education/github-education-for-students](https://docs.github.com/en/education/about-github-education/github-education-for-students)
    - [lightning.ai/pricing](https://lightning.ai/pricing) (Follow the sequence: Get started free/Start free → (school) Email)

    ### Target Audience

    This is a training workshop for beginners, with minimal to no prior experience, who see the relevance and importance of using data science tools for their research and using AI tools to self-learn/assist coding for research. This is **not** suitable for those who have already used the mentioned tools and techniques on a regular basis.

    Priority will be given to **SENSS/SeNSS students** who can benefit most from the workshop. Unfilled places will be offered to unfunded students from **SENSS/SeNSS institutions**: [senss.ac.uk/about](https://www.senss.ac.uk/about).

    ### Further Details

    - **Places:** limited to a maximum of 40 attendees
    - **Time:** begins 9:30am, finishes by 6:30pm on the scheduled date
    - **Venue postcode:** EC1Y 8TZ
    - **Cost:** free to registered participants (a sandwich lunch will be served); attendees cover their own travel and accommodation costs
    - Registrants failing to attend the workshop may be blacklisted for future events held by the organiser

    ### Application

    Please email a CV and a brief description about the below to Dr Andrew Yim ([a.yim@citystgeorges.ac.uk](mailto:a.yim@citystgeorges.ac.uk)) by the deadline on **31 August 2026**:

    - Your research direction(s)
    - Why data science and AI tools are important / relevant to your research
    - Your expectation on how this workshop might benefit your research
    - Your affiliation: (a) SENSS / (b) SeNSS / (c) unfunded students of SENSS/SeNSS institutions
    - Your year of study in PhD programme

    **Acceptance notification will be sent by 14 September 2026.**
    """)
    return


if __name__ == "__main__":
    app.run()
