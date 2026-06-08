# Where to find public-domain folk tales, by source type

Ranked by text fidelity and ease of harvesting. Prefer sources higher in this
list — they need less cleanup and carry less copyright risk.

## 1. Project Gutenberg — best
Proofread, clean markup, unambiguously US public domain. Many cultures have a
classic English collection here (Jacobs' *Celtic/English/Indian Fairy Tales*,
Ozaki's *Japanese Fairy Tales*, Lang's colour Fairy Books, Asbjørnsen & Moe via
Dasent, etc.).

- Find editions: search `https://www.gutenberg.org/ebooks/search/?query=<culture>+fairy+tales`
  or use Gutendex JSON: `https://gutendex.com/books/?search=<culture>%20fairy%20tales`.
- Download the **EPUB (no images)**, drop it in `sources/`, then
  `split_gutenberg_epub.py --inspect` it to see structure, write a config, split.

## 2. Wikisource — best for proofread single editions
Often hosts a whole book with one tale per subpage. Highest fidelity after
Gutenberg, reached cleanly through the MediaWiki `action=parse` API (no scraping).

- Find: search `https://en.wikisource.org/w/index.php?search=<culture>+fairy+tales`
  or browse the work's index page to list subpages.
- Other-language Wikisources (de, fr, ru, ...) host originals and translations —
  set `"lang"` in the config. (The Russian Andersen corpus came from ru.wikisource.)
- Harvest with `fetch_wikisource.py` (subpages mode usually; single mode if the
  whole book is on one page split by headings).

## 3. archive.org — fallback for OCR-only books
Use when no Gutenberg/Wikisource edition exists but a **full-view** scan does.
Lower fidelity (OCR), so flag it. The `*_djvu.txt` is the plain-text OCR.

- Find: `https://archive.org/advancedsearch.php?q=<culture>+folk+tales+AND+mediatype:texts`
  (JSON output available). **Check access**: full-view = PD-safe; "Borrow" = skip.
- Harvest with `fetch_archive_ocr.py` (give it the `archive_id` and ordered title
  list; inspect the djvu.txt first to get exact heading strings).

## 4. HathiTrust, Sacred-Texts, regional digital libraries
- **HathiTrust**: large, but full-text download is limited; usually better as a
  *catalogue* lead than a harvest source.
- **sacred-texts.com**: many old folklore/mythology e-texts (PD), but the site is
  Cloudflare-gated and often redundant with Gutenberg — try Gutenberg first.
- **Regional libraries / national Wikisources** for non-English originals.

## Cataloguing / index sources (metadata, not text)
No single aggregator is enough — consult several and merge with
`catalogue_merge.py` (it dedupes by title and tags each title's source). Target
~150 distinct titles. Sources, roughly by yield:

- **D. L. Ashliman, pitt.edu/~dash** — cross-cultural index by ATU type and
  culture; `catalogue_ashliman.py` filters it to one culture and surfaces the
  collectors to chase. Depth varies a lot by culture (deep for European, thin for
  others). Texts are copyrighted translations → metadata only.
- **Tables of contents of the PD editions you find** — a Gutenberg/Wikisource
  book's TOC *is* a tale list. `split_gutenberg_epub.py --inspect` prints the
  headings; dump them to a CSV. This is the highest-quality catalogue source
  because every title is already harvestable.
- **Wikisource** — a collection's index page lists its subpages (one per tale).
  Pull the subpage titles via the API or the index page.
- **Wikipedia / Wikidata** — "List of <culture> folktales", "<culture> mythology",
  and category pages give titles and often the collector/edition. Free to catalogue.
- **SurLaLune, folklore wikis, national folklore archives** — title lists by
  culture; metadata only (commentary is copyrighted).
- **ATU (Aarne–Thompson–Uther) type numbers** give the type spine. The full
  Uther 2004 catalogue is copyrighted — use only numbers + short titles.

When the master is still under target, the missing titles usually live in an
aggregator you haven't tried yet — that's what the second sweep (SKILL.md Phase 1b)
is for. Search specifically for the collectors and types you already found.

## A good harvest order for a new culture
1. Catalogue: run `catalogue_ashliman.py "<Culture>"` to see what exists and who
   collected it.
2. For each collector/classic collection it surfaces, look for a **Gutenberg**
   edition first, then **Wikisource**, then a full-view **archive.org** scan.
3. Harvest each cleared edition as its own collection; dedup; update the manifest.
