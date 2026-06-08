"""
folktale_lib — shared plumbing for the folktale-harvester skill.

Every per-source fetcher in this project ends up needing the same handful of
primitives: a consistent per-tale HTML wrapper, a slugifier, a cached HTTP GET,
the Wikisource MediaWiki `action=parse` call, an archive.org djvu.txt grabber,
and a couple of cleaners that turn messy source HTML/OCR into tidy <p> prose.

Rather than re-deriving these for each culture, import them from here. The goal
is that a new fetcher is *thin* — mostly the list of titles/pages specific to a
book — because the fiddly, error-prone parts live in one tested place.

Output convention (matches the existing corpus):
  corpus/<collection>/NNN_<slug>.html   one file per tale, zero-padded sequence
  corpus/<collection>/0.css             a stub stylesheet

All texts must be PUBLIC DOMAIN. This library does not and cannot check that —
that judgement happens before you call it (see references/copyright.md).
"""

import os
import re
import csv
import time
import json
import html as htmlmod
import subprocess
import urllib.parse

# Project root = three levels up from this file
# (.claude/skills/folktale-harvester/scripts/folktale_lib.py -> project root).
PROJ = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
CORPUS = os.path.join(PROJ, "corpus")
CACHE = os.path.join(PROJ, ".cache", "harvester")
UA = "fairy-tales-research/1.0 (daniel.hiterer@gmail.com)"

os.makedirs(CACHE, exist_ok=True)

