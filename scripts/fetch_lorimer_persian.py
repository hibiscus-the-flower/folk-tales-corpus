"""
Harvest Lorimer & Lorimer, *Persian Tales* (Macmillan, 1919) — the classic
collection of genuine oral Persian folk tales (Kermani + Bakhtiari), from the
archive.org OCR. Public domain (1919).

Irregular source → thin bespoke fetcher, as the folktale-harvester skill advises:
all the plumbing (djvu fetch, OCR cleaning, HTML writing, provenance) comes from
folktale_lib. The only book-specific logic is how tales are delimited.

Each tale's real heading in the OCR body is the line "THE STORY OF <TITLE>".
Running page-heads repeat the title but as "STORY OF <TITLE> <pageno>" (no leading
"THE"), so matching on "THE STORY OF" and keeping the FIRST occurrence of each
distinct title yields the real headings in order, free of running heads.

Usage:
    python3 scripts/fetch_lorimer_persian.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                ".claude", "skills", "folktale-harvester", "scripts"))
import folktale_lib as fl

ARCHIVE_ID = "cu31924029903881"
COLLECTION = "persian_lorimer_en"
SOURCE = "archive.org cu31924029903881 OCR — Persian Tales (Lorimer & Lorimer, 1919)"

txt = fl.archive_djvu(ARCHIVE_ID)

# Drop the front matter / TOC: begin at the second "KERMANI TALES" (the body).
ms = [m.start() for m in re.finditer(r"KERMANI TALES", txt)]
if len(ms) >= 2:
    txt = txt[ms[1]:]

# Trim trailing apparatus (glossary/notes) if present.
tail = re.search(r"\bGLOSSARY\b|\bNOTES\b", txt[len(txt) // 2:])
if tail:
    txt = txt[: len(txt) // 2 + tail.start()]

# Real tale headings: "THE STORY OF <title>". The title is in ALL CAPS and may
# wrap across a line; the prose that follows is mixed-case. So after the marker we
# collect the run of all-caps tokens (across newlines), stopping at the first
# mixed-case word — that reconstructs wrapped titles like "THE CITY OF / NOTHING-
# IN-THE-WORLD" in full.
CAPS_TOKEN = re.compile(r"[A-Z][A-Z'’.\-]*$|^(?:OF|THE|AND|A|IN|TO|OR)$", re.I)
MIN_GAP = 1500          # a real tale is long; closer "THE STORY OF" = running head

def grab_title(after):
    toks = re.split(r"[\s/]+", after.strip())
    out = []
    for t in toks[:12]:
        t = t.strip(",")
        if not t:
            continue
        if re.search(r"[a-z]", t) or re.fullmatch(r"\d+", t):   # prose / page no.
            break
        out.append(t)
    return re.sub(r"\s+", " ", " ".join(out)).strip(" .,-")

seen, heads = set(), []
for m in re.finditer(r"THE STORY OF\s+", txt):
    if heads and m.start() - heads[-1][0] < MIN_GAP:     # running head, skip
        continue
    title = grab_title(txt[m.end():m.end() + 90])
    key = fl.norm_title(title)
    if not key or len(key) < 3 or key in seen:
        continue
    seen.add(key)
    heads.append((m.start(), title))

# Merge adjacent headings that open with the same two words: OCR running-heads
# sometimes mutate a long tale's title enough to dodge the gap/dedup filters and
# spawn a fragment ("THE COLT QEYTAS" / "THE COLT Q-YTAS"). Two consecutive tales
# rarely share their first two words, so folding these together is safe here and
# reunites the split tale with its body.
def same_tale(a, b):
    ta, tb = fl.norm_title(a).split(), fl.norm_title(b).split()
    if not ta or not tb:
        return False
    if len(ta) >= 2 and len(tb) >= 2 and ta[:2] == tb[:2]:
        return True                    # share opening two words
    short, long = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return long[:len(short)] == short  # one title is a token-prefix of the other

merged = []
for pos, title in heads:
    if merged and same_tale(title, merged[-1][1]):
        # Same tale's running head — keep the earlier position (body start) but
        # prefer the fuller title (OCR often clips one of the two).
        if len(title) > len(merged[-1][1]):
            merged[-1] = (merged[-1][0], title)
        continue
    merged.append((pos, title))
heads = merged

tales = []
for i, (pos, title) in enumerate(heads):
    end = heads[i + 1][0] if i + 1 < len(heads) else len(txt)
    # Title-case the ALL-CAPS OCR heading for display.
    disp = title.title().replace("'S", "'s")
    body = fl.ocr_to_paragraphs(txt[pos:end], drop_heading="THE STORY OF " + title)
    tales.append((disp, body))

note = f"Source: {SOURCE} — text is OCR, lightly cleaned."
n = fl.write_collection(COLLECTION, tales, lang="en", note=note)
if n:
    fl.record_source(COLLECTION, "D. L. R. & E. O. Lorimer", SOURCE,
                     language="en", culture="Persian")
print(f"\n{n} Lorimer tales. Add to build_manifest.py and re-run it.")
