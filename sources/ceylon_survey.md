# Ceylon (Sinhalese) folk tales — edition survey

Run date: 2026-06-08. Culture: **Ceylon / Sinhalese** (Sri Lanka). Harvested as a
distinct culture during the Indian run because it surfaced in the Gutenberg sweep
and is the largest remaining clean public-domain South-Asian trove — but it is
*not* India, so it lives in its own `ceylon_*` collections, not `indian_*`.

US public-domain gate per `references/copyright.md`: all editions are pre-1929
Gutenberg → cleared.

**Catalogue:** `index/catalogue_ceylon.csv` — 276 titles.
**Harvested:** 276 tales across 3 volumes.

## HARVEST — done

| Edition | Collector | Yr | Gutenberg | Tales | Collection |
|---|---|---|---|---|---|
| Village Folk-Tales of Ceylon, Vol. 1 | Henry Parker | 1910 | #56614 | 75 | `ceylon_parker_v1_en` |
| Village Folk-Tales of Ceylon, Vol. 2 | Henry Parker | 1914 | #57399 | 103 | `ceylon_parker_v2_en` |
| Village Folk-Tales of Ceylon, Vol. 3 | Henry Parker | 1914 | #58889 | 98 | `ceylon_parker_v3_en` |

**Total: 276 tales.** Parker's three volumes are the definitive early English
collection of Sinhalese village folklore (gathered from cultivators, washermen,
Vaeddās, etc.), organised by the caste of the teller.

### Splitting notes
- Tales at `h2`, each preceded by a bare `No. N` number-heading and grouped under
  caste-section dividers ("STORIES TOLD BY THE CULTIVATING CASTE AND VAEDDĀS." etc.)
  — all skipped via `skip_headings`; tale titles kept.
- Titles carry trailing footnote digits ("The Story of Senasurā1") — stripped with
  `title_strip` `\d+$`.
- Dropped the per-volume `Colophon`. No short stubs or section-header bleed left.
- Dedup: **0** exact/near duplicates within or across the three volumes.

## Leads for a future pass (Ceylon / wider South Asia)
- **Told on the Pagoda: Tales of Burmah** (#36171), **Shan Folk-Lore Stories**
  (#32375) — Burmese/Shan, own culture.
- **Folk Tales from Tibet** (#75000) — distinct from the Indian-source Tibetan
  Tales already in `indian_tibetan_en`.
- Parker also published *Ancient Ceylon* (archaeology, not tales — skip).
