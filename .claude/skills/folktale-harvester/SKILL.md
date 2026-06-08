---
name: folktale-harvester
description: >-
  Autonomously expand this public-domain folk/fairy-tale corpus with the tales of
  a given culture. Use this whenever the user wants to add, collect, gather,
  harvest, scrape, build, or expand folk tales / fairy tales / folklore / legends
  / myths for ANY culture, country, ethnicity, region, or tradition (e.g.
  "Japanese fairy tales", "add Irish folk tales", "get me as many Norwegian tales
  as possible", "expand the corpus with Indian folklore", "find Celtic stories").
  Trigger even when the user just names a culture and asks for "as many tales as
  possible" or to "expand the corpus" — that means run this. It catalogues what
  exists, finds complete public-domain editions, splits them into per-tale HTML
  in corpus/, dedups, and updates the manifest. Do NOT use for editing a single
  existing tale file or for non-folklore text.
---

# Folktale Harvester

Expand the corpus with one culture's public-domain folk tales, end to end and
autonomously. The user names a culture (e.g. *Japanese*, *Irish*, *Norwegian*);
you produce as many clean, deduplicated, per-tale HTML files as the public domain
allows, wired into the existing index.

This skill generalizes the workflow that already built the Andersen, Grimm, and
Jewish/Yiddish collections. The hard-won lesson baked in here: **harvest whole
editions, not individual titles.** A web search for one tale title rarely yields
a clean public-domain page, but a complete PD collection splits cleanly into
dozens of tales. So the catalogue tells you *what exists and who collected it*,
and the texts come from *editions*, not title-by-title searches.

## Two tracks

- **Catalogue** (the map): from aggregators, build a deduped list of the culture's
  tales — titles, ATU types, cultures, collectors. Metadata only; this is always
  copyright-safe and tells you which collections to chase.
- **Harvest** (the texts): for each public-domain edition the catalogue points to,
  get the full text and split it into per-tale HTML. This is where the corpus
  actually grows.

The catalogue feeds the harvest. Run catalogue first, then harvest what it surfaces.

## The hard rule: public domain only

Read `references/copyright.md` and hold the line. Because runs are autonomous, you
are the only gate. The short version: **edition published before 1929 (US), or on
Project Gutenberg → harvestable; "Borrow"/waitlist on archive.org or any modern
translation → catalogue the metadata but do not harvest the text.** Date the
*edition/translation*, not the underlying folklore. When unsure, catalogue only
and record the doubt. Never let the desire for "as many as possible" erode this.

## Coverage targets

Treat **150 catalogue titles** and **100 harvested tales** as *floors, not
ceilings* — the more the merrier. Keep going as long as the public domain keeps
giving: harvest every cleared edition you can find, not just enough to clear the
bar. The floors exist only to stop you quitting early; there is no upper limit.

The one thing that overrides "more" is quality: never pad the count with
copyrighted text, near-duplicate reprints, or junk OCR. A larger corpus is better
*only* when every tale is clean and public-domain.

Some cultures simply have less in the public domain. If you can't reach a floor,
say so and list what blocked it (e.g. key collections still in copyright) — that
shortfall is a finding, not a failure. Reaching 100+ tales normally means
harvesting **several editions** (a typical collection yields 20–40), so keep going
past the first book until you have genuinely exhausted the public-domain editions.

## Working within a token budget

A full run makes many tool calls, and the cost that matters is **what lands in the
model context** — i.e. what tools print and what you read. The bundled scripts do
all heavy lifting (OCR, epub bodies, crawls) in Python so raw text never enters
context; keep it that way:

- **Never `Read` a raw source dump** — djvu.txt OCR, full epub bodies, the whole
  catalogue CSV. Let the scripts process them; they print compact summaries and
  route detail to `.cache/harvester/*.log` (grep that only if a number looks off).
- **Spot-check with small Python that prints truncated output** (first/last
  paragraph, a count), not by opening whole tale files. One tale file is ~20–40 KB.
- **Trust the summaries.** `--inspect`, the fetchers, and `dedup_corpus.py` already
  print exactly what you need to decide the next step. Don't re-dump to verify.
- Caching under `.cache/harvester/` means re-running a crawl or fetch is free and
  silent — lean on it rather than widening searches "just in case."

## Workflow

Work through these phases. Narrate progress as you go; you don't need to stop for
approval, but do produce the survey so your public-domain decisions are auditable.

### Phase 1 — Catalogue (multi-aggregator, 150+ titles — more is better)
Build the "map" from **several** aggregators, not one — Ashliman is strong on some
cultures and thin on others (it returned only 19 titles for Japanese). The
aggregators to consult are listed in `references/sources.md`; at minimum:

1. Run the anchor crawl (deterministic, cached, token-cheap):
   ```bash
   python3 .claude/skills/folktale-harvester/scripts/catalogue_ashliman.py "<Culture>" [aliases...]
   ```
   Pass sensible aliases (`"Irish" Ireland Celtic`, `"Norwegian" Norway`). It
   writes `index/catalogue_<culture>_ashliman.csv` and prints the collectors to chase.
2. Gather more titles from other aggregators (web search + the APIs in
   `references/sources.md`): Wikisource book indexes, Wikipedia "list of <culture>
   folktales" pages, and the tables of contents of candidate Gutenberg editions
   (`split_gutenberg_epub.py --inspect` prints them). Save each source's titles to
   its own small CSV with a `title` column, named for its source (e.g.
   `/tmp/<culture>_wikisource.csv`).
3. Merge everything into one deduped master `index/catalogue_<culture>.csv`:
   ```bash
   python3 .../scripts/catalogue_merge.py "<Culture>" index/catalogue_<culture>_ashliman.csv /tmp/<culture>_*.csv
   ```
   It reports the unique count and warns if you're under 150. If short, find more
   aggregators and re-run — it auto-includes the existing master and accumulates
   (see the second sweep below).

### Phase 1b — Second sweep (the "did I miss an aggregator?" pass)
Once you think you've found everything, deliberately look **again** for sources
you skipped the first time — now informed by what you found: the collector names
that surfaced, the ATU types present, the era and region. Search for those
specifically (e.g. a named collector's other books, a regional digital library, a
national Wikisource). Dump any new titles to a CSV and re-run `catalogue_merge.py`
— it's idempotent, so this only adds. This second pass is cheap (cached crawls,
small searches) and routinely finds editions the first pass missed.

