"""
Fetch and split two public-domain Jewish folk-tale collections from Project
Gutenberg into per-tale HTML files that match the corpus format used for
grimm_en / andersen_en.

Collections produced
--------------------
landa_en       - Gertrude Landa, "Jewish Fairy Tales and Legends" (Gutenberg #26711)
                 26 tales drawn from Talmud/Midrash & Yiddish folk tradition.
                 Illustrated by H. Coelho Seixas (London: Shapiro, Vallentine, 1919).

friedlander_en - Gerald Friedlander & Beatrice Hirschfeld, "Jewish Fairy Stories"
                 (Gutenberg #72880)
                 8 tales sourced from Babylonian Talmud, Yalkut Shimoni, etc.

Usage
-----
    python scripts/fetch_yiddish.py

Re-running is idempotent: cached HTML is reused, existing corpus files are
overwritten only if the Gutenberg source changed.
"""

import os, re, time, html as htmlmod, subprocess, shutil

# ---------------------------------------------------------------------------
PROJ  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(PROJ, ".cache", "yiddish")
UA    = "fairy-tales-research/1.0 (daniel.hiterer@gmail.com)"
os.makedirs(CACHE, exist_ok=True)

SOURCES = [
    {
        "label":    "landa_en",
        "url":      "https://www.gutenberg.org/files/26711/26711-h/26711-h.htm",
        "cache":    "26711.html",
        "author":   "Gertrude Landa",
        "language": "en",
        "source":   "Gutenberg #26711 (Landa)",
        "title_tag":  "h2",
        "skip_ids":   {"toc", "toi", "preface", "colophon"},
        # Front matter: title page ("Jewish Fairy Tales") and narrator byline
        "skip_re":    re.compile(
            r"^[\"'“‘]?(jewish fairy tales.*|aunt naomi|contents|"
            r"table of contents|illustrations?|preface|introduction|notes?|"
            r"bibliography|colophon|index)[\"'”’]?\s*$", re.I),
        # Strip nav spans like <span class="totoc">...</span> from titles
        "strip_span_re": re.compile(r'<span[^>]*class="totoc"[^>]*>.*?</span>', re.DOTALL | re.I),
    },
    {
        "label":    "friedlander_en",
        "url":      "https://www.gutenberg.org/files/72880/72880-h/72880-h.htm",
        "cache":    "72880.html",
        "author":   "Gerald Friedlander",
        "language": "en",
        "source":   "Gutenberg #72880 (Friedlander)",
        "title_tag":  "h2",
        "skip_ids":   {"toc", "toi"},
        "skip_re":    re.compile(
            r"^(contents|table of contents|list of illustrations|preface|"
            r"introduction|notes?|bibliography|colophon)\s*$", re.I),
        "strip_span_re": None,
        # Friedlander titles are ALL CAPS — convert to title case
        "titlecase": True,
    },
]

# ---------------------------------------------------------------------------
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
{body}
</body>
</html>
"""


def fetch_url(url, cache_path):
    if os.path.exists(cache_path):
        return open(cache_path, encoding="utf-8", errors="replace").read()
    raw = subprocess.run(
        ["curl", "-sL", "-A", UA, url], capture_output=True
    ).stdout
    text = raw.decode("utf-8", "replace")
    open(cache_path, "w", encoding="utf-8").write(text)
    time.sleep(0.5)
    return text


def slugify(text):
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = text.replace("'", "").replace("’", "").replace("‘", "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def tag_text(raw_tag):
    """Strip HTML tags, collapse whitespace, and unescape entities."""
    stripped = re.sub(r"<[^>]+>", "", raw_tag)
    return htmlmod.unescape(re.sub(r"\s+", " ", stripped)).strip()


def split_into_tales(html_src, title_tag, skip_ids, skip_re,
                     strip_span_re=None, titlecase=False):
    """
    Split a full-book HTML string into a list of (title_str, body_html) pairs.

    The body of tale N is everything from its title heading up to (not
    including) the next title heading at the same level.
    """
    html_src = re.sub(r"<(script|style)\b.*?</\1>", "", html_src,
                      flags=re.DOTALL | re.I)

    TAG_RE = re.compile(
        r"<" + title_tag + r"(\b[^>]*)>(.*?)</" + title_tag + r">",
        re.DOTALL | re.I,
    )

    matches = list(TAG_RE.finditer(html_src))
    tales = []
    for i, m in enumerate(matches):
        attrs = m.group(1)
        inner = m.group(2)

        # Strip navigation spans (e.g. <span class="totoc">ToC</span>)
        if strip_span_re:
            inner = strip_span_re.sub("", inner)

        title = tag_text(inner)

        # Convert ALL CAPS titles to Title Case if requested
        if titlecase and title == title.upper():
            title = title.title()

        # Skip by id attribute
        id_m = re.search(r'\bid=["\']([^"\']+)["\']', attrs, re.I)
        tag_id = id_m.group(1).lower() if id_m else ""
        if tag_id in skip_ids:
            continue

        # Skip by title text
        if skip_re.match(title):
            continue

        # Body is from this heading's start to the next heading's start (or EOF)
        body_start = m.start()
        body_end   = matches[i + 1].start() if i + 1 < len(matches) else len(html_src)
        body_html  = html_src[body_start:body_end].strip()

        # Apply strip_span_re to body as well so inline nav links don't appear
        if strip_span_re:
            body_html = strip_span_re.sub("", body_html)

        tales.append((title, body_html))

    return tales


def write_collection(spec):
    label          = spec["label"]
    url            = spec["url"]
    cache_fn       = spec["cache"]
    title_tag      = spec["title_tag"]
    skip_ids       = spec["skip_ids"]
    skip_re        = spec["skip_re"]
    strip_span_re  = spec.get("strip_span_re")
    titlecase      = spec.get("titlecase", False)

    out_dir = os.path.join(PROJ, "corpus", label)
    os.makedirs(out_dir, exist_ok=True)

    css_stub = "/* Gutenberg source: no bundled CSS */\n"
    css_path = os.path.join(out_dir, "0.css")
    if not os.path.exists(css_path):
        open(css_path, "w", encoding="utf-8").write(css_stub)

    print(f"\n=== {label} ===")
    cache_path = os.path.join(CACHE, cache_fn)
    src = fetch_url(url, cache_path)

    tales = split_into_tales(src, title_tag, skip_ids, skip_re,
                             strip_span_re=strip_span_re, titlecase=titlecase)
    print(f"  Found {len(tales)} tales")

    # Remove previously generated files so stale ones don't linger
    for old in (f for f in os.listdir(out_dir) if f.endswith(".html") and f != "0.css"):
        os.remove(os.path.join(out_dir, old))

    for seq, (title, body) in enumerate(tales, start=1):
        slug     = slugify(title) or f"tale-{seq}"
        filename = f"{seq:03d}_{slug}.html"
        path     = os.path.join(out_dir, filename)
        html_out = DOC_TEMPLATE.format(title=title, body=body)
        open(path, "w", encoding="utf-8").write(html_out)
        print(f"  {filename}  <-  {title}")

    print(f"  {len(tales)} files written to corpus/{label}/")


for spec in SOURCES:
    write_collection(spec)

print("\nDone. Run scripts/build_manifest.py to update the index.")
