"""
split_gutenberg_epub — split a Project Gutenberg EPUB into per-tale HTML.

Gutenberg is the best free source: proofread, clean markup, unambiguously public
domain in the US (everything on the main site is). Download the EPUB (no images),
then split it here.

EPUBs vary, so this works in two modes:

  "headings"  — concatenate the spine's content files and start a new tale at
                every heading of a chosen level. Front-matter and license
                headings are dropped via `skip_headings`; multi-part tales are
                kept whole via `subpart_headings` (a heading matching that
                pattern folds into the preceding tale rather than starting a new
                one — e.g. "Evening", "Chapter II", "The Third Visit").
  "files"     — the EPUB already stores one tale per content file (some Gutenberg
                builds do). Each spine file becomes one tale; its first heading is
                the title.

Inspect the EPUB first to choose mode and patterns:
    python3 split_gutenberg_epub.py --inspect book.epub
This lists the spine files and the headings it finds, so you can see the
structure before committing to a config.

Usage:
    python3 split_gutenberg_epub.py --inspect <book.epub>
    python3 split_gutenberg_epub.py <config.json>

Config:
{
  "collection":  "celtic_jacobs_en",
  "author":      "Joseph Jacobs",
  "culture":     "Celtic",
  "lang":        "en",
  "source":      "Gutenberg #7885 — Celtic Fairy Tales (Jacobs, 1892)",
  "epub":        "sources/celtic_fairy_tales.epub",
  "mode":        "headings",
  "heading_level": 2,
  "skip_headings": ["contents", "preface", "introduction", "notes",
                    "full project gutenberg license", "transcriber"],
  "subpart_headings": [],       // regexes; headings to fold into the prior tale
  "title_strip": "^[IVXLC]+\\s+"  // optional regex stripped from each tale title
}                                 // (e.g. leading Roman/arabic numbering)
"""

import os
import re
import sys
import json
import zipfile

from folktale_lib import (PROJ, clean_text, html_to_paragraphs,
                          write_collection, record_source)

BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.DOTALL | re.I)
STRAY_RE = re.compile(r"<(?:link|meta)\b[^>]*/?>", re.I)


def spine_files(zf):
    """Return content file paths in reading order, from the OPF spine."""
    opf_name = None
    for n in zf.namelist():
        if n.endswith(".opf"):
            opf_name = n
            break
    if not opf_name:
        # Fall back: all xhtml/html, sorted.
        return sorted(n for n in zf.namelist()
                      if re.search(r"\.(x?html?)$", n, re.I))
    opf = zf.read(opf_name).decode("utf-8", "replace")
    base = os.path.dirname(opf_name)
    # Map manifest id -> href (attribute order varies, so parse each item tag).
    manifest = {}
    for item in re.findall(r"<item\b[^>]*?/?>", opf):
        mid = re.search(r'id="([^"]+)"', item)
        href = re.search(r'href="([^"]+)"', item)
        if mid and href:
            manifest[mid.group(1)] = href.group(1)
    order = re.findall(r'<itemref\b[^>]*idref="([^"]+)"', opf)
    files = []
    for idref in order:
        href = manifest.get(idref)
        if href and re.search(r"\.(x?html?)$", href, re.I):
            files.append(os.path.join(base, href) if base else href)
    return files


def read_bodies(epub_path):
    """Yield (filename, inner_body_html) for each spine content file."""
    with zipfile.ZipFile(epub_path) as zf:
        for fn in spine_files(zf):
            try:
                raw = zf.read(fn).decode("utf-8", "replace")
            except KeyError:
                continue
            m = BODY_RE.search(raw)
            inner = STRAY_RE.sub("", m.group(1)) if m else ""
            yield fn, inner


