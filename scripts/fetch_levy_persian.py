"""
Harvest Reuben Levy, *The Three Dervishes and Other Persian Tales and Legends*
(Oxford, 1923) from the archive.org OCR. Public domain (1923).

Bespoke fetcher (irregular source, as the folktale-harvester skill advises): the
book has several front-matter repeats of its titles (TOC + half-title), which
defeats the generic fetcher's single-TOC-skip. So we explicitly trim to the
narrative start, then locate each tale heading in sequence (first occurrence after
the previous, NO TOC skip). It is partly nested — frame tales contain embedded
stories — but each embedded story has its own heading, so they split cleanly.

Usage:
    python3 scripts/fetch_levy_persian.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                ".claude", "skills", "folktale-harvester", "scripts"))
import folktale_lib as fl

ARCHIVE_ID = "threedervischeso00levyuoft"
COLLECTION = "persian_levy_en"
SOURCE = ("archive.org threedervischeso00levyuoft OCR — The Three Dervishes and "
          "other Persian Tales (Levy, 1923)")

# (display title, distinctive match string as it appears in the body)
TITLES = [
    ("The Three Dervishes",                         "THREE DERVISHES"),
    ("The Story of the First Dervish",               "Story of the First Dervish"),
    ("The Story of the Second Dervish",              "Story of the Second Dervish"),
    ("The Story of the Third Dervish",               "Story of the Third"),
    ("The Story of Ashraf Khan",                     "Ashraf Khan"),
    ("The Story of Saji the Jeweller of Wasit",      "Jeweller"),
    ("The Generosity of Hatim Tai",                  "Generosity of"),
    ("Jamshid and Zuhak",                            "Jamshid and"),
    ("The Story of the Sailor and the Pearl Merchant", "Sailor and the"),
    ("The Treasure of Mansur",                       "Treasure of Mansur"),
    ("The Palace of Nine Pavilions",                 "Palace of Nine"),
    ("Akhtar the Cut-purse",                         "Akhtar the"),
    ("Afzal the Soothsayer",                         "Afzal the"),
    ("Nahid and her Harp",                           "Nahid and"),
    ("Khurshid and the White Genie",                 "Khurshid and the White"),
    ("Nasir the Butcher",                            "Nasir, the Butcher"),
    ("The Enchanted Island",                         "Enchanted Island"),
    ("Sayyara, Son of the King of the Greeks",       "Sayyara"),
    ("The Prince of Kashmir and the Holy Sheikh",    "Kashmir"),
    ("Khurshidshah and the Princess of China",       "Khurshidshah"),
]


def rx(s):
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()), re.I)


txt = fl.archive_djvu(ARCHIVE_ID)

# Trim to the narrative start: "...THREE DERVISHES  It is related that in time
# past...". Anchor on the first "It is related" and keep the heading just before.
narr = re.search(r"It\s+is\s+related\s+that", txt)
if narr:
    head = list(rx("THREE DERVISHES").finditer(txt[:narr.start()]))
    txt = txt[head[-1].start():] if head else txt[narr.start():]

# Trim trailing apparatus (glossary / index) so the last tale doesn't absorb it.
tail = re.search(r"\bGLOSSARY\b", txt[len(txt) // 2:])
if tail:
    txt = txt[: len(txt) // 2 + tail.start()]

# Locate each title in sequence (first occurrence after the previous).
positions, cursor = [], 0
for _disp, match in TITLES:
    m = rx(match).search(txt, cursor)
    if not m:
        print(f"  !! not found: {_disp}")
        positions.append(None)
        continue
    positions.append(m.start())
    cursor = m.end()

tales = []
for i, (disp, match) in enumerate(TITLES):
    if positions[i] is None:
        continue
    start = positions[i]
    end = len(txt)
    for j in range(i + 1, len(TITLES)):
        if positions[j] is not None:
            end = positions[j]; break
    body = fl.ocr_to_paragraphs(txt[start:end], drop_heading=match)
    tales.append((disp, body))

note = f"Source: {SOURCE} — text is OCR, lightly cleaned."
n = fl.write_collection(COLLECTION, tales, lang="en", note=note)
if n:
    fl.record_source(COLLECTION, "Reuben Levy", SOURCE, language="en", culture="Persian")
print(f"\n{n} Levy tales. Add to build_manifest.py and re-run it.")
