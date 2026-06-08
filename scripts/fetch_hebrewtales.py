"""
Fetch the full English text of *Hebrew Tales: Selected and Translated from the
Writings of the Ancient Hebrew Sages* (Hyman Hurwitz, 1826; this ed. via English
Wikisource) and split it into per-tale HTML files matching the corpus format.

~64 short tales, parables, fables, and facetiae translated from Talmud / Midrash
(three of them furnished by S. T. Coleridge). Public domain (Hurwitz d. 1844).

Source (single transcluded page on Wikisource):
  https://en.wikisource.org/wiki/Hebrew_tales;_selected_and_translated_from_the_writings_of_the_ancient_Hebrew_sages

The page has no HTML headings; each tale begins with a standalone <b>Title</b>
paragraph (often with a subtitle), optionally followed by a scriptural epigraph,
then the body. We segment on those bold markers.

Output collection: corpus/hebrew_tales_en/

Usage:
    python3 scripts/fetch_hebrewtales.py
"""

import os, re, time, json, html as htmlmod, subprocess, urllib.parse

PROJ    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJ, "corpus", "hebrew_tales_en")
CACHE   = os.path.join(PROJ, ".cache", "yiddish")
UA      = "fairy-tales-research/1.0 (daniel.hiterer@gmail.com)"
API     = "https://en.wikisource.org/w/api.php"
PAGE    = ("Hebrew_tales;_selected_and_translated_from_the_writings_"
           "of_the_ancient_Hebrew_sages")

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


def tag_text(raw):
    return htmlmod.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw))).strip()


def api_parse(page):
    cache_path = os.path.join(CACHE, "hurwitz_raw.json")
    if os.path.exists(cache_path):
        data = json.load(open(cache_path, encoding="utf-8"))
    else:
        params = {"action": "parse", "page": page, "format": "json",
                  "prop": "text", "formatversion": "2"}
        url = API + "?" + urllib.parse.urlencode(params)
        raw = subprocess.run(["curl", "-sL", "-A", UA, url],
                             capture_output=True).stdout
        data = json.loads(raw.decode("utf-8", "replace"))
        json.dump(data, open(cache_path, "w", encoding="utf-8"))
        time.sleep(0.4)
    return data.get("parse", {}).get("text", "")


def clean_body(segment, title):
    """Extract readable <p> prose from a tale segment, dropping the title line."""
    segment = re.sub(r"<style\b.*?</style>", "", segment, flags=re.DOTALL | re.I)
    paras = re.findall(r"<p\b[^>]*>.*?</p>", segment, re.DOTALL | re.I)
    title_norm = re.sub(r"\s+", " ", title).strip().lower()
    out = []
    for p in paras:
        p = re.sub(r"<sup\b.*?</sup>", "", p, flags=re.DOTALL | re.I)
        p = re.sub(r'<span class="mw-editsection".*?</span>', "", p,
                   flags=re.DOTALL | re.I)
        # Drop Wikisource page-number anchor spans.
        p = re.sub(r'<span[^>]*class="[^"]*pagenum[^"]*"[^>]*>.*?</span>', "", p,
                   flags=re.DOTALL | re.I)
        p = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", p, flags=re.DOTALL | re.I)
        text = tag_text(p)
        if not text:
            continue
        # Drop the leading title paragraph (rendered separately as <h2>).
        if text.lower() == title_norm:
            continue
        # Drop lone section numerals.
        if re.fullmatch(r"[IVXLCM]+\.?", text):
            continue
        out.append(p.strip())
    return "\n".join(out)


raw = api_parse(PAGE)

# Trim the Wikisource license footer.
m = re.search(r"This work was published before", raw)
if m:
    raw = raw[:m.start()]

# Body starts at the SECOND occurrence of the first tale title (the first is in
# the CONTENTS table).
first = "Moses and the Lamb"
p1 = raw.find(first)
p2 = raw.find(first, p1 + 1)
body_region = raw[p2 - 200:] if p2 != -1 else raw

# All standalone bold markers = tale-title boundaries.
BOLD_RE = re.compile(r"<b>(.*?)</b>", re.DOTALL)
boundaries = []
for m in BOLD_RE.finditer(body_region):
    title = tag_text(m.group(1))
    if not title or re.fullmatch(r"[IVXLCM]+\.?", title):
        continue
    boundaries.append((m.start(), title))

# minimal CSS stub
css_path = os.path.join(OUT_DIR, "0.css")
if not os.path.exists(css_path):
    open(css_path, "w", encoding="utf-8").write("/* Wikisource source: no CSS */\n")
for old in (f for f in os.listdir(OUT_DIR) if f.endswith(".html")):
    os.remove(os.path.join(OUT_DIR, old))

count = 0
for i, (pos, title) in enumerate(boundaries):
    end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(body_region)
    segment = body_region[pos:end]
    body = clean_body(segment, title)
    if not body:
        print(f"  !! empty body: {title}")
        continue
    seq = count + 1
    slug = slugify(title) or f"tale-{seq}"
    filename = f"{seq:03d}_{slug}.html"
    content = DOC_TEMPLATE.format(title=htmlmod.escape(title), body=body)
    open(os.path.join(OUT_DIR, filename), "w", encoding="utf-8").write(content)
    print(f"  {filename}  <-  {title[:60]}")
    count += 1

print(f"\n{count} tales written to corpus/hebrew_tales_en/")
print("Run scripts/build_manifest.py to update the index.")