def inspect(epub_path):
    """Compact structural view: heading levels in use and a sample of titles.

    The goal is to let you choose mode + heading_level + skip patterns without
    echoing every heading (a 200-tale book would otherwise flood the context).
    """
    from collections import Counter
    levels = Counter()
    files_with_heads = 0
    sample = []
    nfiles = 0
    for fn, body in read_bodies(epub_path):
        nfiles += 1
        heads = re.findall(r"<h([1-6])\b[^>]*>(.*?)</h\1>", body, re.DOTALL | re.I)
        if heads:
            files_with_heads += 1
        for lvl, t in heads:
            levels[lvl] += 1
            if len(sample) < 30:
                sample.append((lvl, clean_text(t)[:70]))

    total_heads = sum(levels.values())
    print(f"{nfiles} spine files, {files_with_heads} contain headings, "
          f"{total_heads} headings total.")
    print(f"heading levels in use: {dict(sorted(levels.items()))}")
    if not levels:
        print("  -> no headings; tales may be split by <p>/<b> — write a bespoke fetcher")
    elif total_heads <= files_with_heads:
        print('  -> ~one heading per file; mode "files" may work (but "headings" is safer)')
    else:
        print('  -> multiple headings per file; use mode "headings" + skip_headings')
    print("\nfirst headings (level: text) — pick the tale level, skip the rest:")
    for lvl, t in sample:
        print(f"  h{lvl}: {t}")
    if total_heads > 30:
        print(f"  ... (+{total_heads - 30} more headings; full list omitted to save tokens)")


def run(cfg):
    epub_path = cfg["epub"]
    if not os.path.isabs(epub_path):
        epub_path = os.path.join(PROJ, epub_path)
    bodies = list(read_bodies(epub_path))
    lang = cfg.get("lang", "en")
    strip_rx = re.compile(cfg["title_strip"]) if cfg.get("title_strip") else None

    def fix(title):
        return strip_rx.sub("", title).strip() if strip_rx else title

    tales = []

    if cfg.get("mode", "headings") == "files":
        for _fn, body in bodies:
            hm = re.search(r"<h([1-6])\b[^>]*>(.*?)</h\1>", body, re.DOTALL | re.I)
            title = clean_text(hm.group(2)) if hm else ""
            if not title:
                continue
            if _skip(title, cfg):
                continue
            tales.append((fix(title), html_to_paragraphs(body, drop_title=title)))
    else:
        level = cfg.get("heading_level", 2)
        big = "\n".join(b for _f, b in bodies)
        heads = list(re.finditer(rf"<h{level}\b[^>]*>(.*?)</h{level}>",
                                 big, re.DOTALL | re.I))
        sub_pats = [re.compile(p, re.I) for p in cfg.get("subpart_headings", [])]
        # Build (title, start, end) tale spans, folding subparts into the prior.
        spans = []
        for i, m in enumerate(heads):
            title = clean_text(m.group(1))
            start = m.start()
            end = heads[i + 1].start() if i + 1 < len(heads) else len(big)
            is_sub = any(p.search(title) for p in sub_pats)
            if _skip(title, cfg):
                continue
            if is_sub and spans:
                spans[-1] = (spans[-1][0], spans[-1][1], end)   # extend prior
            else:
                spans.append((title, start, end))
        for title, start, end in spans:
            body = html_to_paragraphs(big[start:end], drop_title=title)
            tales.append((fix(title), body))

    n = write_collection(cfg["collection"], tales, lang=lang)
    if n:
        record_source(cfg["collection"], cfg["author"], cfg["source"],
                      language=lang, culture=cfg.get("culture"))
    return n


def _skip(title, cfg):
    t = title.lower()
    return any(re.search(p, t) for p in cfg.get("skip_headings", []))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--inspect":
        inspect(sys.argv[2])
    elif len(sys.argv) == 2:
        cfg = json.load(open(sys.argv[1], encoding="utf-8"))
        run(cfg)
        print("\nDone. Add the collection to scripts/build_manifest.py and re-run it.")
    else:
        sys.exit("usage: python3 split_gutenberg_epub.py [--inspect] <book.epub | config.json>")
