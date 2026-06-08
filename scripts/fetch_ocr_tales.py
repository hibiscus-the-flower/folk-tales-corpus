"""
Harvest Jewish folk-tale collections that exist only as Internet-Archive OCR
(djvu.txt) — no clean Gutenberg/Wikisource edition. Each book is split into
per-tale (or per-chapter) HTML files matching the corpus format.

Because the source is raw OCR, text fidelity is LOWER than the other corpus
collections: expect occasional mis-recognised letters and drop-cap garble at the
start of a tale. The manifest `source` field flags these as OCR.

Books handled (all public domain):
  isaacs    Abram S. Isaacs, *Stories from the Rabbis* (1893)            — 16 discrete tales
  rapaport  Samuel Rapaport, *Tales and Maxims from the Midrash* (1907)  — by Midrash source
  polano    H. Polano, *The Talmud: Selections* (1876)                   — legend sections

Splitting: each book has an ordered list of section/tale titles. We locate each
title in the body as a heading (flexible whitespace, case-insensitive), taking
the FIRST occurrence after the previous title (running-page-heads repeat a title
but never match the *next* one, so the sequence stays aligned).

Usage:
    python3 scripts/fetch_ocr_tales.py            # all books
    python3 scripts/fetch_ocr_tales.py isaacs     # one or more book keys
"""

import os, re, sys, time, html as htmlmod, subprocess

PROJ  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(PROJ, ".cache", "yiddish")
UA    = "fairy-tales-research/1.0 (daniel.hiterer@gmail.com)"
os.makedirs(CACHE, exist_ok=True)

# --------------------------------------------------------------------------- #
BOOKS = {
    "isaacs": {
        "label":      "isaacs_en",
        "archive_id": "storiesfromrabb00isaa",
        "author":     "Abram S. Isaacs",
        "source":     "archive.org storiesfromrabb00isaa OCR (Stories from the Rabbis, 1893)",
        "titles": [
            "The Faust of the Talmud",
            "The Wooing of the Princess",
            "The Rip Van Winkle of the Talmud",
            "Rabbinical Romance",
            "The Shepherd's Wife",
            "The Repentant Rabbi",
            "The Inheritance",
            "Elijah in the Legends",
            "When Solomon was King",
            "Rabbinical Humor",
            "The Munchausen of the Talmud",
            "The Rabbi's Dream",
            "The Gift that Blessed",
            "In the Sweat of Thy Brow",
            "A Four-Leaved Clover",
            "The Expiation",
            "A String of Pearls",
        ],
        # text marking the end of the last tale (publisher catalogue follows)
        "end_marker": "Popular New Books",
    },

    "rapaport": {
        "label":      "rapaport_en",
        "archive_id": "talesmaximsfromm00rapa",
        "author":     "Samuel Rapaport",
        "source":     "archive.org talesmaximsfromm00rapa OCR (Tales and Maxims from the Midrash, 1907)",
        # Organised by Midrash source-book, not discrete tales. Headings are
        # ALL-CAPS in the body; match case-sensitively (also skips the TOC).
        "caps_match": True,
        # (display title, UPPERCASE match string as it appears as a body heading)
        "titles": [
            ("Alexander of Macedon",            "ALEXANDER OF MACEDON"),
            ("Demons",                          "DEMONS"),
            ("Ashmedai, the King of Demons",    "ASHMEDAI"),
            ("Messiah",                         "MESSIAH"),
            ("Genesis Rabba",                   "GENESIS RABBA"),
            ("Exodus Rabba",                    "EXODUS RABBA"),
            ("Leviticus Rabba",                 "LEVITICUS RABBA"),
            ("Numbers Rabba",                   "NUMBERS RABBA"),
            ("Deuteronomy Rabba",               "DEUTERONOMY RABBA"),
            ("Midrash Ruth",                    "MIDRASH RUTH"),
            ("Midrash Song of Songs",           "MIDRASH SONG OF SONGS"),
            ("Midrash Ecclesiastes",            "MIDRASH ECCLESIASTES"),
            ("Midrash Lamentations",            "MIDRASH LAMENTATIONS"),
            ("Midrash Esther",                  "MIDRASH ESTHER"),
            ("Midrash Psalms",                  "MIDRASH PSALMS"),
            ("Midrash Proverbs",                "MIDRASH PROVERBS"),
            ("Midrash Samuel",                  "MIDRASH SAMUEL"),
            ("Midrash Tanchumah (Yelamdinu)",   "YELAMDINU"),
        ],
        "end_marker": None,   # last chapter runs to the Index; trimmed below
        "end_marker_caps": "INDEX",
    },
}

# --------------------------------------------------------------------------- #
DOC_TEMPLATE = """\
<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link href="0.css" rel="stylesheet" type="text/css"/>
</head>
<body class="x-ebookmaker x-ebookmaker-3">
<div class="chapter">
<h2>{title}</h2>
<p class="ocr-note"><em>Source: {source} — text is OCR, lightly cleaned.</em></p>
{body}
</div>
</body>
</html>
"""


