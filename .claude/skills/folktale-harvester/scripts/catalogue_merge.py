"""
catalogue_merge — combine tale lists from several aggregators into one deduped
master catalogue for a culture.

The catalogue track should never rely on a single aggregator: Ashliman is strong
on some cultures and thin on others, Wikisource/Wikipedia list pages cover
different ground, and a Gutenberg edition's table of contents is itself a tale
list. This tool merges any number of CSVs into `index/catalogue_<culture>.csv`,
deduping by normalised title and remembering which source(s) each title came from.

It is idempotent on title and auto-includes the existing master, so the
**second sweep** is trivial: after you discover an aggregator you missed, dump
its titles to a CSV and re-run this — new titles are added, known ones just gain
a source tag. Re-running never loses earlier entries.

Each input CSV needs at least a `title` column. Optional columns it will carry
through: `atu`, `culture`, `author`, `source_page`. The source label for an input
is its filename stem (so name your CSVs meaningfully, e.g. wikisource.csv).

Usage:
    python3 catalogue_merge.py <culture> <input1.csv> [input2.csv ...]

Example:
    python3 catalogue_merge.py Japanese \
        index/catalogue_japanese.csv \         # the Ashliman crawl output
        /tmp/japanese_wikisource.csv \
        /tmp/japanese_wikipedia_list.csv
"""

import os
import sys
import csv

from folktale_lib import PROJ, norm_title

CARRY = ["atu", "culture", "author", "source_page"]


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main(culture, inputs):
    master_path = os.path.join(PROJ, "index", f"catalogue_{culture.lower()}.csv")
    # Auto-include the existing master so re-runs accumulate (the second sweep).
    if master_path not in [os.path.abspath(p) for p in inputs] and os.path.exists(master_path):
        inputs = [master_path] + inputs

    merged = {}          # norm_title -> row dict (with a 'sources' set)
    per_source = {}
    for path in inputs:
        label = os.path.splitext(os.path.basename(path))[0]
        rows = load(path)
        per_source[label] = len(rows)
        for r in rows:
            title = (r.get("title") or "").strip()
            if not title:
                continue
            key = norm_title(title)
            if not key:
                continue
            src = set((r.get("sources") or label).split("|")) if r.get("sources") else {label}
            if key in merged:
                merged[key]["sources"] |= src
                for c in CARRY:                      # fill blanks only
                    if not merged[key].get(c) and r.get(c):
                        merged[key][c] = r[c]
            else:
                row = {"title": title, "sources": set(src)}
                for c in CARRY:
                    row[c] = r.get(c, "")
                merged[key] = row

    rows = sorted(merged.values(), key=lambda r: norm_title(r["title"]))
    fields = ["title"] + CARRY + ["sources", "n_sources"]
    with open(master_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            r = dict(r)
            srcs = sorted(r.pop("sources"))
            r["sources"] = "|".join(srcs)
            r["n_sources"] = len(srcs)
            w.writerow(r)

    print(f"{len(rows)} unique titles -> index/catalogue_{culture.lower()}.csv")
    for label, n in per_source.items():
        print(f"  {label}: {n} rows in")
    corroborated = sum(1 for r in rows if len(r["sources"]) > 1)
    print(f"  titles confirmed by >1 source: {corroborated}")
    if len(rows) < 150:
        print(f"  NOTE: {len(rows)} < 150 target — search for more aggregators "
              f"(Wikisource/Wikipedia list pages, edition TOCs) and re-run.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: python3 catalogue_merge.py <culture> <input.csv> [more.csv ...]")
    main(sys.argv[1], sys.argv[2:])
