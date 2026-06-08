"""
fetch_wikisource — harvest a public-domain Wikisource book into per-tale HTML.

Wikisource is the highest-fidelity free source after Gutenberg: proofread text,
no OCR garble, reachable cleanly through the MediaWiki action=parse API. Most
collections store one tale per subpage, which is the easy and reliable case.

Drive it with a small JSON config so the script stays generic and each book is
just data. Two layouts are supported:

  "subpages"  — one tale per Wikisource subpage (the common case). You give the
                base page and the ordered list of [display_title, subpage].
  "single"    — the whole book on one page, tales separated by headings. You give
                the page and the heading level to split on.

Usage:
    python3 fetch_wikisource.py <config.json>

Config (subpages):
{
  "collection": "japanese_ozaki_en",
  "author":     "Yei Theodora Ozaki",
  "culture":    "Japanese",
  "lang":       "en",
  "source":     "Wikisource — Japanese Fairy Tales (Ozaki, 1908)",
  "mode":       "subpages",
  "base":       "Japanese_Fairy_Tales",
  "subpages": [
     ["My Lord Bag of Rice", "My_Lord_Bag_of_Rice"],
     ["The Tongue-Cut Sparrow", "The_Tongue-Cut_Sparrow"]
  ]
}

Config (single):
{
  "collection": "...", "author": "...", "culture": "...", "lang": "en",
  "source": "...", "mode": "single",
  "page": "Hebrew_Tales", "heading_level": 3,
  "skip_headings": ["Preface", "Contents", "Introduction"]   // optional
}

Before writing any config, confirm the edition is public domain
(see references/copyright.md). PD status is your call, not the script's.
"""

import sys
import json
import re

from folktale_lib import (wikisource_parse, html_to_paragraphs, clean_text,
                          write_collection, record_source)


def run(cfg):
    lang = cfg.get("lang", "en")
    mode = cfg.get("mode", "subpages")
    tales = []

    if mode == "subpages":
        base = cfg["base"]
        for title, subpage in cfg["subpages"]:
            page = f"{base}/{subpage}" if base else subpage
            raw = wikisource_parse(page, lang=lang)
            if not raw:
                print(f"  !! no content for {title} ({page})")
                continue
            body = html_to_paragraphs(raw, drop_title=title)
            tales.append((title, body))

    elif mode == "single":
        raw = wikisource_parse(cfg["page"], lang=lang)
        level = cfg.get("heading_level", 2)
        skip = {s.lower() for s in cfg.get("skip_headings", [])}
        # Find every heading at the chosen level, in document order.
        heads = list(re.finditer(rf"<h{level}\b[^>]*>(.*?)</h{level}>",
                                 raw, re.DOTALL | re.I))
        for i, m in enumerate(heads):
            title = clean_text(m.group(1))
            if not title or title.lower() in skip:
                continue
            start = m.end()
            end = heads[i + 1].start() if i + 1 < len(heads) else len(raw)
            body = html_to_paragraphs(raw[start:end], drop_title=title)
            if body:
                tales.append((title, body))
    else:
        sys.exit(f"unknown mode: {mode!r}")

    n = write_collection(cfg["collection"], tales, lang=lang)
    if n:
        record_source(cfg["collection"], cfg["author"], cfg["source"],
                      language=lang, culture=cfg.get("culture"))
    return n


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 fetch_wikisource.py <config.json>")
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    run(cfg)
    print("\nDone. Add the collection to scripts/build_manifest.py and re-run it.")
