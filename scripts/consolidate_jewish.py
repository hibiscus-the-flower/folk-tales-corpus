"""
Consolidate the Jewish-repertoire collections:

  1. index/jewish_repertoire.csv  — a unified catalogue of every Jewish tale
     (collection, title, author, year, source-type, fidelity, word count).
  2. index/jewish_variant_candidates.csv — cross-collection tales that are likely
     RETELLINGS OF THE SAME SOURCE STORY. Text-similarity can't find these (the
     wordings are independent), so we link by shared *distinctive proper nouns*
     (rare names like Ashmedai, Shamir, Kenaz, Bostanai that occur in only a few
     tales). These are candidates for human review, NOT auto-merged.

Dedup note: scripts/dedup_jewish.py already verified there are zero text
duplicates (max pairwise 4-gram Jaccard 0.028), so nothing is deleted here.

Usage:
    python3 scripts/consolidate_jewish.py
"""

import os, re, csv, glob, html
from collections import defaultdict
from itertools import combinations

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# collection -> (author, year, source-type, fidelity)
COLL_META = {
    "landa_en":            ("Gertrude Landa",        1919, "Talmud/Midrash retelling", "clean"),
    "friedlander_en":      ("Gerald Friedlander",    1918, "Talmud/Midrash retelling", "clean"),
    "jewish_fairy_book_en":("Gerald Friedlander",    1920, "Talmud/Midrash retelling", "clean"),
    "hebrew_tales_en":     ("Hyman Hurwitz",         1826, "Talmud/Midrash tale/fable", "clean"),
    "ginzberg_legends_en": ("Louis Ginzberg",        1909, "Aggadah / biblical legend", "clean"),
    "isaacs_en":           ("Abram S. Isaacs",       1893, "Talmud/Midrash retelling", "ocr"),
    "rapaport_en":         ("Samuel Rapaport",       1907, "Midrash source-book",       "ocr"),
    "weinreich_en":        ("Various (YIVO zamlers)", 1988, "E-European oral mayse",     "stub"),
}
TEXT_COLLS = [c for c in COLL_META if c != "weinreich_en"]

META_CLASS_RE = re.compile(r'class="(section-label|ocr-note|stub|src)"', re.I)

# Common capitalised words that are NOT distinctive proper nouns.
STOP = set("""The A An And But Or For Nor So Yet As At By In On Of To Up If It He She
They We You I His Her Their Our Your My Him Them Then There Thus When While Who Whom
Whose What Which That This These Those Now Here Lord God King Rabbi Reb One Two Three
Holy Israel Jews Jewish Torah Talmud Midrash Book Tale Story Chapter Part Day Night
Heaven Earth Man Woman Son Sons Father Mother Once Behold O Oh Yea Verily Said Says
Great Good Evil Behold Among Before After Over Under Into Out From With Without Upon
Every All Both Each Some Many Much More Most Such No Not Never Ever Also Even Only
Sabbath Egypt Moses Abraham Isaac Jacob Joseph David Solomon Pharaoh Adam Eve Noah
Angel Angels Spirit Soul Death Life Law Word Words World Time Hand House People
North South East West General State States Court Crown Royal Royalty Highness Majesty
Mighty Sovereign Princess Prince Hell Heaven Hunger Kingdom Emperor Empress Queen
Sir Madam Master Mistress Lady Throne Palace Castle City Town Land Sea River Mountain
Gentile Gentiles Heathen Wise Fool Beggar Merchant Slave Thief Bride Bridegroom""".split())

TITLE_RE = re.compile(r"<h2\b[^>]*>(.*?)</h2>", re.DOTALL | re.I)


