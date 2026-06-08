# Jewish Repertoire — Consolidation & Dedup Report
*Run 2026-06-04*

## Scope

All 8 Jewish/Yiddish collections in the corpus (736 entries: 607 full-text + 129
Weinreich stubs, ~748k words).

| Collection | Source | Tales | Words | Fidelity |
|---|---|---:|---:|---|
| `ginzberg_legends_en` | Ginzberg, *Legends of the Jews* (1909–13) | 451 | 498,435 | clean |
| `rapaport_en` | Rapaport, *Tales and Maxims from the Midrash* (1907) | 18 | 82,766 | OCR |
| `landa_en` | Landa, *Jewish Fairy Tales and Legends* (1919) | 25 | 51,050 | clean |
| `jewish_fairy_book_en` | Friedlander, *The Jewish Fairy Book* (1920) | 23 | 41,572 | clean |
| `isaacs_en` | Isaacs, *Stories from the Rabbis* (1893) | 17 | 35,260 | OCR |
| `hebrew_tales_en` | Hurwitz, *Hebrew Tales* (1826) | 65 | 24,036 | clean |
| `friedlander_en` | Friedlander, *Jewish Fairy Stories* (1918) | 8 | 15,070 | clean |
| `weinreich_en` | Weinreich/YIVO, *Yiddish Folktales* (1988) | 129 | 0 | stub |
| **Total** | | **736** | **748,189** | |

## Dedup result — nothing to remove

Method: MinHash (96 hashes) over word 4-grams, on all 607 full-text tales;
pairwise Jaccard. See `scripts/dedup_jewish.py`, report in
`index/dedup_jewish_report.csv`.

- **Exact text duplicates: 0**
- **Near duplicates (Jaccard ≥ 0.55): 0**
- **Cross-collection same-title pairs: 0**
- **Max pairwise similarity between *any* two tales: 0.028** — i.e. essentially no
  shared verbatim text anywhere in the repertoire.

Why so clean: although many tales share a Talmudic/Midrashic *source*, each
collection is an **independent English retelling/translation**, so they share
almost no verbatim wording. Even two tales of the identical story (e.g. Adam's
dust gathered from the four corners of the earth — `jewish_fairy_book/The
Citizen of the World` vs `ginzberg/The Creation of Adam`) score ~0.01.

**Conclusion:** these are *variants*, not duplicates. None were deleted.

## Consolidation outputs

1. **`index/jewish_repertoire.csv`** — unified catalogue of all 736 entries
   (collection, file, title, author, year, source-type, fidelity, word count).
2. **`index/jewish_variant_candidates.csv`** — cross-collection tales that are
   likely **retellings of the same source story**, linked by shared *distinctive
   proper nouns* (rare names occurring in ≤ 8 tales). Since variants share no
   verbatim text, this name-overlap signal is the only way to surface them.
   For human review — NOT auto-merged. 9 high-confidence pairs, including:
   - *King Alexander's Adventures* (Landa) ↔ *Alexander of Macedon* (Rapaport) — Alexander-romance cycle
   - *King Solomon's Carpet* (Friedlander) ↔ Isaacs Solomon tales — the Solomon / Ashmodai / Shamir cycle
   - *The Prince and the Rabbi* / *Messiah* — the Christian-disputation (*Shevet Yehudah*) tales linking both Friedlander books & Rapaport
   - *The Magic Lamp* ↔ *Teacher of the Kabbalah* — Kabbalah legends
   - Ginzberg Joseph legends ↔ Rapaport Genesis/Leviticus Rabba — the Joseph & Antoninus material

## Quality check

No leaked Wikisource reference/footnote cruft in any Jewish collection (the
`reference`/`cite-bracket`/`mw-cite-backlink` classes are confined to
`andersen_ru`, out of scope; the single `poem` in Landa is a legitimate verse).

Scripts: `scripts/dedup_jewish.py`, `scripts/consolidate_jewish.py`.
