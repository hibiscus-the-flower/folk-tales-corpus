"""
dedup_corpus — find duplicate / near-duplicate tales across collections.

Folk-tale corpora contain two very different kinds of overlap, and they must be
treated differently:

  * TEXT DUPLICATES — the *same translation* reprinted in two places. Safe to
    drop one copy.
  * VARIANTS — the *same story* retold by different authors in different words.
    These are the lifeblood of folklore research and must NOT be deleted. They
    have low text similarity, so a text-similarity method leaves them alone by
    design — that is the point, not a limitation.

Each tale is fingerprinted with MinHash over word 4-grams. The script REPORTS;
it never deletes. Review the report and remove copies yourself if warranted.

Usage:
    python3 dedup_corpus.py                       # all collections in corpus/
    python3 dedup_corpus.py irish_jacobs_en irish_kennedy_en   # only these
"""

import os
import re
import csv
import sys
import glob
import html
import hashlib
from itertools import combinations

from folktale_lib import PROJ, norm_title

NUM_HASHES = 96
SHINGLE_N = 4
NEAR_THRESH = 0.55
_MASK = (1 << 32) - 1
_PARAMS = []
for _i in range(NUM_HASHES):
    _h = hashlib.md5(str(_i).encode()).digest()
    _PARAMS.append((int.from_bytes(_h[:4], "big") | 1, int.from_bytes(_h[4:8], "big")))

# Paragraph classes that are metadata, not tale text.
META_CLASS_RE = re.compile(r'class="(section-label|ocr-note|stub|src|cite-bracket|'
                           r'reference|reference-text|mw-cite-backlink)"', re.I)


def tale_text(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    tm = re.search(r"<h2\b[^>]*>(.*?)</h2>", raw, re.DOTALL | re.I)
    title = html.unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else ""
    body = [m.group(2) for m in re.finditer(r"<p\b([^>]*)>(.*?)</p>", raw, re.DOTALL | re.I)
            if not META_CLASS_RE.search(m.group(1))]
    text = html.unescape(re.sub(r"<[^>]+>", " ", " ".join(body)))
    return title, text


def normalise(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()


def shingles(norm):
    words = norm.split()
    if len(words) < SHINGLE_N:
        return {norm} if norm else set()
    return {" ".join(words[i:i + SHINGLE_N]) for i in range(len(words) - SHINGLE_N + 1)}


def minhash(shs):
    if not shs:
        return tuple([0] * NUM_HASHES)
    hashed = [int.from_bytes(hashlib.md5(s.encode()).digest()[:4], "big") for s in shs]
    return tuple(min(((a * x + b) & _MASK) for x in hashed) for a, b in _PARAMS)


def est_jaccard(a, b):
    return sum(1 for x, y in zip(a["sig"], b["sig"]) if x == y) / NUM_HASHES


def true_jaccard(a, b):
    A, B = a["shs"], b["shs"]
    if not A or not B:
        return 0.0
    inter = len(A & B)
    return inter / (len(A) + len(B) - inter)


def main(collections):
    base = os.path.join(PROJ, "corpus")
    if not collections:
        collections = sorted(d for d in os.listdir(base)
                             if os.path.isdir(os.path.join(base, d)))
    docs = []
    for coll in collections:
        for path in sorted(glob.glob(os.path.join(base, coll, "*.html"))):
            title, text = tale_text(path)
            norm = normalise(text)
            shs = shingles(norm)
            docs.append({"coll": coll, "fname": os.path.basename(path),
                         "title": title, "ntitle": norm_title(title), "shs": shs,
                         "sig": minhash(shs), "exact": hashlib.md5(norm.encode()).hexdigest(),
                         "words": len(norm.split())})
    print(f"Loaded {len(docs)} tales from {len(collections)} collections.\n")

    exact_groups = {}
    for i, d in enumerate(docs):
        exact_groups.setdefault(d["exact"], []).append(i)
    exact_dups = [g for g in exact_groups.values() if len(g) > 1]

    near_pairs = []
    for i, j in combinations(range(len(docs)), 2):
        if docs[i]["exact"] == docs[j]["exact"]:
            continue
        if est_jaccard(docs[i], docs[j]) < NEAR_THRESH:
            continue
        tj = true_jaccard(docs[i], docs[j])
        if tj >= NEAR_THRESH:
            near_pairs.append((tj, i, j))
    near_pairs.sort(reverse=True)

    title_groups = {}
    for i, d in enumerate(docs):
        if d["ntitle"]:
            title_groups.setdefault(d["ntitle"], []).append(i)
    title_dups = [(t, g) for t, g in title_groups.items()
                  if len({docs[k]["coll"] for k in g}) > 1]

    out = os.path.join(PROJ, "index", "dedup_report.csv")
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "similarity", "coll_a", "file_a", "title_a",
                    "coll_b", "file_b", "title_b"])
        for g in exact_dups:
            for a, b in combinations(g, 2):
                da, db = docs[a], docs[b]
                w.writerow(["exact", "1.000", da["coll"], da["fname"], da["title"],
                            db["coll"], db["fname"], db["title"]])
        for tj, i, j in near_pairs:
            da, db = docs[i], docs[j]
            w.writerow(["near", f"{tj:.3f}", da["coll"], da["fname"], da["title"],
                        db["coll"], db["fname"], db["title"]])
        for t, g in title_dups:
            for a, b in combinations(g, 2):
                da, db = docs[a], docs[b]
                if true_jaccard(da, db) < NEAR_THRESH:
                    w.writerow(["same-title", f"{true_jaccard(da, db):.3f}",
                                da["coll"], da["fname"], da["title"],
                                db["coll"], db["fname"], db["title"]])

    print(f"EXACT duplicate groups: {len(exact_dups)}")
    print(f"NEAR-duplicate pairs (Jaccard >= {NEAR_THRESH}): {len(near_pairs)}")
    print(f"Cross-collection same-title, low overlap (likely VARIANTS, keep): "
          f"{len(title_dups)}")
    print(f"\nReport -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
