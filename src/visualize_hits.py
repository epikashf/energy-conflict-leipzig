
import csv
import os
from collections import Counter
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(__file__)

INPUT_FILE = os.path.join(
    BASE_DIR, "..", "output", "hits_2010_regex.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR, "..", "output", "keyword_frequency_2010.png"
)

counts = Counter()

with open(INPUT_FILE, encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        for column in [
            "site_matches",
            "nuclear_matches",
            "other_matches"
        ]:
            for keyword in row[column].split(";"):
                keyword = keyword.strip()
                if keyword:
                    counts[keyword] += 1

sorted_counts = counts.most_common()

keywords = [item[0] for item in sorted_counts]
frequencies = [item[1] for item in sorted_counts]

plt.figure(figsize=(11, 6))
plt.barh(keywords, frequencies, color="steelblue")
plt.gca().invert_yaxis()

plt.xlabel("Number of matching sentences")
plt.ylabel("Keyword")
plt.title("Keyword Frequency in German News (2010)")
plt.tight_layout()

plt.savefig(OUTPUT_FILE, dpi=300)
plt.show()

print(f"Chart saved to: {OUTPUT_FILE}")
