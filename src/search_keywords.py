"""
search_keywords.py

Searches one year's downloaded Leipzig corpus for our energy-conflict
keywords, and writes a tabular CSV of every matching sentence with
metadata (year, corpus, sentence ID, which keyword(s) matched).

Usage:
    python src/search_keywords.py --year 2010
"""

import argparse
import csv
import glob
import os

from fetch_corpus import build_corpus_id, DATA_DIR

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

# All keywords from the meeting notes, lowercased for case-insensitive matching.
# The three "sites" are called out separately so we can later check
# co-occurrence (single / pair / all-three) — see docs/pseudocode.md Step 3.
SITE_KEYWORDS = ["wackersdorf", "wyhl", "kalkar"]

OTHER_KEYWORDS = [
    "waa",
    "wiederaufarbeitungsanlage",
    "kernkraftwerk",
    "atomkraftwerk",
    "schneller bruter",
    "schneller brüter",
    "jahrestag",
    "mahnwache",
    "demonstration",
]

ALL_KEYWORDS = SITE_KEYWORDS + OTHER_KEYWORDS


def find_sentences_file(corpus_folder: str) -> str:
    """
    The Leipzig corpus archive contains a few files; the one we want
    ends in '-sentences.txt'. This looks for it inside the extracted folder.
    """
    matches = glob.glob(os.path.join(corpus_folder, "**", "*-sentences.txt"), recursive=True)
    if not matches:
        raise FileNotFoundError(
            f"Couldn't find a '-sentences.txt' file inside {corpus_folder}.\n"
            f"Open the folder and check the actual filename — Leipzig sometimes "
            f"changes the naming slightly between corpora."
        )
    return matches[0]


def search_year(year: str, lang: str = "deu", source: str = "news", size: str = "1M"):
    corpus_id = build_corpus_id(lang, source, year, size)
    corpus_folder = os.path.join(DATA_DIR, corpus_id)

    if not os.path.isdir(corpus_folder):
        print(
            f"[error] No downloaded data found for {corpus_id}.\n"
            f"Run this first:\n"
            f"    python src/fetch_corpus.py --year {year}\n"
        )
        raise SystemExit(1)

    sentences_path = find_sentences_file(corpus_folder)
    print(f"[read] Using sentence file: {sentences_path}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"hits_{year}.csv")

    total_sentences = 0
    total_hits = 0

    with open(sentences_path, encoding="utf-8", errors="replace") as infile, \
         open(output_path, "w", encoding="utf-8", newline="") as outfile:

        writer = csv.writer(outfile)
        writer.writerow(["year", "corpus", "sentence_id", "keywords_matched", "sentence_text"])

        for line in infile:
            total_sentences += 1
            # Leipzig sentence files are tab-separated: "<id>\t<sentence text>"
            parts = line.rstrip("\n").split("\t", 1)
            if len(parts) != 2:
                continue  # skip malformed lines rather than crashing
            sentence_id, sentence_text = parts

            lowered = sentence_text.lower()
            matched = [kw for kw in ALL_KEYWORDS if kw in lowered]

            if matched:
                total_hits += 1
                writer.writerow([year, corpus_id, sentence_id, "; ".join(matched), sentence_text])

    print(f"[done] Scanned {total_sentences} sentences, found {total_hits} hits.")
    print(f"[done] Results written to {output_path}")

    if total_hits == 0:
        print(
            "[note] Zero hits this year is a valid result, not necessarily an "
            "error — it may just mean the keywords weren't common in this "
            "year's 1M-sentence sample. Worth flagging to Alice either way."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search one year of corpus for keywords.")
    parser.add_argument("--year", required=True, help="e.g. 2010")
    parser.add_argument("--lang", default="deu")
    parser.add_argument("--source", default="news")
    parser.add_argument("--size", default="1M")
    args = parser.parse_args()

    search_year(args.year, args.lang, args.source, args.size)
