<!-- <img src="img/BayesCityStGeorges_logoNoBkgd.png" alt="Bayes City St George's logo" style="float: right; width: 180px; margin: 0 0 1rem 1rem;" /> -->

![](img/BayesCityStGeorges_logoNoBkgd.png){fig-align="center" width="120%" alt="Bayes City St George's logo" style="float: right; width: 180px; margin: 0 0 1rem 1rem;"}


# Training Workshop on Data Science and AI Tools for Beginners

_**<span style="color:blue;">Held on</span>**_ 30 September 2026 · **Bayes Business School, City St George's, University of London**, 106 Bunhill Row, London **EC1Y 8TZ**

<!-- _(Note: See the **application procedure and deadline** at the bottom of this page.)_ -->

---

## What participants say


<style>
.testimonial-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}
.testimonial {
  background: rgba(128, 128, 128, 0.08);
  border-left: 4px solid #2a6fb0;
  border-radius: 6px;
  padding: 0.9rem 1.1rem;
  font-size: 0.95em;
}
.testimonial p { margin: 0 0 0.6rem 0; }
.testimonial .who { margin: 0; font-size: 0.85em; opacity: 0.7; }
details.testimonial-long {
  background: rgba(128, 128, 128, 0.08);
  border-left: 4px solid #2a6fb0;
  border-radius: 6px;
  padding: 0.6rem 1.1rem;
  margin: 0.6rem 0;
  font-size: 0.95em;
}
details.testimonial-long summary {
  cursor: pointer;
  font-weight: 600;
  list-style: none;
}
details.testimonial-long summary::-webkit-details-marker { display: none; }
details.testimonial-long summary::before {
  content: "+";
  display: inline-block;
  width: 1.2em;
  font-weight: 700;
  color: #2a6fb0;
}
details.testimonial-long[open] summary::before { content: "\2212"; }
details.testimonial-long p { margin: 0.7rem 0 0.3rem 0; }
details.testimonial-long .who { font-size: 0.85em; opacity: 0.7; }
</style>


<div class="testimonial-grid">

<div class="testimonial">
<p><i>Extremely well set up and helpful, would have liked more time on the day or spread over a day and a half</i></p>
</div>

<div class="testimonial">
<p><i>"It is a great opportunity to systematically get to know the basics of git, codespace, and AI-assisted coding</i> 😃<i>"</i></p>
</div>

<div class="testimonial">
<p><i>"The broad introduction to different coding platforms was very useful for beginners."</i></p>
</div>

<div class="testimonial">
<p><i>"I found the workshop very useful, especially as someone with no formal background in data science or AI. I appreciate the time and effort that went into making the workshop accessible for beginners."</i></p>
</div>

</div>


<details class="testimonial-long">
<summary><i>"The workshkop made me realise that coding, NLP and web crawling are not as difficult or inaccessible as they may initially seem. ...</i></summary>

_With the support of AI, and Dr Yim’s introduction to a range of useful tools and platforms, I felt as though I was “standing on the shoulders of giants” rather than starting from scratch. Most importantly, the workshop showed me that learning these skills is really about practice. I came away feeling much more confident that, with continued practice, I can learn to use these methods effectively in my own research."_
</details>

<details class="testimonial-long">
<summary><i>"I would definitely recommend joining the workshop, ...</i></summary>

_especially if you are a PhD student who is curious about data science, AI, or coding but has not had formal training in these areas. The workshop is beginner-friendly and gives you a chance to try the tools yourself rather than just learning about them in theory. It gave me the confidence to continue exploring them after the workshop. You do not need to be a computer scientist or have previous coding experience. Come with an open mind and think about one or two ways these tools might be useful for your own PhD."_
</details>

---

- **09:30-09:45 Arrival** 
  - Collect your name badge from a desk on G/F
  - Grab a coffee/tea and some pastries before the Workshop starts
- **09:45-11:00 GitHub ecosystem; Code examples in marimo**
  - Version control; Web scraping/crawling in action: handling bot detection/cookie banners, collecting URLs; Extracting pages from PDF (with OCR where needed)
  - 11:00-11:30 Morning coffee break
- **11:30-12:45 Getting AI assistance**
  - GitHub Copilot: inline autocompletion, Ask/Plan/Agent mode; Other agentic tools; Accessing LLMs via API
  - 12:45-13:45 Sandwich lunch
