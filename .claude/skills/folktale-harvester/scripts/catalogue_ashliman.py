"""
catalogue_ashliman — build a culture-filtered target list from D. L. Ashliman's
folktexts site (pitt.edu/~dash), the best free cross-cultural folktale index.

This is the CATALOGUE track: it does not fetch tale texts (those are copyrighted
translations). It harvests only factual metadata — title, ATU/type number,
culture, attributed author/collector — to tell you what exists for a culture and,
crucially, which collectors and books to then hunt for full PD texts of.

It BFS-crawls the two alpha indexes, extracts per-variant rows from the
<h2>Title</h2> -> <h3>Country (Author)</h3> pattern, then filters to rows whose
culture/origin matches the requested culture (substring, plus your aliases).

Usage:
    python3 catalogue_ashliman.py "Japanese" [alias1 alias2 ...]
    python3 catalogue_ashliman.py "Irish" Ireland Celtic

Output:
    index/catalogue_<culture>.csv   filtered rows (atu, topic, title, culture,
                                    author, origin_raw, source_page)
A printed summary lists the distinct authors/collectors found — those are your
leads for the harvest track.

Only metadata is extracted; no tale prose or Ashliman's commentary (copyright).
"""

import os
import re
import csv
import sys
import json
import html as htmlmod

from folktale_lib import http_get, clean_text, PROJ

ROOT = "https://www.pitt.edu/~dash/"
NAV = {"ashliman.html", "folktexts.html", "folktexts2.html", "folklinks.html",
       "index.html"}
LINK_RE = re.compile(r'href="([a-z0-9_]+\.html)(?:#[^"]*)?"', re.I)
STOP = re.compile(r"^(contents|table of contents|links?( to related sites)?|"
                  r"related links|notes?|bibliography|sources?|return to|"
                  r"d\.?\s*l\.?\s*ashliman|revised|other links|see also|"
                  r"folklore and mythology|legends|external links)\b", re.I)
CAP = 1500


def fetch(page):
    return http_get(ROOT + page, cache_key="ashliman_" + page, pause=0.3)


def parse_origin(s):
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", s)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return s, ""


def crawl():
    seen, order = set(), []
    queue = ["folktexts.html", "folktexts2.html"]
    while queue and len(seen) < CAP:
        page = queue.pop(0)
        if page in seen:
            continue
        seen.add(page)
        h = fetch(page)
        if page not in NAV:
            order.append(page)
        for href in LINK_RE.findall(h):
            href = href.lower()
            if href not in seen:
                queue.append(href)
    return order


def all_rows():
    rows, seen = [], set()
    for page in crawl():
        h = fetch(page)
        body = re.sub(r"<(script|style)\b.*?</\1>", "", h, flags=re.DOTALL | re.I)
        atu = ""
        m = re.match(r"type0*(\d+[a-z]?)", page, re.I)
        if m:
            atu = m.group(1).upper()
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.DOTALL | re.I)
        topic = clean_text(h1.group(1)) if h1 else page.replace(".html", "")
        heads = [(int(l), clean_text(t)) for l, t in
                 re.findall(r"<h([2-4])[^>]*>(.*?)</h\1>", body, re.DOTALL | re.I)]
        heads = [(l, t) for l, t in heads if t and not STOP.match(t)]
        i = 0
        while i < len(heads):
            lvl, title = heads[i]
            origin = ""
            if i + 1 < len(heads) and heads[i + 1][0] > lvl:
                origin = heads[i + 1][1]; i += 2
            else:
                i += 1
            if origin:
                culture, author = parse_origin(origin)
            else:
                base, paren = parse_origin(title)
                if paren:
                    title, culture, author = base, paren, ""
                else:
                    culture, author = "", ""
            if re.match(r"^[\dIVXLCM]+\.?[a-z]?$", title):
                continue
            key = (page, title, origin)
            if key in seen:
                continue
            seen.add(key)
            rows.append({"atu": atu, "topic": topic, "title": title,
                         "culture": culture, "author": author,
                         "origin_raw": origin, "source_page": page})
    return rows


def main(culture, aliases):
    terms = [culture] + list(aliases)
    pat = re.compile("|".join(re.escape(t) for t in terms), re.I)
    if not fetch("folktexts.html").strip():
        sys.stderr.write(
            "WARNING: Ashliman (pitt.edu/~dash) is unreachable or blocked from this "
            "environment. This is NOT fatal — Ashliman is one aggregator among "
            "several. Build the catalogue from the OTHER sources in "
            "references/sources.md (Wikisource book indexes, Wikipedia 'list of "
            "<culture> folktales', candidate Gutenberg TOCs) and run "
            "catalogue_merge.py on those. Writing an empty Ashliman CSV so the "
            "merge step still runs.\n")
        rows = []
    else:
        rows = all_rows()
    hits = [r for r in rows
            if pat.search(r["culture"]) or pat.search(r["origin_raw"])]
    # One source among several — write a source-specific file. The deduped master
    # catalogue_<culture>.csv is produced by catalogue_merge.py from this + others.
    out = os.path.join(PROJ, "index", f"catalogue_{culture.lower()}_ashliman.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["atu", "topic", "title", "culture",
                                          "author", "origin_raw", "source_page"])
        w.writeheader()
        w.writerows(hits)

    print(f"\n{len(hits)} {culture} entries (of {len(rows)} total) -> "
          f"index/catalogue_{culture.lower()}_ashliman.csv")
    authors = {}
    for r in hits:
        if r["author"]:
            authors[r["author"]] = authors.get(r["author"], 0) + 1
    if authors:
        print("\nCollectors / authors to chase for full PD texts:")
        for a, c in sorted(authors.items(), key=lambda x: -x[1]):
            print(f"  {c:4d}  {a}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: python3 catalogue_ashliman.py "Culture" [aliases...]')
    main(sys.argv[1], sys.argv[2:])
