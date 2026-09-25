# Pseudocode & Documentation

## Data source decision

We considered two ways to get German-language sentence data from Leipzig:

| Option | What it is | Needs a key? | Filterable by year? | Are we using it? |
|---|---|---|---|---|
| Yearly downloadable corpora | Static `.tar.gz` files, one per year/language/size, e.g. `deu_news_2010_1M.tar.gz` | No | Yes | **Yes** |
| Wortschatz `Sentences` web service (SOAP) | General-purpose lookup, returns example sentences for a word | No (rate-limited only) | No | No |

Since our goal is **year-by-year** mention counts (1990–2020), the yearly
downloadable corpora is the correct source. The `Sentences` service was
considered but doesn't let us pin a query to a specific year, so it doesn't
fit this task — noting this so we don't revisit it later without a reason.

**On volume:** we're using the 1M-sentence tier per year. If a keyword
search comes back with very few or zero hits for a given year, that's an
okay result on its own — it doesn't necessarily mean something is broken,
just that the term wasn't common in that year's sample. Alice flagged this
is fine.

---

## Step 1 — Download one year of corpus data

```
FUNCTION fetch_corpus(year, language="deu", source="news", size="1M"):
    build download URL using year/language/source/size
    IF file already exists locally:
        skip download
    ELSE:
        download the .tar.gz file
        extract it into data/<year>/
    RETURN path to the extracted sentences file
```

## Step 2 — Search one year for our keywords

```
DEFINE keywords = [
    "wackersdorf", "wyhl", "kalkar",
    "waa", "wiederaufarbeitungsanlage",
    "kernkraftwerk", "atomkraftwerk",
    "schneller bruter", "schneller brüter",
    "jahrestag", "mahnwache", "demonstration"
]

FUNCTION search_keywords(year):
    load sentences file for that year
    FOR each sentence in the file:
        matched = []
        FOR each keyword in keywords:
            IF keyword appears in sentence (case-insensitive):
                add keyword to matched
        IF matched is not empty:
            record row: {year, sentence_id, sentence text, keywords matched, corpus name}
    SAVE all recorded rows to output/hits_<year>.csv
```

## Step 3 — Co-occurrence logic (planned, not yet built)

Per Alice's guidance: first look at each site individually, then check
whether sites are mentioned *together*.

```
FOR each sentence already flagged as a hit:
    check which of {wyhl, kalkar, wackersdorf} appear in it
    IF exactly one site appears:
        tag as "single mention"
    IF exactly two sites appear:
        tag as "pair" (record which pair)
    IF all three appear:
        tag as "all three"
```

This lets us later ask: are these three conflicts remembered/discussed as
one connected story, or mostly separately?

## Step 4 — Location filtering (planned, later phase)

Per meeting notes: "every relevant thing is going to have mention of that
place" — meaning a later refinement should also check that a hit isn't a
false positive (e.g., "Wyhl" as part of an unrelated proper noun). This is
noted for a future pass, not part of the one-year prototype.

## Step 5 — Confidence threshold (planned, later phase)

Meeting notes mention an "estimated confidence threshold" for keyword
matches — this likely refers to weighting or filtering hits by how
confidently a sentence is actually *about* the topic versus a coincidental
keyword match. Flagged as a follow-up question for Alice: what threshold
or method does she have in mind (e.g., requiring 2+ keyword matches per
sentence, or a minimum sentence length)?

## Output format (tabular, with metadata)

| year | corpus | sentence_id | keyword_matched | sentence_text |
|---|---|---|---|---|
| 2010 | deu_news_2010_1M | 48213 | wackersdorf | "..." |

This is the format for the one-year prototype deliverable.
