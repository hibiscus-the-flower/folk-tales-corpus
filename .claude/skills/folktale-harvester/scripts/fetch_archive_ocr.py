"""
fetch_archive_ocr — harvest a book that exists only as Internet-Archive OCR.

Use this when there is no Gutenberg or Wikisource edition but archive.org has a
full-view (public-domain) scan with a *_djvu.txt. Fidelity is LOWER than HTML
sources — expect mis-read letters and drop-cap garble — so every tale carries a
provenance note flagging it as OCR.

Splitting works by locating each tale title as a heading in the OCR stream, in
order. Running page-heads repeat a title but never match the *next* one, so the
sequence stays aligned. Two match modes:

  default      case-insensitive, whitespace-flexible — good for discrete titles.
  "caps_match" case-sensitive on the UPPERCASE form with word boundaries — use
               when titles are short ALL-CAPS headings (e.g. RUTH, DEMONS) that
               would otherwise substring-match body words; also auto-skips the
               mixed-case table of contents.

ALWAYS --inspect the book first — OCR layout is unpredictable:

    python3 fetch_archive_ocr.py --inspect <archive_id>

It prints the contents block (your title list), the first lines of the narrative
(your `body_start` anchor), and a front-matter check. Scanned books frequently
repeat their titles in more than one front section (a contents page AND a
half-title page). One contents list is auto-skipped, but multiple repeats fool
the anchoring and dump the whole body into one tale — set `body_start` to the
exact opening words of the first tale's narrative and the front matter is trimmed
cleanly. If a book is also *nested* (a frame story whose chapters contain embedded
sub-stories interleaved with "continuations"), the config approach gets brittle —
write a thin bespoke fetcher that imports folktale_lib instead (see
scripts/fetch_levy_persian.py and fetch_lorimer_persian.py for worked examples).

Usage:
    python3 fetch_archive_ocr.py --inspect <archive_id>
    python3 fetch_archive_ocr.py <config.json>

Config:
{
  "collection": "irish_kennedy_en",
  "author":     "Patrick Kennedy",
  "culture":    "Irish",
  "lang":       "en",
  "source":     "archive.org legendaryfiction00kenn OCR (1866)",
  "archive_id": "legendaryfiction00kenn",
  "caps_match": false,
  "titles": ["The Twelve Wild Geese", "The Lazy Beauty and her Aunts"],
  // when caps_match is true, titles may be [display, "UPPERCASE MATCH"] pairs
  "body_start": "It is related that",    // optional: trims ALL front matter to here
  "end_marker": "Popular New Books",      // optional: trims trailing catalogue
  "end_marker_caps": "INDEX"              // optional: trims back-matter (tail only)
}

Confirm public-domain status before harvesting (see references/copyright.md).
A full-view archive.org item is normally PD, but verify the edition date.
"""

import sys
import json
import re

from folktale_lib import archive_djvu, ocr_to_paragraphs, write_collection, record_source


def title_rx(title, caps=False):
    if caps:
        pat = r"\b" + r"\s+".join(re.escape(w) for w in title.upper().split()) + r"\b"
        return re.compile(pat)
    return re.compile(r"\s+".join(re.escape(w) for w in title.split()), re.I)


def anchor_body(txt, titles, caps):
    """Return the offset where the narrative body begins (past front matter).

    A contents/half-title page lists the titles close together, so the first
    title is followed *almost immediately* by the second. In the body, the first
    title's heading is followed by prose and the second title is far away. So we
    accept the first occurrence of title[0] that is NOT shortly followed by
    title[1]. This skips one OR several front-matter title lists (the single-skip
    default missed the second repeat — that's the bug this fixes). For books with
    a lone half-title (title[0] alone on a page, title[1] not nearby), this can
    still mis-anchor — use the explicit `body_start` config in that case.
    """
    occ0 = list(title_rx(titles[0][1], caps).finditer(txt))
    if not occ0:
        return 0
    if len(titles) < 2:
        return occ0[1].start() if len(occ0) > 1 else occ0[0].start()
    rx1 = title_rx(titles[1][1], caps)
    for m in occ0:
        nxt = rx1.search(txt, m.end())
        if not nxt or (nxt.start() - m.end()) > 800:   # prose follows -> body
            return m.start()
    return occ0[-1].start()


