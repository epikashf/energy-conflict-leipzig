
import argparse
import csv
import glob
import os
import re

from fetch_corpus import build_corpus_id, DATA_DIR

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

# The three nuclear conflict locations
SITE_KEYWORDS = [
    "wackersdorf",
    "wyhl",
    "kalkar",
]

# Nuclear-related terms
NUCLEAR_KEYWORDS = [
    "waa",
    "wiederaufarbeitungsanlage",
    "wiederaufbereitungsanlage",
    "kernkraftwerk",
    "atomkraftwerk",
    "schneller bruter",
    "schneller brüter",
]

# Protest and commemoration terms
OTHER_KEYWORDS = [
    "jahrestag",
    "mahnwache",
    "demonstration",
]

ALL_KEYWORDS = SITE_KEYWORDS + NUCLEAR_KEYWORDS + OTHER_KEYWORDS

# Common German endings for some keywords
WORD_ENDINGS = {
    "atomkraftwerk": r"(?:e|en|s)?",
    "kernkraftwerk": r"(?:e|en|s)?",
    "wiederaufbereitungsanlage": r"(?:n)?",
    "wiederaufarbeitungsanlage": r"(?:n)?",
    "demonstration": r"(?:en|s)?",
    "mahnwache": r"(?:n)?",
}

# Match complete words, including the endings above
PATTERNS = {}

for kw in ALL_KEYWORDS:
    ending = WORD_ENDINGS.get(kw, "")

    PATTERNS[kw] = re.compile(
        r"\b" + re.escape(kw) + ending + r"\b",
        re.IGNORECASE
    )


def find_sentences_file(corpus_folder):
    # Find the sentence file inside the downloaded corpus
    matches = glob.glob(
        os.path.join(corpus_folder, "**", "*-sentences.txt"),
        recursive=True
    )

    if not matches:
        raise FileNotFoundError(
            f"Could not find a sentences file in {corpus_folder}"
        )

    return matches[0]


def find_matches(sentence, keywords):
    # Return the keywords found in this sentence
    return [
        kw for kw in keywords
        if PATTERNS[kw].search(sentence)
    ]


def search_year(year, lang="deu", source="news", size="1M"):
    corpus_id = build_corpus_id(lang, source, year, size)
    corpus_folder = os.path.join(DATA_DIR, corpus_id)

    if not os.path.isdir(corpus_folder):
        print(f"Corpus not found: {corpus_id}")
        print(f"Run: python fetch_corpus.py --year {year}")
        return

    sentences_path = find_sentences_file(corpus_folder)

    print(f"Reading: {sentences_path}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    regex_path = os.path.join(
        OUTPUT_DIR, f"hits_{year}_regex.csv"
    )

    filtered_path = os.path.join(
        OUTPUT_DIR, f"hits_{year}_filtered.csv"
    )

    total = 0
    regex_hits = 0
    filtered_hits = 0

    with open(
        sentences_path, encoding="utf-8", errors="replace"
    ) as infile, open(
        regex_path, "w", encoding="utf-8", newline=""
    ) as regex_file, open(
        filtered_path, "w", encoding="utf-8", newline=""
    ) as filtered_file:

        regex_writer = csv.writer(regex_file)
        filtered_writer = csv.writer(filtered_file)

        header = [
            "year",
            "corpus",
            "sentence_id",
            "site_matches",
            "nuclear_matches",
            "other_matches",
            "sentence_text",
        ]

        regex_writer.writerow(header)
        filtered_writer.writerow(header)

        for line in infile:
            total += 1

            # Show progress every 100,000 sentences
            if total % 100000 == 0:
                print(
                    f"Scanned {total:,} sentences...",
                    flush=True
                )

            # Each line has a sentence ID and its text
            parts = line.rstrip("\n").split("\t", 1)

            if len(parts) != 2:
                continue

            sentence_id, sentence = parts

            sites = find_matches(sentence, SITE_KEYWORDS)
            nuclear = find_matches(sentence, NUCLEAR_KEYWORDS)
            other = find_matches(sentence, OTHER_KEYWORDS)

            # Skip sentences without any keywords
            if not (sites or nuclear or other):
                continue

            row = [
                year,
                corpus_id,
                sentence_id,
                "; ".join(sites),
                "; ".join(nuclear),
                "; ".join(other),
                sentence,
            ]

            # Save every sentence matching at least one keyword
            regex_writer.writerow(row)
            regex_hits += 1

            # Save sentences with a site AND nuclear term
            if sites and nuclear:
                filtered_writer.writerow(row)
                filtered_hits += 1

    print(f"\nYear: {year}")
    print(f"Sentences scanned: {total}")
    print(f"Regex matches: {regex_hits}")
    print(f"Site + nuclear matches: {filtered_hits}")
    print(f"Saved: {regex_path}")
    print(f"Saved: {filtered_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search Leipzig corpus for energy conflict keywords."
    )

    parser.add_argument("--year", required=True)
    parser.add_argument("--lang", default="deu")
    parser.add_argument("--source", default="news")
    parser.add_argument("--size", default="1M")

    args = parser.parse_args()

    search_year(
        args.year,
        args.lang,
        args.source,
        args.size
    )
