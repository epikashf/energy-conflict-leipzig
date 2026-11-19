
import argparse
import csv
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")


def match_sources(year):
    corpus = f"deu_news_{year}_1M"
    corpus_dir = os.path.join(DATA_DIR, corpus)

    mapping_path = os.path.join(
        corpus_dir, f"{corpus}-inv_so.txt"
    )
    sources_path = os.path.join(
        corpus_dir, f"{corpus}-sources.txt"
    )
    input_path = os.path.join(
        OUTPUT_DIR, f"hits_{year}_filtered.csv"
    )
    output_path = os.path.join(
        OUTPUT_DIR, f"hits_{year}_with_sources.csv"
    )

    # Read the keyword hits we want to enrich
    with open(input_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        hits = list(reader)
        columns = reader.fieldnames

    if not hits:
        print("No filtered hits found.")
        return

    wanted_ids = {row["sentence_id"] for row in hits}

    # Map matching sentence IDs to their source IDs
    sentence_sources = defaultdict(set)

    with open(mapping_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) < 2:
                continue

            source_id, sentence_id = parts[:2]

            if sentence_id in wanted_ids:
                sentence_sources[sentence_id].add(source_id)

    wanted_sources = set()

    for source_ids in sentence_sources.values():
        wanted_sources.update(source_ids)

    # Retrieve URLs and dates for matching sources
    source_details = {}

    with open(sources_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) < 3:
                continue

            source_id = parts[0]

            if source_id in wanted_sources:
                source_details[source_id] = {
                    "url": parts[1],
                    "date": parts[2],
                }

    # Create a separate row for each sentence-source pair
    output_columns = columns + [
        "source_id",
        "source_url",
        "publication_date",
    ]

    matched_rows = 0
    unmatched_rows = 0

    with open(
        output_path, "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=output_columns
        )
        writer.writeheader()

        for hit in hits:
            sentence_id = hit["sentence_id"]
            source_ids = sorted(
                sentence_sources.get(sentence_id, [])
            )

            if not source_ids:
                writer.writerow({
                    **hit,
                    "source_id": "",
                    "source_url": "",
                    "publication_date": "",
                })
                unmatched_rows += 1
                continue

            for source_id in source_ids:
                details = source_details.get(source_id, {})

                writer.writerow({
                    **hit,
                    "source_id": source_id,
                    "source_url": details.get("url", ""),
                    "publication_date": details.get("date", ""),
                })
                matched_rows += 1

    print(f"\nYear: {year}")
    print(f"Filtered sentences: {len(hits)}")
    print(f"Matched sentence-source pairs: {matched_rows}")
    print(f"Unmatched sentences: {unmatched_rows}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", required=True)
    args = parser.parse_args()

    match_sources(args.year)