# Per-tale HTML wrapper. Kept byte-compatible with the existing corpus so the
# manifest builder, dedup, and any downstream tooling see a uniform shape.
DOC_TEMPLATE = """\
<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{lang}">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link href="0.css" rel="stylesheet" type="text/css"/>
</head>
<body class="x-ebookmaker x-ebookmaker-3">
<div class="chapter">
<h2>{title}</h2>
{note}{body}
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# Filenames & text
# --------------------------------------------------------------------------- #
def slugify(text, maxlen=80):
    """A filename-safe, lowercase, hyphenated slug. Empty -> '' (caller fallback)."""
    text = re.sub(r"\s+", " ", text).strip().lower()
    for ch in ("'", "’", "‘", '"', ",", ".", ":", ";", "?", "!"):
        text = text.replace(ch, "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:maxlen]


def clean_text(raw):
    """Strip tags, unescape entities, collapse whitespace -> plain string."""
    return htmlmod.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw))).strip()


def norm_title(t):
    """Loose title key for matching across sources (drops leading article/punct)."""
    t = t.lower()
    t = re.sub(r"^(the|a|an)\s+", "", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# --------------------------------------------------------------------------- #
# Cached HTTP (curl, so it behaves like the rest of the project's fetchers)
# --------------------------------------------------------------------------- #
def http_get(url, cache_key=None, pause=0.3):
    """GET a URL, caching the raw body under .cache/harvester. Polite by default."""
    if cache_key is None:
        cache_key = re.sub(r"[^A-Za-z0-9]+", "_", url)[:150]
    path = os.path.join(CACHE, cache_key)
    if os.path.exists(path):
        return open(path, encoding="utf-8", errors="replace").read()
    raw = subprocess.run(["curl", "-sL", "-A", UA, url],
                         capture_output=True).stdout
    body = raw.decode("utf-8", "replace")
    open(path, "w", encoding="utf-8").write(body)
    time.sleep(pause)
    return body


def wikisource_parse(page, lang="en"):
    """Return parsed HTML of a Wikisource page via the MediaWiki action=parse API.

    This is the clean way to harvest Wikisource — it gives rendered prose without
    scraping the skin. `page` is the full page title, e.g.
    "The_Jewish_Fairy_Book_(Gerald_Friedlander)/The_Magic_Apples".
    """
    api = f"https://{lang}.wikisource.org/w/api.php"
    params = {"action": "parse", "page": page, "format": "json",
              "prop": "text", "formatversion": "2"}
    url = api + "?" + urllib.parse.urlencode(params)
    key = f"ws_{lang}_" + re.sub(r"[^A-Za-z0-9]+", "_", page) + ".json"
    raw = http_get(url, cache_key=key, pause=0.4)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return ""
    return data.get("parse", {}).get("text", "")


def archive_djvu(archive_id):
    """Return the OCR plain text of an archive.org item (its *_djvu.txt)."""
    url = f"https://archive.org/stream/{archive_id}/{archive_id}_djvu.txt"
    raw = http_get(url, cache_key=archive_id + "_djvu.txt", pause=0.5)
    m = re.search(r"<pre[^>]*>(.*)</pre>", raw, re.DOTALL | re.I)
    return htmlmod.unescape(m.group(1)) if m else raw


# --------------------------------------------------------------------------- #
# Cleaners: messy source -> tidy list of <p> paragraphs
# --------------------------------------------------------------------------- #
def html_to_paragraphs(raw_html, drop_title=None):
    """Extract readable <p> prose from a chunk of source HTML.

    Handles the usual Wikisource/Gutenberg cruft: <style>/<sup> footnote markers,
    edit-section spans, and link wrappers (kept as plain text). Skips running
    heads — a lone chapter number, or the tale title repeated at the top.
    """
    raw_html = re.sub(r"<style\b.*?</style>", "", raw_html, flags=re.DOTALL | re.I)
    title_caps = re.sub(r"\s+", " ", drop_title).strip().upper() if drop_title else None
    out = []
    for p in re.findall(r"<p\b[^>]*>.*?</p>", raw_html, re.DOTALL | re.I):
        p = re.sub(r"<sup\b.*?</sup>", "", p, flags=re.DOTALL | re.I)
        p = re.sub(r'<span class="mw-editsection".*?</span>', "", p,
                   flags=re.DOTALL | re.I)
        p = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", p, flags=re.DOTALL | re.I)
        text = clean_text(p)
        if not text:
            continue
        if re.fullmatch(r"[IVXLCM\d]+\.?", text):
            continue
        if title_caps and text.upper().rstrip(".") == title_caps.rstrip("."):
            continue
        out.append(p.strip())
    return "\n".join(out)


def ocr_to_paragraphs(segment, drop_heading=None):
    """Turn a raw OCR text segment into cleaned <p> paragraphs.

    OCR has no markup, so paragraphs are inferred from blank lines, hyphenated
    line-breaks are mended, and page numbers / END markers / repeated running
    heads are dropped. Lower fidelity than HTML sources — flag it in the note.
    """
    if drop_heading:
        rx = re.compile(r"\s+".join(re.escape(w) for w in drop_heading.split()), re.I)
        segment = rx.sub("", segment, count=1)
    title_upper = re.sub(r"\s+", " ", drop_heading).upper() if drop_heading else None

    kept = []
    for ln in segment.splitlines():
        s = ln.strip()
        if not s:
            kept.append("")
            continue
        if re.fullmatch(r"[\dIVXLCM]{1,4}\.?", s):
            continue
        if re.fullmatch(r"(THE\s+)?END\.?", s, re.I):
            continue
        if title_upper and re.sub(r"\s+", " ", s).upper().strip(".") == title_upper.strip("."):
            continue
        kept.append(s)

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
        p = re.sub(r"(\w)-\s+(\w)", r"\1\2", p)       # mend hyphenation
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) < 3:
            continue
        out.append("<p>" + htmlmod.escape(p) + "</p>")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Writing tales
# --------------------------------------------------------------------------- #
def write_collection(collection, tales, lang="en", note=None, fresh=True):
    """Write a list of tales to corpus/<collection>/ as NNN_<slug>.html.

    `tales` is a list of (title, body_html) pairs already containing <p> tags.
    `note` is an optional provenance line (e.g. an OCR-fidelity warning) inserted
    under the <h2> of every tale. Returns the number of files written.
    """
    out_dir = os.path.join(CORPUS, collection)
    os.makedirs(out_dir, exist_ok=True)
    css = os.path.join(out_dir, "0.css")
    if not os.path.exists(css):
        open(css, "w", encoding="utf-8").write("/* harvested source: no CSS */\n")
    if fresh:
        for old in (f for f in os.listdir(out_dir) if f.endswith(".html")):
            os.remove(os.path.join(out_dir, old))

    note_html = ""
    if note:
        note_html = f'<p class="src"><em>{htmlmod.escape(note)}</em></p>\n'

    # Detailed per-tale list goes to a log file, not to stdout, so a run does not
    # spend model-context tokens echoing dozens of filenames. The terminal gets a
    # compact summary plus any warnings (the part you actually need to see).
    log_lines, written, count = [], [], 0
    for title, body in tales:
        if not body or not body.strip():
            print(f"  !! empty body, skipped: {title}")
            continue
        count += 1
        slug = slugify(title) or f"tale-{count}"
        fn = f"{count:03d}_{slug}.html"
        content = DOC_TEMPLATE.format(
            lang=lang, title=htmlmod.escape(title), note=note_html, body=body)
        open(os.path.join(out_dir, fn), "w", encoding="utf-8").write(content)
        log_lines.append(f"{fn}  <-  {title}  ({body.count('<p')} paras)")
        written.append((fn, title))

    log_path = os.path.join(CACHE, f"{collection}_harvest.log")
    open(log_path, "w", encoding="utf-8").write("\n".join(log_lines) + "\n")

    if written:
        first = f"{written[0][0]} «{written[0][1]}»"
        last = f"{written[-1][0]} «{written[-1][1]}»"
        print(f"  {collection}: {count} tales  [{first} … {last}]")
        print(f"  detail -> .cache/harvester/{collection}_harvest.log")
    else:
        print(f"  {collection}: 0 tales written")
    return count


def record_source(collection, author, source, language="en", culture=None):
    """Append a provenance row to index/harvested_sources.csv.

    A lightweight ledger so build_manifest.py (and you) can see, per collection,
    who wrote it, where it came from, and which culture it belongs to. Idempotent
    on `collection` — re-running a fetch updates the existing row.
    """
    path = os.path.join(PROJ, "index", "harvested_sources.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = ["collection", "author", "language", "culture", "source"]
    rows = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path, encoding="utf-8")):
            rows[r["collection"]] = r
    rows[collection] = {"collection": collection, "author": author,
                        "language": language, "culture": culture or "",
                        "source": source}
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for c in sorted(rows):
            w.writerow(rows[c])
    print(f"  recorded provenance: {collection} -> index/harvested_sources.csv")
