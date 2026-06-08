"""
fetch_munoz_spanish — harvest José Muñoz Escámez, Fairy Tales from Spain
(Gutenberg #43212, 1913).

The EPUB has no h2/h3 tale headings; tales are marked by:
  <p id="tale-slug"><span class="bold large">TALE TITLE</span></p>
This bespoke fetcher splits on those anchors.
"""
import os, re, sys, zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                "../.claude/skills/folktale-harvester/scripts"))
from folktale_lib import (PROJ, html_to_paragraphs, write_collection,
                          record_source)

EPUB = os.path.join(PROJ, "sources", "munoz_fairy_tales_spain_en.epub")
COLLECTION = "spanish_munoz_en"
AUTHOR = "José Muñoz Escámez (trans. anon., 1913)"
SOURCE = "Gutenberg #43212 — Fairy Tales from Spain (Muñoz Escámez, 1913)"
CULTURE = "Spanish"
LANG = "en"

TITLE_RE = re.compile(
    r'<p[^>]+id=["\'][^"\']*["\'][^>]*>'
    r'\s*<span[^>]*class=["\'][^"\']*bold[^"\']*["\'][^>]*>(.*?)</span>',
    re.DOTALL | re.I)

SKIP_IDS = {"khing-chu-fu"}   # not Spanish; keep for completeness but flag
LICENSE_RE = re.compile(r'full.project.gutenberg', re.I)

def main():
    with zipfile.ZipFile(EPUB) as zf:
        # Read spine order from OPF
        opf = next(n for n in zf.namelist() if n.endswith('.opf'))
        opf_text = zf.read(opf).decode('utf-8', 'replace')
        base = os.path.dirname(opf)
        manifest = {}
        for item in re.findall(r'<item\b[^>]*?/?>',  opf_text):
            mid = re.search(r'id="([^"]+)"', item)
            href = re.search(r'href="([^"]+)"', item)
            if mid and href:
                manifest[mid.group(1)] = href.group(1)
        order = re.findall(r'<itemref\b[^>]*idref="([^"]+)"', opf_text)
        files = [os.path.join(base, manifest[i])
                 for i in order if i in manifest
                 and re.search(r'\.(x?html?)$', manifest.get(i,''), re.I)]

        # Concatenate all body content
        big = ""
        for fn in files:
            try:
                raw = zf.read(fn).decode('utf-8', 'replace')
            except KeyError:
                continue
            m = re.search(r'<body[^>]*>(.*)</body>', raw, re.DOTALL | re.I)
            if m:
                big += m.group(1)

    # Find all tale-title anchors
    spans = []
    for m in TITLE_RE.finditer(big):
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        title = re.sub(r'\s+', ' ', title).title()  # normalise caps
        if LICENSE_RE.search(title):
            continue
        spans.append((title, m.start()))

    tales = []
    for i, (title, start) in enumerate(spans):
        end = spans[i+1][1] if i+1 < len(spans) else len(big)
        body = html_to_paragraphs(big[start:end], drop_title=title)
        tales.append((title, body))

    n = write_collection(COLLECTION, tales, lang=LANG)
    if n:
        record_source(COLLECTION, AUTHOR, SOURCE, language=LANG, culture=CULTURE)
    print(f"\nDone. {n} tales written to corpus/{COLLECTION}/")

if __name__ == "__main__":
    main()
