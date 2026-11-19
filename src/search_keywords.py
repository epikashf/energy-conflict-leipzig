
import argparse
import csv
import glob
import os
import re

from fetch_corpus import build_corpus_id, DATA_DIR

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

SITE_KEYWORDS = ["wackersdorf", "wyhl", "kalkar"]

NUCLEAR_KEYWORDS = [
    "waa",
    "wiederaufarbeitungsanlage",
    "wiederaufbereitungsanlage",
    "kernkraftwerk",
    "atomkraftwerk",
    "schneller bruter",
    "schneller brüter",
]

OTHER_KEYWORDS = [
    "jahrestag",
    "mahnwache",
    "demonstration",
]

ALL_KEYWORDS = SITE_KEYWORDS + NUCLEAR_KEYWORDS + OTHER_KEYWORDS

# Match whole words, not parts of other words
PATTERNS = {
    kw: re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
    for kw in ALL_KEYWORDS
}


def find_sentences_file(corpus_folder):
    matches = glob.glob(
        os.path.join(corpus_folder, "**", "*-sentences.txt"),
        recursive=True
    )
    if not matches:
        raise FileNotFoundError("Could not find the sentences file.")
    return matches[0]


def find_matches(sentence, keywords):
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    regex_path = os.path.join(OUTPUT_DIR, f"hits_{year}_regex.csv")
    filtered_path = os.path.join(OUTPUT_DIR, f"hits_{year}_filtered.csv")

    total = 0
    regex_hits = 0
    filtered_hits = 0

    with open(sentences_path, encoding="utf-8", errors="replace") as infile, \
         open(regex_path, "w", encoding="utf-8", newline="") as regex_file, \
         open(filtered_path, "w", encoding="utf-8", newline="") as filtered_file:

        regex_writer = csv.writer(regex_file)
        filtered_writer = csv.writer(filtered_file)

        header = [
            "year", "corpus", "sentence_id",
            "site_matches", "nuclear_matches",
            "other_matches", "sentence_text"
        ]

        regex_writer.writerow(header)
        filtered_writer.writerow(header)

        for line in infile:
            total += 1
            parts = line.rstrip("\n").split("\t", 1)

            if len(parts) != 2:
                continue

            sentence_id, sentence = parts

            sites = find_matches(sentence, SITE_KEYWORDS)
            nuclear = find_matches(sentence, NUCLEAR_KEYWORDS)
            other = find_matches(sentence, OTHER_KEYWORDS)

            if not (sites or nuclear or other):
                continue

            row = [
                year, corpus_id, sentence_id,
                "; ".join(sites),
                "; ".join(nuclear),
                "; ".join(other),
                sentence
            ]

            regex_writer.writerow(row)
            regex_hits += 1

            # Keep sentences mentioning both a site and a nuclear term
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", required=True)
    parser.add_argument("--lang", default="deu")
    parser.add_argument("--source", default="news")
    parser.add_argument("--size", default="1M")
    args = parser.parse_args()

    search_year(args.year, args.lang, args.source, args.size)