def run(cfg):
    caps = cfg.get("caps_match", False)
    txt = archive_djvu(cfg["archive_id"])

    if cfg.get("end_marker"):
        em = title_rx(cfg["end_marker"]).search(txt)
        if em:
            txt = txt[:em.start()]
    if cfg.get("end_marker_caps"):
        ms = [m for m in title_rx(cfg["end_marker_caps"], caps=True).finditer(txt)
              if m.start() > len(txt) * 0.5]
        if ms:
            txt = txt[:ms[0].start()]

    # Normalise to (display, match_str) pairs.
    titles = [t if isinstance(t, (list, tuple)) else (t, t) for t in cfg["titles"]]

    # Find where the narrative body starts (so headings aren't matched in the
    # contents / half-title front matter). `body_start` is the robust override;
    # otherwise auto-detect by skipping clustered title lists.
    if cfg.get("body_start"):
        # Match whitespace-flexibly: OCR runs words together with irregular
        # spacing, so a literal phrase from the page rarely matches verbatim.
        bs_rx = re.compile(r"\s+".join(re.escape(w) for w in cfg["body_start"].split()), re.I)
        bm = bs_rx.search(txt)
        if bm:
            pre = list(title_rx(titles[0][1], caps).finditer(txt[:bm.start()]))
            txt = txt[pre[-1].start():] if pre else txt[bm.start():]
            cursor = 0
        else:
            print(f"  !! body_start not found: {cfg['body_start']!r} — "
                  f"falling back to auto-anchor")
            cursor = anchor_body(txt, titles, caps)
    else:
        cursor = anchor_body(txt, titles, caps)

    positions = []
    for _disp, match_str in titles:
        m = title_rx(match_str, caps).search(txt, cursor)
        if not m:
            print(f"  !! heading not found: {_disp}")
            positions.append(None)
            continue
        positions.append(m.start())
        cursor = m.end()

    tales = []
    for i, (disp, match_str) in enumerate(titles):
        if positions[i] is None:
            continue
        start = positions[i]
        end = len(txt)
        for j in range(i + 1, len(titles)):
            if positions[j] is not None:
                end = positions[j]; break
        body = ocr_to_paragraphs(txt[start:end], drop_heading=match_str)
        tales.append((disp, body))

    note = f"Source: {cfg['source']} — text is OCR, lightly cleaned."
    n = write_collection(cfg["collection"], tales, lang=cfg.get("lang", "en"), note=note)
    if n:
        record_source(cfg["collection"], cfg["author"], cfg["source"],
                      language=cfg.get("lang", "en"), culture=cfg.get("culture"))
    return n


def inspect(archive_id):
    """Print what you need to write a config: the contents block (title list),
    the narrative opening (body_start anchor), and a front-matter repeat check."""
    txt = archive_djvu(archive_id)
    print(f"{archive_id}: {len(txt)} chars of OCR.\n")

    cm = re.search(r"\bCONTENTS\b", txt)
    if cm:
        print("CONTENTS block (your 'titles' list — fix OCR garble by hand):")
        for ln in txt[cm.start():cm.start() + 1600].splitlines():
            s = ln.strip()
            if s and not re.fullmatch(r"[\d ivxlcIVXLC.\-]+", s):
                print("   ", s[:66])
        print()

    # Narrative opening: first real prose line after the front matter. Skip
    # contents entries (dot-leaders, trailing page numbers) and headings.
    body = txt[cm.end():] if cm else txt
    for ln in body.splitlines():
        s = ln.strip()
        if len(s) < 45 or re.search(r"\.\s*\.", s) or re.search(r"\d\s*$", s):
            continue                                   # leaders / page number
        words = s.split()
        lower = sum(1 for w in words if re.fullmatch(r"[a-z]{2,}", w))
        if lower >= 6:                                 # several lowercase words = prose
            print(f"likely narrative start (use as 'body_start'):\n    \"{s[:60]}...\"\n")
            break

    # Front-matter repeat check: does an early heading-ish line recur?
    caps_lines = [l.strip() for l in txt[:len(txt)//2].splitlines()
                  if re.fullmatch(r"[A-Z][A-Z .,'’\-]{6,40}", l.strip() or "X")]
    from collections import Counter
    dup = [(c, n) for c, n in Counter(caps_lines).items() if n > 1]
    if dup:
        print("front-matter repeats detected (TOC + half-title etc.) — set 'body_start':")
        for c, n in sorted(dup, key=lambda x: -x[1])[:6]:
            print(f"   {n}× {c[:50]}")
    else:
        print("no obvious title repeats; the default auto-anchor should be fine.")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--inspect":
        inspect(sys.argv[2])
    elif len(sys.argv) == 2:
        cfg = json.load(open(sys.argv[1], encoding="utf-8"))
        run(cfg)
        print("\nDone. Add the collection to scripts/build_manifest.py and re-run it.")
    else:
        sys.exit("usage: python3 fetch_archive_ocr.py [--inspect <archive_id> | <config.json>]")
