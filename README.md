# Energy Conflict — Leipzig Corpus

Part of the [Reimagining Sites of Energy Conflict](https://github.com/digbmc/energyconflict) project (Prof. Carol Hager, Bryn Mawr LITS Digital Scholarship).

## What this repo does

This repo pulls year-by-year German-language corpus data from the
[Leipzig Corpora Collection](https://wortschatz.uni-leipzig.de/en/download)
and searches it for mentions of three German nuclear energy conflict sites —
**Wyhl**, **Kalkar**, and **Wackersdorf** — along with related keywords
(WAA, Wiederaufarbeitungsanlage, Kernkraftwerk, Atomkraftwerk, Schneller
Brüter, Jahrestag, Mahnwache, Demonstration).

The goal is to see:
- How often each site is mentioned, year by year
- Whether the three sites are mentioned *together* in the same sentence
  (single hits → pairs → all three)
- Eventually, whether mentions cluster around anniversaries, protests, or
  policy events

## Do we need an API key?

**No.** The Leipzig Corpora Collection's yearly corpus files are freely
downloadable with no account or authentication
(see [usage terms](https://wortschatz.uni-leipzig.de/en/usage)). We are using
the **1M-sentence** German news corpus for each year from 1990–2020.

There is a separate Wortschatz web service (SOAP-based `Sentences` API) that
also requires no key for normal use, but it queries their *general* corpus
rather than a specific year — so it isn't the right tool for year-by-year
analysis, and we aren't using it here. If we ever need more than 1M
sentences for a single year, Leipzig asks that we contact them directly
rather than use that API — see `docs/pseudocode.md` for details.

## Repo structure

```
energy-conflict-leipzig/
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   └── pseudocode.md       # step-by-step logic, in plain English
├── src/
│   ├── fetch_corpus.py     # downloads one year's corpus file
│   └── search_keywords.py  # searches a downloaded corpus for keywords
├── data/                   # downloaded corpus files (NOT committed — see .gitignore)
└── output/                 # CSV results (small samples OK to commit)
```

## Setup

1. Clone this repo and `cd` into it.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage — one-year prototype

```bash
# Step 1: download one year's corpus (example: 2010)
python src/fetch_corpus.py --year 2010

# Step 2: search that year's corpus for our keywords
python src/search_keywords.py --year 2010
```

This produces `output/hits_2010.csv` — a table of every sentence that
matched one or more of our keywords, with the keyword(s) matched, the
sentence text, the sentence ID, and the corpus/year it came from.

## Important: don't commit the raw corpus

The full downloaded corpus files are large and (per the project's private
corpus note) should **not** be pushed to GitHub. The `data/` folder is
already excluded via `.gitignore`. Only the `output/` CSVs (our derived
results) should be committed.

## Status

- [x] Repo created
- [x] Pseudocode/documentation written
- [x] Confirmed no API key needed; identified correct data source (yearly
      downloadable corpora, not the general Sentences web service)
- [ ] One-year prototype tested end-to-end
- [ ] Co-occurrence (pairs / all-three) logic added
- [ ] Scaled to full 1990–2020 range