def slugify(text):
    text = re.sub(r"\s+", " ", text).strip().lower()
    for ch in ("'", "'", "'", '"', ",", ".", ":", ";", "?", "!"):
        text = text.replace(ch, "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80]


def fetch_djvu(archive_id):
    cache_path = os.path.join(CACHE, archive_id + "_djvu.txt")
    if os.path.exists(cache_path):
        raw = open(cache_path, encoding="utf-8", errors="replace").read()
    else:
        url = f"https://archive.org/stream/{archive_id}/{archive_id}_djvu.txt"
        raw = subprocess.run(["curl", "-sL", "-A", UA, url],
                             capture_output=True).stdout.decode("utf-8", "replace")
        open(cache_path, "w", encoding="utf-8").write(raw)
        time.sleep(0.5)
    m = re.search(r"<pre[^>]*>(.*)</pre>", raw, re.DOTALL | re.I)
    return htmlmod.unescape(m.group(1)) if m else raw


def title_rx(title, caps=False):
    """Matcher for an OCR'd heading. Spacing varies, so join words with \\s+.

    caps=False: case-insensitive (clean discrete-title books like Isaacs).
    caps=True:  case-sensitive on the UPPERCASE form with word boundaries, so a
                short heading like RUTH does not match body words ('untruth')
                and the mixed-case table of contents is skipped automatically.
    """
    if caps:
        pat = r"\b" + r"\s+".join(re.escape(w) for w in title.upper().split()) + r"\b"
        return re.compile(pat)
    return re.compile(r"\s+".join(re.escape(w) for w in title.split()), re.I)


def clean_ocr_body(segment, match_str, caps=False):
    """Turn an OCR text segment into cleaned <p> paragraphs."""
    # Drop the leading heading occurrence (the title itself).
    seg = title_rx(match_str, caps).sub("", segment, count=1)
    # For caps books, strip inline running heads ("GENESIS RABBA 63") globally.
    if caps:
        run = r"\b" + r"\s+".join(re.escape(w) for w in match_str.upper().split())
        seg = re.sub(run + r"(\s+\d+)?\b", " ", seg)

    lines = seg.splitlines()
    kept = []
    title_upper = re.sub(r"\s+", " ", match_str).upper()
    for ln in lines:
        s = ln.strip()
        if not s:
            kept.append("")               # paragraph break
            continue
        # Drop standalone page numbers, END markers, and running-head titles.
        if re.fullmatch(r"[\dIVXLCM]{1,4}\.?", s):
            continue
        if re.fullmatch(r"(THE\s+)?END\.?", s, re.I):
            continue
        if re.sub(r"\s+", " ", s).upper().strip(".") == title_upper.strip("."):
            continue
        kept.append(s)

    # Join lines into paragraphs (blank line = paragraph boundary); mend hyphenation.
    paras, cur = [], []
    for ln in kept:
        if ln == "":
            if cur:
                paras.append(" ".join(cur)); cur = []
        else:
            cur.append(ln)
    if cur:
        paras.append(" ".join(cur))

    out = []
    for p in paras:
        p = re.sub(r"(\w)-\s+(\w)", r"\1\2", p)     # mend hyphenated breaks
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) < 3:
            continue
        out.append("<p>" + htmlmod.escape(p) + "</p>")
    return "\n".join(out)


def process(key):
    spec = BOOKS[key]
    label = spec["label"]
    out_dir = os.path.join(PROJ, "corpus", label)
    os.makedirs(out_dir, exist_ok=True)
    css = os.path.join(out_dir, "0.css")
    if not os.path.exists(css):
        open(css, "w", encoding="utf-8").write("/* OCR source: no CSS */\n")
    for old in (f for f in os.listdir(out_dir) if f.endswith(".html")):
        os.remove(os.path.join(out_dir, old))

    print(f"\n=== {key} ({label}) ===")
    caps = spec.get("caps_match", False)
    txt = fetch_djvu(spec["archive_id"])
    if spec.get("end_marker"):
        em = title_rx(spec["end_marker"]).search(txt)   # whitespace-flexible
        if em:
            txt = txt[:em.start()]
    if spec.get("end_marker_caps"):
        # Trim at the FIRST occurrence of an all-caps back-matter marker
        # (e.g. the start of the INDEX), but only in the document's tail to
        # avoid a stray early all-caps match.
        ms = list(title_rx(spec["end_marker_caps"], caps=True).finditer(txt))
        ms = [m for m in ms if m.start() > len(txt) * 0.5]
        if ms:
            txt = txt[:ms[0].start()]

    # Normalise titles to (display, match_str) pairs.
    titles = [t if isinstance(t, tuple) else (t, t) for t in spec["titles"]]

    # Locate each heading position in sequence.
    positions = []
    first_occ = list(title_rx(titles[0][1], caps).finditer(txt))
    if caps:
        cursor = first_occ[0].start() if first_occ else 0      # caps skips TOC
    else:
        cursor = first_occ[1].start() if len(first_occ) > 1 else (
                 first_occ[0].start() if first_occ else 0)      # skip 1 TOC hit
    for disp, match_str in titles:
        m = title_rx(match_str, caps).search(txt, cursor)
        if not m:
            print(f"  !! heading not found in body: {disp}")
            positions.append(None)
            continue
        positions.append(m.start())
        cursor = m.end()

    count = 0
    for i, (disp, match_str) in enumerate(titles):
        if positions[i] is None:
            continue
        start = positions[i]
        end = len(txt)
        for j in range(i + 1, len(titles)):
            if positions[j] is not None:
                end = positions[j]; break
        body = clean_ocr_body(txt[start:end], match_str, caps)
        if not body:
            print(f"  !! empty body: {disp}")
            continue
        count += 1
        fn = f"{count:03d}_{slugify(disp)}.html"
        content = DOC_TEMPLATE.format(
            title=htmlmod.escape(disp), source=htmlmod.escape(spec["source"]), body=body)
        open(os.path.join(out_dir, fn), "w", encoding="utf-8").write(content)
        print(f"  {fn}  <-  {disp}  ({body.count('<p>')} paras)")
    print(f"  {count} tales written to corpus/{label}/")
    return count


keys = sys.argv[1:] or list(BOOKS.keys())
total = sum(process(k) for k in keys if k in BOOKS)
print(f"\nTotal: {total} tales. Run scripts/build_manifest.py to update the index.")
