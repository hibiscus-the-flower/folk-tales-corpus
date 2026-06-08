"""
Fetch *The Legends of the Jews* by Louis Ginzberg (tr. Henrietta Szold,
1909-1913) from Project Gutenberg and split it into per-legend HTML files
matching the corpus format.

This is the canonical English synthesis of Jewish aggadah (legend) from the
Talmud and Midrash. Each volume is organised as H2 "books" (biblical figure /
era) containing many H3 discrete legends; we emit one file per H3 legend and
record the enclosing book as the section label.

NOTE: this is biblical/aggadic legend, a different register from East-European
oral Yiddish *mayses*; included as canonical Jewish legend, all public domain.

Narrative volumes (Gutenberg ids):
  vol 1 #1493  Bible Times and Characters from the Creation to Jacob
  vol 2 #1494  Bible Times and Characters from Joseph to the Exodus
  vol 3 #2881  Bible Times and Characters from the Exodus to the Death of Moses
  vol 4 #2882  Bible Times and Characters from Joshua to Esther
(vols 5-7 are notes/index, not tales — excluded.)

Markup differs by volume: legends are marked by an <a name="chapNN"> anchor
(inside an <h3> in vol 1, an <h2> in vols 2-4); books by <a name="bookNN">.
We classify purely by the anchor name, independent of heading level.

Output collection: corpus/ginzberg_legends_en/

Usage:
    python3 scripts/fetch_ginzberg.py            # all narrative volumes
    python3 scripts/fetch_ginzberg.py 1493       # one or more specific ids
"""

import os, re, sys, time, html as htmlmod, subprocess

PROJ    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJ, "corpus", "ginzberg_legends_en")
CACHE   = os.path.join(PROJ, ".cache", "yiddish")
UA      = "fairy-tales-research/1.0 (daniel.hiterer@gmail.com)"

VOLUMES = ["1493", "1494", "2881", "2882"]

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)

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
<p class="section-label"><em>{section}</em></p>
{body}
</div>
</body>
</html>
"""

# A "book" H2 looks like "IV<br/>NOAH" (roman numeral + title).
BOOK_RE = re.compile(r"^\s*[IVXLCM]+\b", re.I)


def fetch_vol(vid):
    cache_path = os.path.join(CACHE, f"ginzberg_v_{vid}.html")
    if os.path.exists(cache_path):
        return open(cache_path, encoding="utf-8", errors="replace").read()
    url = f"https://www.gutenberg.org/files/{vid}/{vid}-h/{vid}-h.htm"
    raw = subprocess.run(["curl", "-sL", "-A", UA, url],
                         capture_output=True).stdout
    text = raw.decode("utf-8", "replace")
    open(cache_path, "w", encoding="utf-8").write(text)
    time.sleep(0.5)
    return text


def heading_text(raw):
    """Clean a heading's inner HTML: drop <br/>, collapse whitespace."""
    txt = re.sub(r"<br\s*/?>", " ", raw, flags=re.I)
    txt = re.sub(r"<[^>]+>", "", txt)
    return htmlmod.unescape(re.sub(r"\s+", " ", txt)).strip()


def slugify(text):
    text = re.sub(r"\s+", " ", text).strip().lower()
    for ch in ("'", "'", "'", '"', ",", ".", ":", ";", "?", "!"):
        text = text.replace(ch, "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80]


def clean_body(segment):
    """Extract readable <p> prose, dropping footnote anchors and page anchors."""
    paras = re.findall(r"<p\b[^>]*>.*?</p>", segment, re.DOTALL | re.I)
    out = []
    for p in paras:
        # Drop footnote reference superscripts and their anchor links.
        p = re.sub(r"<sup\b.*?</sup>", "", p, flags=re.DOTALL | re.I)
        p = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", p, flags=re.DOTALL | re.I)
        p = re.sub(r"<a\b[^>]*/>", "", p, flags=re.I)
        # Drop leftover footnote reference markers like [43], [853].
        p = re.sub(r"\[\d+\]", "", p)
        p = re.sub(r"[ \t]{2,}", " ", p)
        text = htmlmod.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p))).strip()
        if not text:
            continue
        out.append(p.strip())
    return "\n".join(out)


vols = sys.argv[1:] or VOLUMES

# clear stale output
css_path = os.path.join(OUT_DIR, "0.css")
if not os.path.exists(css_path):
    open(css_path, "w", encoding="utf-8").write("/* Gutenberg source: no CSS */\n")
for old in (f for f in os.listdir(OUT_DIR) if f.endswith(".html")):
    os.remove(os.path.join(OUT_DIR, old))

# A heading carrying a book/chap/pref anchor, at any heading level. Captures:
#   1 = heading tag, 2 = anchor type (book|chap|pref), 3 = number, 4 = inner HTML
HEAD_RE = re.compile(
    r'<(h[2-4])\b[^>]*>\s*<a name="(book|chap|pref)(\d+)"></a>\s*(.*?)</\1>',
    re.DOTALL | re.I)

seq = 0
for vid in vols:
    print(f"\n=== volume {vid} ===")
    src = fetch_vol(vid)

    # Safety: only harvest if this really is a Ginzberg "Legends" volume.
    title_m = re.search(r"<title>(.*?)</title>", src, re.DOTALL | re.I)
    page_title = heading_text(title_m.group(1)) if title_m else ""
    if "legends of the jews" not in page_title.lower():
        print(f"  SKIP — not a Legends volume (title: {page_title!r})")
        continue

    src = re.sub(r"<(script|style)\b.*?</\1>", "", src, flags=re.DOTALL | re.I)
    m_end = re.search(r"\*\*\* END OF TH", src)
    if m_end:
        src = src[:m_end.start()]

    heads = [(m.group(2).lower(), int(m.group(3)), heading_text(m.group(4)),
              m.start(), m.end())
             for m in HEAD_RE.finditer(src)]

    # Fallback section label = the "VOLUME N ... FROM X TO Y" subtitle, for
    # volumes (e.g. vol 3) that have no <a name="bookNN"> division anchors.
    sub_m = re.search(r"<h4\b[^>]*>(.*?)</h4>", src, re.DOTALL | re.I)
    subtitle = heading_text(sub_m.group(1)) if sub_m else "The Legends of the Jews"
    current_book = subtitle

    vol_count = 0
    for i, (kind, num, title, hstart, hend) in enumerate(heads):
        if kind == "book" or (kind == "chap" and num == 0):
            # A division header (book anchor, or chap00 used as a section).
            current_book = title
            continue
        if kind == "pref":
            continue
        # kind == "chap" with num >= 1: a legend.
        body_start = hend
        body_end = heads[i + 1][3] if i + 1 < len(heads) else len(src)
        body = clean_body(src[body_start:body_end])
        if not body:
            continue
        seq += 1
        vol_count += 1
        slug = slugify(title) or f"legend-{seq}"
        filename = f"{seq:03d}_{slug}.html"
        content = DOC_TEMPLATE.format(
            title=htmlmod.escape(title),
            section=htmlmod.escape(current_book),
            body=body)
        open(os.path.join(OUT_DIR, filename), "w", encoding="utf-8").write(content)
    print(f"  {vol_count} legends from volume {vid}")

print(f"\n{seq} legends written to corpus/ginzberg_legends_en/")
print("Run scripts/build_manifest.py to update the index.")