- **13:45-15:30 GPU-accelerated NLP**
  - Lightning.ai; Text analysis with stop words, lemmatization and bigrams, illustrated with risk factors in company filings
  - 15:30-16:00 Afternoon coffee break
- **16:00-17:45 R ecosystem; Q&A for your research**
  - Strengths of R; Identifying useful open-source packages (e.g., Polars)

---

## Why These Tools Matter

This workshop introduces a connected toolkit for modern research. Here's what you'll explore and how each piece fits together:

- **Python** — A beginner-friendly, general-purpose programming language and the backbone of most data science work. It's the language used to write web scrapers and crawlers, run NLP analyses, and build the demo code you'll see throughout the day.
- **R** — A language built specifically for statistics and data analysis. Many researchers use it alongside Python; learning both gives you flexibility depending on your discipline's conventions. 
- **GitHub Copilot** — An AI coding assistant inside VS Code/Codespaces. Beyond suggesting code as you type, it can answer questions, draft a plan for your idea, and carry out the plan for you. It lowers the barrier to writing Python/R by helping you self-learn syntax and troubleshoot, making it the ideal companion for beginners tackling the other tools on this list.
- **LLM access via API** — Calling a large language model from your own code, e.g., to summarise or categorise financial statement notes at scale. The Workshop includes a minimal example.
- **Web scraping** — The practice of automatically extracting data from websites, typically written in Python. It's often the first step in a research pipeline, feeding raw material (web pages, PDF reports) into later analysis. The Workshop addresses practical obstacles such as bot detection, cookie pop-ups and scanned PDFs that need optical character recognition (OCR).
- **Web crawling** — A related technique for systematically navigating and collecting pages across a website (rather than a single page), often used to locate the relevant documents before scraping the specific content you need.
- **Natural Language Processing (NLP)** — A field of techniques for analysing text data, frequently applied *after* scraping/crawling has collected raw material. Concepts like n-grams and lemmatization (below) are core NLP building blocks.
- **N-grams** — Sequences of adjacent words (or characters) used to capture patterns in text, a foundational technique within NLP for tasks like language modelling or text classification. The Workshop focuses on bigrams (word pairs) and bigram clouds.
- **Lemmatization** — The process of reducing words to their base/dictionary form (e.g., "running" → "run"), a common text pre-processing step in NLP that improves the accuracy of downstream analysis. It is computationally intensive, which is where GPU acceleration pays off.
- **marimo/Jupyter** — Jupyter is an interactive notebook environment for writing and running Python/R code alongside notes and outputs, widely used for exploratory data science and demos. marimo is a newer, reactive alternative to Jupyter, designed to make notebooks more robust and reproducible, addressing various limitations of Jupyter. The Workshop's main code examples are marimo notebooks.
- **VS Code** — A popular code editor that integrates with GitHub Copilot, Jupyter/marimo notebooks, and cloud environments like Codespaces, making it a natural hub for the whole workflow.
- **GitHub** — A platform for storing, sharing, and version-controlling code, and the account you'll need to access GitHub Copilot and Codespaces.
- **Codespaces** — GitHub's cloud-based development environment, letting you run VS Code, Python and your scraping/crawling code entirely in the browser, without installing anything locally.
- **Lightning.ai** — A cloud computing platform providing free-tier compute for running your code; especially useful when your laptop isn't powerful enough for certain data science or AI tasks.
- **Posit Cloud (RStudio)** — A cloud platform for running R in RStudio through your browser; used in the preliminary materials.

Together, these tools form a pipeline: **write and edit code (VS Code, marimo/Jupyter) → get AI assistance (GitHub Copilot, LLM APIs) → run it in the cloud (Codespaces, Lightning.ai, Posit Cloud) → collect data (web scraping/crawling, PDF extraction) → analyse it (NLP, n-grams, lemmatization) → manage and share it all (GitHub, Python/R)**.

![](img/GitHubEcosystem.png){fig-align="center" width="120%"}

---

## Training Workshop on Data Science and AI Tools for Beginners

### 30 September 2026

Curious about **Python**, **R**, **GitHub Copilot**, **web scraping**, natural language processing (NLP) or related tools/techniques — but haven't had a chance to try them out yet? Maybe you've also heard of tools/platforms like **Jupyter**, **marimo**, **VS Code**, **Codespaces**, **GitHub**, **Lightning.ai**, or techniques and concepts like **web crawling**, **n-grams**, **lemmatization** but they still feel a bit out of reach?

