"""
fetch_corpus.py

Downloads one year of the Leipzig Corpora Collection German news corpus
and extracts it locally. No API key or account needed — these are public
downloadable files.

Usage:
    python src/fetch_corpus.py --year 2010
    python src/fetch_corpus.py --year 2010 --size 1M --lang deu --source news
"""

import argparse
import os
import tarfile
import urllib.request

# Where the extracted corpus files will live. This folder is in .gitignore
# so we never accidentally commit the raw corpus data.
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

BASE_URL = "https://downloads.wortschatz-leipzig.de/corpora"


def build_corpus_id(lang: str, source: str, year: str, size: str) -> str:
    """Builds the corpus filename Leipzig expects, e.g. deu_news_2010_1M"""
    return f"{lang}_{source}_{year}_{size}"


def fetch_corpus(year: str, lang: str = "deu", source: str = "news", size: str = "1M") -> str:
    """
    Downloads and extracts one year's corpus if we don't already have it.
    Returns the path to the folder containing the extracted files.
    """
    corpus_id = build_corpus_id(lang, source, year, size)
    year_folder = os.path.join(DATA_DIR, corpus_id)
    tar_path = os.path.join(DATA_DIR, f"{corpus_id}.tar.gz")

    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.isdir(year_folder):
        print(f"[skip] {corpus_id} is already downloaded and extracted at {year_folder}")
        return year_folder

    url = f"{BASE_URL}/{corpus_id}.tar.gz"
    print(f"[download] Fetching {url} ...")

    try:
        urllib.request.urlretrieve(url, tar_path)
    except Exception as e:
        # Plain-language explanation of the most likely failure reasons
        print(
            f"[error] Could not download {url}.\n"
            f"This usually means one of two things:\n"
            f"  1. That year/size combination doesn't exist for this language "
            f"(double check on https://wortschatz.uni-leipzig.de/en/download)\n"
            f"  2. A network issue on your end — try again in a moment.\n"
            f"Raw error: {e}"
        )
        raise SystemExit(1)

    print(f"[extract] Unpacking {tar_path} ...")
    os.makedirs(year_folder, exist_ok=True)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=year_folder)

    # Clean up the .tar.gz once extracted, to save disk space
    os.remove(tar_path)

    print(f"[done] {corpus_id} ready at {year_folder}")
    return year_folder


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download one year of the Leipzig corpus.")
    parser.add_argument("--year", required=True, help="e.g. 2010")
    parser.add_argument("--lang", default="deu", help="language code, default: deu")
    parser.add_argument("--source", default="news", help="source type, default: news")
    parser.add_argument("--size", default="1M", help="corpus size, default: 1M")
    args = parser.parse_args()

    fetch_corpus(args.year, args.lang, args.source, args.size)