### Phase 1c — Survey
Write `sources/<culture>_survey.md`: every candidate **edition** with a verdict
(**HARVEST / CATALOGUE ONLY / SKIP**) and the reason, per `references/copyright.md`.
This is the project's tradition and your audit trail. Prefer editions that
together get you toward ~100 harvestable tales.

### Phase 2 — Harvest cleared editions (100+ tales — more is better)
Harvest every edition marked HARVEST; don't stop at 100 if more public-domain
editions exist — usually several books, and the more the merrier. For each, pick the matching tool
and write a small JSON config (each tool's docstring has the schema and an
example). Output goes to `corpus/<collection>/` as `NNN_<slug>.html`. Name
collections `<culture>_<author>_en` (e.g. `japanese_ozaki_en`).

- **Project Gutenberg** → download the EPUB (no images) into `sources/`, then:
  ```bash
  python3 .../scripts/split_gutenberg_epub.py --inspect sources/<book>.epub   # see structure
  python3 .../scripts/split_gutenberg_epub.py <config.json>
  ```
- **Wikisource** → `python3 .../scripts/fetch_wikisource.py <config.json>`
- **archive.org OCR** → always inspect first, then split:
  ```bash
  python3 .../scripts/fetch_archive_ocr.py --inspect <archive_id>   # ALWAYS first
  python3 .../scripts/fetch_archive_ocr.py <config.json>
  ```
  `--inspect` prints the contents block (your `titles` list — fix OCR garble by
  hand), suggests a `body_start` anchor, and flags front-matter repeats. OCR
  layout is unpredictable, so this step is not optional.

**OCR gotchas (learned the hard way):**
- *Front-matter repeats.* Scanned books often list their titles in **two** front
  sections (a contents page AND a half-title), which throws off where the body
  starts and dumps the whole book into the last tale. If `--inspect` reports
  repeats, set `body_start` to a phrase from the first tale's opening prose — it
  trims all front matter cleanly (matching is whitespace-flexible, so OCR
  double-spacing is fine).
- *Garbled headings.* A title may be OCR-mangled ("PRINCE"→"PEIXCE"); match on a
  distinct intact word from it (e.g. "Kashmir") via a `[display, match]` pair.
- *Back matter.* Use `end_marker_caps` (e.g. "GLOSSARY"/"INDEX") so the last tale
  doesn't swallow the appendix.
- *Nested / frame books.* If a book is a frame story whose chapters embed
  sub-stories interleaved with "continuations", the config approach gets brittle
  — write a thin bespoke fetcher instead (next paragraph). Discrete-title books
  and simple frame books (sub-stories with their own headings) split fine via config.

If a source is too irregular for the config-driven tools, write a thin bespoke
fetcher that **imports `folktale_lib`** (it gives you `DOC_TEMPLATE`, `slugify`,
`wikisource_parse`, `archive_djvu`, `html_to_paragraphs`, `ocr_to_paragraphs`,
`write_collection`, `record_source`). Don't re-derive the plumbing — that's the
whole point of the library. Keep new bespoke fetchers in the project `scripts/`;
`scripts/fetch_lorimer_persian.py` and `fetch_levy_persian.py` are worked examples
(split on a body marker, merge OCR running-head fragments, trim front/back matter).

After each edition, spot-check a couple of output files: real prose, right title,
no front-matter/license bleed-in, multi-part tales kept whole.

### Phase 3 — Dedup & integrate
1. Dedup the new collections (and against existing ones if overlap is plausible):
   ```bash
   python3 .../scripts/dedup_corpus.py <new_collection> [others...]
   ```
   Remember the distinction in the script's docstring: **exact/near text matches
   are droppable duplicates; same-title-but-different-words are VARIANTS — keep
   them.** The script only reports; you decide what (if anything) to delete.
2. Register each new collection in `scripts/build_manifest.py` by appending a row
   to its `COLLECTIONS` list `(subdir, author, lang, source)`, then run it:
   ```bash
   python3 scripts/build_manifest.py
   ```
   (`folktale_lib.record_source` also logs provenance to
   `index/harvested_sources.csv` automatically — use that to fill the row.)

### Phase 4 — Report
Summarize: collections added, tale counts per collection, total new tales, what
was catalogued-only and why, and any leads left for a future pass (editions you
couldn't clear, OCR books worth a closer look). Update the project memory if the
user keeps one.

## Conventions that keep the corpus uniform
- One tale per file, `corpus/<collection>/NNN_<slug>.html`, zero-padded sequence.
- Use the bundled `DOC_TEMPLATE` (via `write_collection`) so every tale has the
  same shape the manifest/dedup expect — don't invent a new HTML layout.
- Prefer the highest-fidelity source available for a given collection (Gutenberg
  > Wikisource > OCR). Flag OCR provenance in the tale note.
- Native Python with the stdlib + `curl` (as the existing scripts do); responses
  are cached under `.cache/harvester/` so reruns are cheap and polite.
