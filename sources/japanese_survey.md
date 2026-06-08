# Japanese folk-tale sources — survey (2026-06-07)

Public-domain harvest survey produced by the `folktale-harvester` skill. Verdict
key: **HARVEST** (full text collected), **CATALOGUE ONLY** (metadata only —
copyright/borrow), **SKIP** (not relevant / redundant). PD test: US, edition
published before 1929 or on Project Gutenberg. See references/copyright.md.

## Catalogue
`catalogue_ashliman.py "Japanese" Japan` → `index/catalogue_japanese.csv`,
19 entries (of 3,231). Ashliman is ATU-type-indexed, so its per-culture depth is
shallow for Japan; the stronger lead source here was the Gutenberg edition search.
No attributed collectors surfaced from Ashliman — leads came from Gutendex.

## Editions assessed

| Source | Edition | Year | Verdict | Notes |
|---|---|---|---|---|
| Gutenberg #4018 | Ozaki, *Japanese Fairy Tales* | 1908 | **HARVEST** | 22 tales → `corpus/japanese_ozaki_en/`. Canonical collection. |
| Gutenberg #35853 | James, *Green Willow and Other Japanese Fairy Tales* | 1910 | **HARVEST** | 38 tales → `corpus/japanese_james_en/`. |
| Gutenberg #73293 | Nixon-Roulet, *Japanese Folk Stories and Fairy Tales* | 1908 | HARVEST (next pass) | PD-clear; not yet collected in this run. |
| Gutenberg #13015 | Mitford, *Tales of Old Japan* | 1871 | HARVEST (next pass) | PD-clear; mixes fairy tales with essays/sermons — needs selective heading config. |
| Gutenberg #45933 | *Romances of Old Japan* | 1918 | HARVEST (next pass) | PD-clear. |
| Gutenberg #19945 | De Benneville, *Bakemono Yashiki (The Haunted House)* | 1920 | HARVEST (next pass) | PD-clear; ghost/legend tales. |

## Collected this run
- `corpus/japanese_ozaki_en/` — 22 tales (Ozaki 1908), Gutenberg #4018, full text.
- `corpus/japanese_james_en/` — 38 tales (James 1910), Gutenberg #35853, full text.
- Total: **60 new Japanese tales.** Manifest 1271 → 1331.

## Dedup
`dedup_corpus.py japanese_ozaki_en japanese_james_en`: 0 text duplicates, 1
cross-collection same-title variant ("The Tongue-Cut Sparrow", Jaccard 0.005 —
independent retellings, **kept**). The two books also share Momotaro, Urashima,
Matsuyama Mirror, and Jelly-Fish tales as variants under differing titles — all
kept, as variants are the point.

## Leads for a future pass
- Harvest the four PD-clear Gutenberg editions above (#73293, #13015, #45933, #19945).
- Wikisource Japan category (e.g. Lang's coloured Fairy Books contain Japanese
  tales) for additional proofread editions.
- Lafcadio Hearn's PD collections (*Kwaidan* 1904, *Japanese Fairy Tales*) — verify
  edition dates; strong candidates.
