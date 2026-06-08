# Persian folk-tale sources — survey (2026-06-07)

Produced by the `folktale-harvester` skill. Verdict key: **HARVEST** (full text
collected), **CATALOGUE ONLY**, **SKIP**. PD test: US, edition pre-1929 or on
Project Gutenberg. See references/copyright.md.

## Catalogue
- `catalogue_ashliman.py "Persian" Persia Iran Iranian` → 4 entries (Ashliman is
  very thin for Persian). Merged with harvested-edition TOCs →
  `index/catalogue_persian.csv`, **68 titles**. Below the 150 floor — the gap is
  aggregators not yet mined (Wikisource, Wikipedia "list of Persian folktales",
  more edition TOCs). Recorded as a lead, not a stopping point.

## Editions assessed

| Source | Edition | Year | Verdict | Notes |
|---|---|---|---|---|
| archive.org `cu31924029903881` | Lorimer & Lorimer, *Persian Tales* | 1919 | **HARVEST** | **50 tales** → `persian_lorimer_en`. Genuine oral folk tales (Kermani + Bakhtiari). OCR; split on the "THE STORY OF …" body marker via `scripts/fetch_lorimer_persian.py`. The keystone source. |
| Gutenberg #60316 | *The Bakhtyār Nāma* (Clouston tr.) | 1883 | **HARVEST** | 10 embedded stories → `persian_bakhtyar_en`. Folk frame-romance; split on h4 "STORY OF …". |
| Gutenberg #24473 | *The Cat and the Mouse: A Book of Persian Fairy Tales* | ~1900s | **HARVEST** | 4 tales → `persian_catmouse_en` (Altemus Fairy Tales Series). |
| archive.org `cu31924012567420` | Olcott, *Tales of the Persian Genii* | 1919 | CATALOGUE ONLY (deferred) | PD, but a deeply nested frame narrative ("Fountain of the Genii" with interleaved continuations) — does not split into clean discrete folk tales without fragile custom logic. Strong lead for a careful future pass (~20–25 nested stories). |
| Gutenberg #60471 | Saʿdi, *The Bustān* | (med.) | SKIP (genre) | PD and tale-rich (111 sections), but classical didactic **verse**; many sections are discourses, not narrative folk tales. Different genre — excluded to keep the count clean (cf. the corpus's literary vs. oral distinction). |
| Gutenberg #13060 | *Persian Literature* (Shah Nameh, Gulistan, etc.) | 1900 | SKIP (genre/structure) | Classical literature (epic + Saʿdi). Tale-rich but literary, and bundled in a large compilation that's awkward to split. Lead for classical-material pass. |
| Gutenberg #57827 | Renninger, *The Story of Rustem … Persian hero tales* | 1909 | CATALOGUE ONLY (deferred) | PD; children's retelling of Shāhnāmeh episodes. Epic-derived rather than folk; deferred. |
| archive.org `threedervischeso00levyuoft` | Levy, *The Three Dervishes and other Persian Tales* | 1923 | **HARVEST** | **20 tales** → `persian_levy_en`. Full-view PD. OCR; bespoke split (`scripts/fetch_levy_persian.py`) — trims front-matter repeats + glossary, then sequential heading match. Partly nested; embedded stories split out cleanly. |

## Collected this run
- `persian_lorimer_en` — 50 tales (Lorimer 1919), archive OCR, full text.
- `persian_levy_en` — 20 tales (Levy 1923), archive OCR, full text.
- `persian_bakhtyar_en` — 10 tales (Clouston 1883), Gutenberg, full text.
- `persian_catmouse_en` — 4 tales (Altemus), Gutenberg, full text.
- **Total: 84 clean Persian folk tales.** Manifest 1331 → 1415.

## Dedup
`dedup_corpus.py` over all three: 0 exact, 0 near, 0 cross-collection — independent
collections, no overlap.

## Why 64 and not 100
64 is the count of *genuine, clean* Persian folk tales reachable this run. The
remaining clear PD routes to 100+ are either structurally messy OCR (Olcott's
nested frame) or a different genre (Saʿdi's classical verse, Shāhnāmeh epic).
Per the skill's quality rule, those weren't padded in silently. Paths to more:
1. Levy, *Three Dervishes* (1928) — verify archive access, harvest.
2. Olcott — a careful bespoke split of its nested stories.
3. Classical Saʿdi/Shāhnāmeh material, clearly labelled (as the corpus already
   does for literary vs. oral Jewish material), if that scope is wanted.
4. Mine Wikisource / Wikipedia list pages to lift the catalogue toward 150.
