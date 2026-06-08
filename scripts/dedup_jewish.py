"""
Find duplicate / near-duplicate tales within the Jewish-repertoire collections.

Strategy
--------
The collections draw on the same Talmud/Midrash sources, so two kinds of overlap
exist, and they must be treated differently:

  * TEXT DUPLICATES — the *same translation* reprinted in two collections
    (e.g. an author's tale appearing in two of his books). Safe to dedupe.
  * VARIANTS — the *same source story* retold by different authors in different
    words. Valuable folklore variants; must NOT be deleted. These have low text
    similarity, so a text-similarity method leaves them alone by design.

We fingerprint each tale with MinHash over word 4-grams and report:
  - exact-text duplicate groups (identical normalised text)
  - near-duplicate pairs (estimated Jaccard >= THRESH, confirmed by true Jaccard)
  - cross-collection same-title pairs (informational; often variants)

Output: index/dedup_jewish_report.csv  (+ printed summary). Read-only — proposes,
does not delete.

Usage:
    python3 scripts/dedup_jewish.py
"""

import os, re, csv, html, hashlib, glob
from itertools import combinations

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Real-text Jewish collections (weinreich is stubs — handled separately by title).
TEXT_COLLECTIONS = [
    "landa_en", "friedlander_en", "jewish_fairy_book_en", "hebrew_tales_en",
    "ginzberg_legends_en", "isaacs_en", "rapaport_en",
]
STUB_COLLECTION = "weinreich_en"

# Paragraph classes that are metadata, not tale text.
META_CLASS_RE = re.compile(r'class="(section-label|ocr-note|stub|src|cite-bracket|'
                           r'reference|reference-text|mw-cite-backlink)"', re.I)

NUM_HASHES = 96
SHINGLE_N = 4
NEAR_THRESH = 0.55          # estimated-Jaccard cutoff for "near duplicate"
_MASK = (1 << 32) - 1
# NUM_HASHES independent (a,b) hash params, derived deterministically.
_PARAMS = []
for i in range(NUM_HASHES):
    h = hashlib.md5(str(i).encode()).digest()
    a = int.from_bytes(h[:4], "big") | 1
    b = int.from_bytes(h[4:8], "big")
    _PARAMS.append((a, b))


def tale_text(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    # Title (for reporting) and body paragraphs.
    tm = re.search(r"<h2\b[^>]*>(.*?)</h2>", raw, re.DOTALL | re.I)
    title = html.unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else ""
    body = []
    for m in re.finditer(r"<p\b([^>]*)>(.*?)</p>", raw, re.DOTALL | re.I):
        if META_CLASS_RE.search(m.group(1)):
            continue
        body.append(m.group(2))
    text = html.unescape(re.sub(r"<[^>]+>", " ", " ".join(body)))
    return title, text


def normalise(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def shingles(norm):
    words = norm.split()
    if len(words) < SHINGLE_N:
        return {norm} if norm else set()
    return {" ".join(words[i:i + SHINGLE_N])
            for i in range(len(words) - SHINGLE_N + 1)}


def minhash(shs):
    if not shs:
        return tuple([0] * NUM_HASHES)
    hashed = [int.from_bytes(hashlib.md5(s.encode()).digest()[:4], "big")
              for s in shs]
    sig = []
    for a, b in _PARAMS:
        sig.append(min(((a * x + b) & _MASK) for x in hashed))
    return tuple(sig)


def norm_title(t):
    t = t.lower()
    t = re.sub(r"^(the|a|an)\s+", "", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---- load all tales --------------------------------------------------------
docs = []   # (collection, fname, title, norm_title, normtext, shingleset, sig, exacthash)
for coll in TEXT_COLLECTIONS:
    for path in sorted(glob.glob(os.path.join(PROJ, "corpus", coll, "*.html"))):
        title, text = tale_text(path)
        norm = normalise(text)
        shs = shingles(norm)
        docs.append({
            "coll": coll,
            "fname": os.path.basename(path),
            "title": title,
            "ntitle": norm_title(title),
            "norm": norm,
            "shs": shs,
            "sig": minhash(shs),
            "exact": hashlib.md5(norm.encode()).hexdigest(),
            "words": len(norm.split()),
        })

print(f"Loaded {len(docs)} tales from {len(TEXT_COLLECTIONS)} collections.\n")


def est_jaccard(a, b):
    sa, sb = a["sig"], b["sig"]
    return sum(1 for x, y in zip(sa, sb) if x == y) / NUM_HASHES


def true_jaccard(a, b):
    A, B = a["shs"], b["shs"]
    if not A or not B:
        return 0.0
    inter = len(A & B)
    return inter / (len(A) + len(B) - inter)


# ---- exact duplicates ------------------------------------------------------
exact_groups = {}
for i, d in enumerate(docs):
    exact_groups.setdefault(d["exact"], []).append(i)
exact_dups = [g for g in exact_groups.values() if len(g) > 1]

# ---- near duplicates (skip pairs already exact) ----------------------------
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

# ---- cross-collection same-title (informational) ---------------------------
title_groups = {}
for i, d in enumerate(docs):
    if d["ntitle"]:
        title_groups.setdefault(d["ntitle"], []).append(i)
title_dups = [(t, g) for t, g in title_groups.items()
              if len({docs[k]["coll"] for k in g}) > 1]

# ---- report ----------------------------------------------------------------
out = os.path.join(PROJ, "index", "dedup_jewish_report.csv")
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
            # only list title-matches that aren't already near/exact text dups
            if true_jaccard(da, db) < NEAR_THRESH:
                w.writerow(["same-title", f"{true_jaccard(da, db):.3f}",
                            da["coll"], da["fname"], da["title"],
                            db["coll"], db["fname"], db["title"]])

print(f"=== EXACT text-duplicate groups: {len(exact_dups)} ===")
for g in exact_dups:
    for k in g:
        print(f"    {docs[k]['coll']:>22}/{docs[k]['fname']}  «{docs[k]['title']}»")
    print()

print(f"=== NEAR text-duplicate pairs (Jaccard >= {NEAR_THRESH}): {len(near_pairs)} ===")
for tj, i, j in near_pairs:
    da, db = docs[i], docs[j]
    print(f"  {tj:.3f}  {da['coll']}/{da['fname']} «{da['title']}»")
    print(f"         {db['coll']}/{db['fname']} «{db['title']}»")

print(f"\n=== Cross-collection SAME-TITLE but low text overlap "
      f"(likely variants, KEEP): {sum(1 for t,g in title_dups)} title(s) ===")
for t, g in title_dups:
    colls = ", ".join(f"{docs[k]['coll']}" for k in g)
    print(f"  «{docs[g[0]]['title']}»  in: {colls}")

print(f"\nFull report -> {out}")