def tale_text(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    tm = TITLE_RE.search(raw)
    title = html.unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else ""
    body = [m.group(2) for m in re.finditer(r"<p\b([^>]*)>(.*?)</p>", raw, re.DOTALL | re.I)
            if not META_CLASS_RE.search(m.group(1))]
    text = html.unescape(re.sub(r"<[^>]+>", " ", " ".join(body)))
    return title, text


# Tokens seen capitalised MID-SENTENCE (preceded by a lowercase word) are real
# proper nouns; tokens only ever capitalised at a sentence start are not.
MIDCAP_RE = re.compile(r"[a-z]+\s+([A-Z][a-zA-Z]{2,})\b")


def proper_nouns(text, goodnouns):
    toks = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", text)
    return {t for t in toks if t in goodnouns and t not in STOP}


# ---- load (two passes: build the good-noun set, then assign) ---------------
raw_docs = []
for coll in TEXT_COLLS:
    for path in sorted(glob.glob(os.path.join(PROJ, "corpus", coll, "*.html"))):
        title, text = tale_text(path)
        raw_docs.append((coll, os.path.basename(path), title, text))

GOODNOUNS = set()
for _, _, _, text in raw_docs:
    GOODNOUNS.update(MIDCAP_RE.findall(text))

docs = []
for coll, fname, title, text in raw_docs:
    docs.append({
        "coll": coll, "fname": fname, "title": title,
        "words": len(text.split()), "nouns": proper_nouns(text, GOODNOUNS),
    })

# document frequency of each proper noun
df = defaultdict(int)
for d in docs:
    for n in d["nouns"]:
        df[n] += 1

# Keep only DISTINCTIVE nouns: appear in >=2 but <= RARE_MAX docs.
RARE_MAX = 8
for d in docs:
    d["rare"] = {n for n in d["nouns"] if 2 <= df[n] <= RARE_MAX}

# ---- catalogue ------------------------------------------------------------
cat = os.path.join(PROJ, "index", "jewish_repertoire.csv")
with open(cat, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["collection", "file", "title", "author", "year",
                "source_type", "fidelity", "word_count"])
    # text collections
    for d in sorted(docs, key=lambda d: (d["coll"], d["fname"])):
        a, y, st, fi = COLL_META[d["coll"]]
        w.writerow([d["coll"], d["fname"], d["title"], a, y, st, fi, d["words"]])
    # weinreich stubs (no text)
    for path in sorted(glob.glob(os.path.join(PROJ, "corpus", "weinreich_en", "*.html"))):
        title, _ = tale_text(path)
        a, y, st, fi = COLL_META["weinreich_en"]
        w.writerow(["weinreich_en", os.path.basename(path), title, a, y, st, fi, 0])

n_stub = len(glob.glob(os.path.join(PROJ, "corpus", "weinreich_en", "*.html")))
print(f"Catalogue: {len(docs)} full-text tales + {n_stub} stubs -> {cat}")

# ---- variant candidates (shared distinctive proper nouns) -----------------
pairs = []
for i, j in combinations(range(len(docs)), 2):
    if docs[i]["coll"] == docs[j]["coll"]:
        continue                      # only cross-collection candidates
    shared = docs[i]["rare"] & docs[j]["rare"]
    if len(shared) >= 3:
        pairs.append((len(shared), shared, i, j))
pairs.sort(reverse=True, key=lambda p: p[0])

var = os.path.join(PROJ, "index", "jewish_variant_candidates.csv")
with open(var, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["shared_n", "shared_names", "coll_a", "file_a", "title_a",
                "coll_b", "file_b", "title_b"])
    for n, shared, i, j in pairs:
        da, db = docs[i], docs[j]
        w.writerow([n, "; ".join(sorted(shared)), da["coll"], da["fname"],
                    da["title"], db["coll"], db["fname"], db["title"]])

print(f"Variant candidates (>=3 shared rare names): {len(pairs)} pairs -> {var}\n")
print("Top cross-collection variant candidates:")
for n, shared, i, j in pairs[:18]:
    da, db = docs[i], docs[j]
    names = ", ".join(sorted(shared)[:5])
    print(f"  [{n}] «{da['title'][:32]}» ({da['coll'].split('_')[0]}) "
          f"<> «{db['title'][:32]}» ({db['coll'].split('_')[0]})")
    print(f"       shared: {names}")
