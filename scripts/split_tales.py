import re
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
OEBPS = os.path.join(BASE, "_x", "OEBPS")
OUT = os.path.join(BASE, "tales_complete")
PREFIX = "3315690094809976166_27200-h-"

# Tales live in spine files h-0 .. h-13 (h-14 is a note, h-15 the license).
CONTENT_FILES = [f"{PREFIX}{i}.htm.xhtml" for i in range(0, 14)]

# Front matter that is not a tale: title page, CONTENTS heading, contents blob.
SKIP_FRONT = {0, 1, 2}

# Anchors that are sub-parts of a larger tale (chapters / evenings / stories /
# days / visits) and therefore must stay embedded, not start a new file.
SUBPART = (
    {17}                       # "A Cheerful Temper" inner section
    | set(range(39, 44))       # The Goloshes of Fortune: 5 chapters
    | set(range(52, 66))       # The Ice Maiden: chapters II-XV
    | set(range(83, 115))      # What the Moon Saw: 32 evenings
    | set(range(126, 133))     # Ole-Luk-Oie: Monday-Sunday
    | {134, 135, 136}          # Ole the Tower-keeper: three visits
    | set(range(162, 169))     # The Snow Queen: seven stories
    | {172, 173, 174, 175}     # Soup from a Sausage Skewer: the mice + finale
)

BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.DOTALL)
STRAY_RE = re.compile(r"<(?:link|meta)\b[^>]*/?>", re.IGNORECASE)
HEAD_RE = re.compile(r'<h([1-6])\b[^>]*id="pgepubid(\d+)"[^>]*>(.*?)</h\1>', re.DOTALL)

DOC_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link href="0.css" rel="stylesheet" type="text/css"/>
<link href="1.css" rel="stylesheet" type="text/css"/>
<link href="2.css" rel="stylesheet" type="text/css"/>
<link href="pgepub.css" rel="stylesheet" type="text/css"/>
</head>
<body class="x-ebookmaker x-ebookmaker-3">
{body}
</body>
</html>
"""


def slugify(text):
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = text.replace("'", "").replace("’", "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def clean_title(raw):
    return re.sub(r"\s+", " ", raw).strip()


# Concatenate the inner <body> flow of every content file, in order.
chunks = []
for fname in CONTENT_FILES:
    with open(os.path.join(OEBPS, fname), encoding="utf-8") as f:
        text = f.read()
    m = BODY_RE.search(text)
    inner = m.group(1) if m else ""
    inner = STRAY_RE.sub("", inner)
    chunks.append(inner)
big = "\n".join(chunks)

# Every heading in document order, with the numeric id and its start offset.
headings = [(int(m.group(2)), clean_title(m.group(3)), m.start())
            for m in HEAD_RE.finditer(big)]

# Tale starts: anything that isn't front matter and isn't a sub-part.
starts = [(num, title, pos) for (num, title, pos) in headings
          if num not in SKIP_FRONT and num not in SUBPART]
start_positions = [pos for (_, _, pos) in starts]

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for css in ("0.css", "1.css", "2.css", "pgepub.css"):
    src = os.path.join(OEBPS, css)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, css))

seq = 0
for i, (num, title, pos) in enumerate(starts):
    end = start_positions[i + 1] if i + 1 < len(starts) else len(big)
    body = big[pos:end].strip()
    seq += 1
    slug = slugify(title) or f"tale-{num}"
    out_name = f"{seq:03d}_{slug}.html"
    with open(os.path.join(OUT, out_name), "w", encoding="utf-8") as out:
        out.write(DOC_TEMPLATE.format(title=title, body=body))
    print(f"{out_name}  <-  {title}")

print(f"\n{seq} tales written to {OUT}")