Then this *beginner-friendly, hands-on* workshop is for you! In just one day, you'll get to explore some of these tools and techniques that can facilitate your research. *No prior experience with Python or R is required* — but participants must complete the self-learning preliminaries before the workshop (see **Advance preparation** below).

Rather than teaching a programming language from the ground up, the workshop uses a *learn-by-doing* approach: we'll guide you through ready-made demo code that you can modify and experiment with, and show you how AI coding assistants (like GitHub Copilot) can act as your learning and research partner. By the end of the day, you'll have taken your first steps into using these tools to support your research.

### Workshop Arrangement

This one-day workshop is organised and delivered by [Dr Andrew Yim](https://www.bayes.citystgeorges.ac.uk/faculties-and-research/experts/andrew-yim), Bayes Business School, City St George's, University of London and supported by the Pathway and Thematic training funding from the SeNSS/SENSS Student Cohort Development Fund (SCDF). The workshop will be held in the Bayes Business School Building at 106 Bunhill Row, London EC1Y 8TZ. The nearest Underground stations are Old Street, Moorgate, and Barbican.

Attendees will have hands-on experience in using various data science and AI tools through cloud computing environments. They are required to:

- **Bring their own laptop**, fully charged, together with its power cable and charger (there are very limited plug sockets in the venue)
- Use a modern, **updated** browser (e.g., Chrome or Edge); **no other software installation** is needed
- Know in advance how to log on to the venue's WiFi via **Eduroam** on their laptop
- **Do the advanced preparation** described below

#### Advance preparation

**Accounts.** Sign up for **free-tier** accounts on the following platforms (**at least a week before** the workshop):

- [education.github.com/pack](https://education.github.com/pack)
  - Follow the sequence: Sign up for Student Developer Pack → Create an account → Sign up for GitHub (using school email address). Do **NOT** use the 'Continue with Google/Apple' options to sign up, because a school email address facilitates claiming GitHub Education benefits.
  - See details at [docs.github.com/en/education/about-github-education/github-education-for-students](https://docs.github.com/en/education/about-github-education/github-education-for-students)
- [lightning.ai/pricing](https://lightning.ai/pricing) (Follow the sequence: Get started free/Start free → (school) Email)
- [posit.cloud/plans/free](https://posit.cloud/plans/free) (free account, for the R exercises)

**Preliminary self-learning materials.** Registered participants will receive an email with the materials, which must be completed *prior to* the Workshop. The materials include:

- Workshop preliminaries (slides): why Python and R, notebooks, Markdown, and an end-to-end example of a data analysis workflow
- Setting up a GitHub account, the Copilot free tier, and a GitHub Codespace created from the Workshop repo
- A Jupyter notebook introducing essential Python commands
- Preparing RStudio on Posit Cloud, and an R Markdown notebook for generating result tables
- Setting up a Lightning.ai account

### Target Audience

This is a training workshop for beginners, with minimal to no prior experience, who see the relevance and importance of using data science tools for their research and using AI tools to self-learn/assist coding for research. Participants are expected to complete the preliminary self-learning materials beforehand, so that the Workshop can focus on applications. This workshop is **not** suitable for those who have already used most of the mentioned tools and techniques on a regular basis.

Priority will be given to **SENSS/SeNSS students** who can benefit most from the workshop. Unfilled places will be offered to unfunded students from **[SENSS/SeNSS institutions](https://www.senss.ac.uk/about)** and other ESRC funded Doctoral Training Partnerships (DTPs).

### Further Details

- **Places:** limited to a maximum of 25 attendees
- **Time:** begins 9:30am, finishes by 6:00pm on the scheduled date
- **Venue:** postcode EC1Y 8TZ
- **Cost:** free to registered participants (a sandwich lunch will be served); attendees cover their own travel and accommodation costs
- Registrants failing to attend the workshop may be blacklisted for future events held by the organiser

### Application

Please email a CV and a brief description about the below to Dr Andrew Yim ([a.yim@citystgeorges.ac.uk](mailto:a.yim@citystgeorges.ac.uk)) by the extended deadline on **17 September 2026**:

- Your research direction(s)
- Why data science and AI tools are important / relevant to your research
- Your expectation on how this workshop might benefit your research
- Your affiliation: (a) SENSS / (b) SeNSS / (c) unfunded students of SENSS/SeNSS institutions / (d) students of other ESRC funded Doctoral Training Partnerships (DTPs)
- Your year of study in PhD programme

**Acceptance notification will be sent by 18 September 2026. Online registration must be submitted by 21 September 2026.**
