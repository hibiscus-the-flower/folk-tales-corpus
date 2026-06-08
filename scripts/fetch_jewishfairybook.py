"""
Fetch the full English text of *The Jewish Fairy Book* (Gerald Friedlander,
London: Routledge / New York: Dutton, 1920) from English Wikisource and split
it into per-tale HTML files matching the corpus format.

23 tales, retold from Talmud / Midrash / medieval Jewish folk tradition.
Public domain (Friedlander d. 1923; work published 1920).

Source index:
  https://en.wikisource.org/wiki/The_Jewish_Fairy_Book_(Gerald_Friedlander)

Output collection: corpus/jewish_fairy_book_en/

Usage:
    python3 scripts/fetch_jewishfairybook.py
"""

import os, re, time, json, html as htmlmod, subprocess, urllib.parse

PROJ    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJ, "corpus", "jewish_fairy_book_en")
CACHE   = os.path.join(PROJ, ".cache", "yiddish")
UA      = "fairy-tales-research/1.0 (daniel.hiterer@gmail.com)"
API     = "https://en.wikisource.org/w/api.php"
BASE    = "The_Jewish_Fairy_Book_(Gerald_Friedlander)"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)

# Tale title -> Wikisource subpage name (order as printed in the book).
TALES = [
    ("The Magic Apples",              "The_Magic_Apples"),
    ("The Wise Merchant",             "The_Wise_Merchant"),
    ("Heavenly Treasures",            "Heavenly_Treasures"),
    ("King Solomon's Carpet",         "King_Solomon's_Carpet"),
    ("The Magic Lamp",                "The_Magic_Lamp"),
    ("Chanina and the Angels",        "Chanina_and_the_Angels"),
    ("The Wonderful Slave",           "The_Wonderful_Slave"),
    ("About Leviathan, King of the Fish", "About_Leviathan,_King_of_the_Fish"),
    ("The Demon's Marriage",          "The_Demon's_Marriage"),
    ("The Magic Leaf",                "The_Magic_Leaf"),
    ("The Prince and the Rabbi",      "The_Prince_and_the_Rabbi"),
    ("The Princess and the Beggar",   "The_Princess_and_the_Beggar"),
    ("The Castle in the Air",         "The_Castle_in_the_Air"),
    ("The Citizen of the World",      "The_Citizen_of_the_World"),
    ("The Snake's Thanks",            "The_Snake's_Thanks"),
    ("The Rebellious Waters",         "The_Rebellious_Waters"),
    ("The Goblin and the Princess",   "The_Goblin_and_the_Princess"),
    ("Iron and the Trees",            "Iron_and_the_Trees"),
    ("David and the Insects",         "David_and_the_Insects"),
    ("The First Vineyard",            "The_First_Vineyard"),
    ("Abraham's Tree",                "Abraham's_Tree"),
    ("Joseph, the Sabbath Lover",     "Joseph,_the_Sabbath_Lover"),
    ("The Magic Sword of Kenaz",      "The_Magic_Sword_of_Kenaz"),
]

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
    for ch in ("'", "'", "'", ",", ".", ":", "?", "!"):
        text = text.replace(ch, "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def api_parse(page):
    """Return the parsed HTML of a Wikisource page via the MediaWiki API."""
    cache_fn = "wikisource_" + re.sub(r"[^A-Za-z0-9]+", "_", page) + ".json"
    cache_path = os.path.join(CACHE, cache_fn)
    if os.path.exists(cache_path):
        data = json.load(open(cache_path, encoding="utf-8"))
    else:
        params = {
            "action": "parse", "page": page, "format": "json",
            "prop": "text", "formatversion": "2",
        }
        url = API + "?" + urllib.parse.urlencode(params)
        raw = subprocess.run(["curl", "-sL", "-A", UA, url],
                             capture_output=True).stdout
        data = json.loads(raw.decode("utf-8", "replace"))
        json.dump(data, open(cache_path, "w", encoding="utf-8"))
        time.sleep(0.4)
    return data.get("parse", {}).get("text", "")


def clean_body(raw_html, title):
    """Keep only the readable prose: <p> paragraphs from mw-parser-output."""
    # Strip embedded <style> (TemplateStyles) blocks up front.
    raw_html = re.sub(r"<style\b.*?</style>", "", raw_html,
                      flags=re.DOTALL | re.I)
    paras = re.findall(r"<p\b[^>]*>.*?</p>", raw_html, re.DOTALL | re.I)

    title_caps = re.sub(r"\s+", " ", title).strip().upper()
    out = []
    for p in paras:
        # Remove edit-section markers, references, and sup/sub noise.
        p = re.sub(r"<sup\b.*?</sup>", "", p, flags=re.DOTALL | re.I)
        p = re.sub(r'<span class="mw-editsection".*?</span>', "", p,
                   flags=re.DOTALL | re.I)
        # Strip all attributes from <a> tags, keep the link text only.
        p = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", p, flags=re.DOTALL | re.I)

        text = re.sub(r"<[^>]+>", "", p)
        text = htmlmod.unescape(re.sub(r"\s+", " ", text)).strip()
        if not text:
            continue
        # Skip running heads: a lone Roman/arabic chapter number, or the
        # repeated ALL-CAPS tale title printed at the top of the chapter.
        if re.fullmatch(r"[IVXLCM\d]+\.?", text):
            continue
        if text.upper().rstrip(".") == title_caps.rstrip("."):
            continue
        out.append(p.strip())
    return "\n".join(out)


# minimal CSS stub
css_path = os.path.join(OUT_DIR, "0.css")
if not os.path.exists(css_path):
    open(css_path, "w", encoding="utf-8").write("/* Wikisource source: no CSS */\n")

# clear stale html
for old in (f for f in os.listdir(OUT_DIR) if f.endswith(".html")):
    os.remove(os.path.join(OUT_DIR, old))

count = 0
for seq, (title, subpage) in enumerate(TALES, start=1):
    page = BASE + "/" + subpage
    raw  = api_parse(page)
    body = clean_body(raw, title)
    if not body:
        print(f"  !! no body extracted for {title} ({page})")
        continue
    slug     = slugify(title) or f"tale-{seq}"
    filename = f"{seq:03d}_{slug}.html"
    content  = DOC_TEMPLATE.format(title=htmlmod.escape(title), body=body)
    open(os.path.join(OUT_DIR, filename), "w", encoding="utf-8").write(content)
    n_paras = body.count("<p")
    print(f"  {filename}  <-  {title}  ({n_paras} paras)")
    count += 1

print(f"\n{count} tales written to corpus/jewish_fairy_book_en/")
print("Run scripts/build_manifest.py to update the index.")
