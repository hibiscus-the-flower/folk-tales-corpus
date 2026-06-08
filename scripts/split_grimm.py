import re
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
OEBPS = os.path.join(BASE, "_g", "OEBPS")
OUT = os.path.join(BASE, "tales_grimm")
TOC = os.path.join(OEBPS, "toc.xhtml")

BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.DOTALL)
LINK_RE = re.compile(r'<a href="([^"#]+)(?:#[^"]*)?"[^>]*>(.*?)</a>', re.DOTALL)

DOC = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link href="0.css" rel="stylesheet" type="text/css"/>
<link href="1.css" rel="stylesheet" type="text/css"/>
<link href="pgepub.css" rel="stylesheet" type="text/css"/>
</head>
<body class="x-ebookmaker x-ebookmaker-3">
{body}
</body>
</html>
"""


def clean_title(raw):
    raw = re.sub(r"<[^>]+>", "", raw)
    return re.sub(r"\s+", " ", raw).strip()


def slugify(text):
    text = text.lower().replace("’", "").replace("'", "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


toc = open(TOC, encoding="utf-8").read()
# Keep only real story entries: "12 Rapunzel" or "Legend 6 The Three Green Twigs".
entries = []
seen = set()
for href, raw in LINK_RE.findall(toc):
    title = clean_title(raw)
    if not re.match(r"^(?:Legend )?\d+\s", title):
        continue
    if href in seen:
        continue
    seen.add(href)
    entries.append((href, title))

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for css in ("0.css", "1.css", "pgepub.css"):
    src = os.path.join(OEBPS, css)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, css))

seq = 0
for href, title in entries:
    text = open(os.path.join(OEBPS, href), encoding="utf-8").read()
    m = BODY_RE.search(text)
    body = m.group(1).strip() if m else ""
    seq += 1
    fn = f"{seq:03d}_{slugify(title)}.html"
    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        f.write(DOC.format(title=title, body=body))

print(f"{seq} Grimm tales written to {OUT}")
print("first:", entries[0][1])
print("last :", entries[-1][1])
