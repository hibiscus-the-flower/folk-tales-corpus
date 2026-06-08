# Indian folk tales — edition survey

Run date: 2026-06-08. Culture: India (South Asian). US public-domain gate per
`references/copyright.md` (edition published **before 1929**, or on Project
Gutenberg → harvestable). All editions below are Gutenberg, hence cleared; the
verdict column records relevance/quality decisions, not copyright doubt.

**Catalogue:** `index/catalogue_indian.csv` — 745 unique titles (57 cross-confirmed).
**Harvested:** 674 tales across 20 collections (wave 1: 13 collections / 541 tales;
wave 2 below: 7 collections / 133 tales).

A persistent caution with Indian collections: the Raj-era anthologists reprinted
each other. **Joseph Jacobs's *Indian Fairy Tales* (1892) is an anthology** that
reproduced Steel, Frere, Campbell and Kingscote, sometimes verbatim — see the
dedup note at the bottom.

## HARVEST — done

| Edition | Author / collector | Yr | Gutenberg | Tales | Collection |
|---|---|---|---|---|---|
| Tales of the Punjab: Folklore of India | Flora Annie Steel | 1894 | #6145 | 42 | `indian_steel_en` |
| Indian Fairy Tales | Joseph Jacobs (anthology) | 1892 | #7128 | 23 | `indian_jacobs_en` |
| Folk-Tales of Bengal | Lal Behari Day | 1883 | #38488 | 22 | `indian_day_en` |
| Folklore of the Santal Parganas | Cecil Henry Bompas | 1909 | #11938 | 195 | `indian_bompas_en` |
| Old Deccan Days; or, Hindoo Fairy Legends | Mary Frere | 1868 | #36696 | 24 | `indian_frere_en` |
| Tales of the Sun; or, Folklore of Southern India | G. Kingscote & S. M. Natesa Sastri | 1890 | #37002 | 26 | `indian_kingscote_en` |
| The Talking Thrush, and Other Tales from India | W. Crooke & W. H. D. Rouse | 1899 | #30635 | 43 | `indian_crooke_en` |
| The Giant Crab, and Other Tales from Old India | W. H. D. Rouse | 1897 | #36039 | 28 | `indian_rouse_en` |
| Simla Village Tales; or, Folk Tales from the Himalayas | Alice E. Dracott | 1906 | #58816 | 57 | `indian_dracott_en` |
| Santal Folk Tales | A. Campbell | 1891 | #35060 | 23 | `indian_campbell_en` |
| Folk Tales of Sind and Guzarat | C. A. Kincaid | 1925 | #76982 | 19 | `indian_kincaid_en` |
| Jataka Tales | Ellen C. Babbitt | 1912 | #62514 | 18 | `indian_babbitt_jataka_en` |
| More Jataka Tales | Ellen C. Babbitt | 1922 | #7518 | 21 | `indian_babbitt_more_en` |

**Wave-1 subtotal: 541 tales.**

### HARVEST — wave 2 (second sweep)

| Edition | Author / collector | Yr | Source | Tales | Collection |
|---|---|---|---|---|---|
| Twenty-Two Goblins (Vetālapañcaviṃśati) | tr. Arthur W. Ryder | 1917 | Gutenberg #2290 | 24 | `indian_goblins_en` |
| Tibetan Tales, Derived from Indian Sources | Schiefner & Ralston | 1882 | Gutenberg #66870 | 50 | `indian_tibetan_en` |
| Deccan Nursery Tales | C. A. Kincaid | 1914 | Gutenberg #11167 | 20 | `indian_deccan_nursery_en` |
| Indian Fairy Tales | Maive Stokes | 1879 | Wikisource | 14 | `indian_stokes_en` |
| Vikram and the Vampire (Baitāl Pachīsī) | tr. R. F. Burton | 1870 | Gutenberg #2400 | 11 | `indian_vikram_en` |
| Hindu Tales from the Sanskrit | S. M. Mitra & Mrs. A. Bell | 1919 | Gutenberg #11310 | 9 | `indian_hindu_sanskrit_en` |
| The Magic Bed: East Indian Fairy-Tales | Hartwell James | 1906 | Gutenberg #37708 | 5 | `indian_magic_bed_en` |

**Wave-2 subtotal: 133 tales. GRAND TOTAL: 674 tales across 20 collections.**

Wave-2 notes: Goblins/Tibetan/Vikram are the classic **Sanskrit story-cycles**
(Vetāla, Avadāna/Jātaka-derived, Baitāl Pachīsī) — literary folklore, kept whole
(multi-chapter tales stitched). Goblin titles were bland h3 headings ("FIFTH
GOBLIN"); re-titled from the TOC ("The Parrot and the Thrush (Goblin 3)"). Stokes
came from Wikisource (only 14 of ~30 tales are transcribed); stripped 2 title-echo
paragraphs. Magic Bed's EPUB doubled each tale with an uppercase half-title page —
dropped the 5 stub pages. Dropped: Tibetan INDEX, Hindu-Sanskrit translator notes,
Goblins/Magic-Bed/Deccan colophons & a "THE END". Wave-2 added **zero** duplicates
against the existing 13 collections.

### Cleanup applied during harvest
- **Jacobs dropcaps:** the EPUB renders each tale's opening capital in a
  `<div class="figleft1">` that the splitter dropped ("he Bodhisatta…"). All 29
  initials recovered from the raw EPUB and patched.
- **Steel illustration captions:** 21 `[Illustration: …]` paragraphs stripped.
- **Bompas:** the book mixes folk tales with an ethnographic customs/superstitions
  section (transmigration, witchcraft beliefs, hunting customs, etc.). Dropped 13
  non-narrative belief-notes + 3 encoding/availability stubs; kept the 195 actual
  tales (incl. the 22-tale numbered Ho/Kolhan appendix).
- **End-matter bleed:** trimmed trailing publisher's-catalogue advertisements from
  Day #022 (Macmillan colour-books list) and Rouse #028 (David Nutt gift-book
  list, ~120 ad paragraphs), plus stray "THE END" lines and per-collection
  `Colophon`/`Corrections` files.
- **Kincaid:** removed a stray bare section-header file ("Round About Nasik").

## CATALOGUE ONLY / not harvested

| Edition | Author | Why not harvested |
|---|---|---|
| Indian Fairy Tales | Maive Stokes (1879) | Not on Gutenberg as a clean EPUB; 30 titles pulled from Wikisource TOC into the catalogue. A full harvest (Wikisource subpages) is a good next pass. |
| Folk-Tales of Kashmir | J. Hilton Knowles (1888) | PD and a major collection; no Gutenberg edition located, Wikisource index 404'd this run. Catalogue lead — chase archive.org full-view OCR next. |
| Indian Tales | Rudyard Kipling (#8649) | SKIP — Kipling's own literary short fiction, not folklore. |
| Folk Lore Notes, Vol. I — Gujarat | A. M. T. Jackson (#56144) | CATALOGUE ONLY — ethnographic belief/custom notes, not narrative tales. |
| Buddhist Birth Stories (Jataka, Vol. 1) | T. W. Rhys Davids (#51880) | Heavy scholarly apparatus; the Babbitt Jataka retellings give cleaner per-tale splits. Lead for a deeper Jataka pass. |
| The Panchatantra / Hitopadesa | (Ryder 1925 etc.) | Not harvested this run — the classic fable cycles are a strong next target (verify a pre-1929/Gutenberg edition). |
| Omens & Superstitions of S. India; Popular Religion & Folk-Lore of N. India (Crooke) | Thurston; Crooke | SKIP as tale sources — ethnography, not narrative. Useful catalogue/context only. |
| Ramayana / Mahabharata translations | Griffith, Dutt, etc. | SKIP — epics, out of scope for folk-tale corpus. |

## Dedup note (kept vs dropped)
`dedup_corpus.py` flagged 9 Jacobs↔source near-duplicates (Jacobs anthologised the
field collectors). Decision:
- **Dropped 6 verbatim reprints from Jacobs** (Jaccard ≥ 0.77: Farmer & the
  Money-lender, Punchkin, Son of Seven Queens/Mothers, How Sun-Moon-and-Wind
  went to Dinner, Tiger-Brahman-Jackal, Lambikin) — kept the original
  collectors' versions (Steel/Frere).
- **Kept 3 as genuine variants** (Jaccard < 0.70: Pride goeth before a Fall,
  The Magic Fiddle, The Soothsayer's Son) — substantially reworded.
- Same-title / low-overlap pairs (e.g. Steel vs Bompas "The Two Brothers";
  Jacobs vs Rouse "The Talkative Tortoise") are **variants — kept**.
Full report: `index/dedup_report.csv`.

## Adjacent South-Asian collections found but NOT harvested (scope = India proper)
These are on Gutenberg (PD) but belong to neighbouring cultures; left out to keep
the `indian_*` collections culturally clean. Strong candidates for their own
culture-tagged harvest if wanted:
- **Village Folk-Tales of Ceylon**, H. Parker, 3 vols (Gutenberg #56614/57399/58889,
  1910–14) — ~260 Sinhalese tales. The single biggest unharvested South-Asian trove.
- **Told on the Pagoda: Tales of Burmah** (#36171) & **Shan Folk-Lore Stories** (#32375) — Burmese/Shan.
- **Folk Tales from Tibet** (#75000) — distinct from the Indian-source Tibetan Tales already harvested.

## SKIPPED this run (relevance/quality)
- **Tales from the Hindu Dramatists** (R. N. Dutta, #18285) — only ~8 retold
  Sanskrit *plays* (Sakuntala etc.), and the EPUB's front matter is too irregular
  to split cleanly. Low folk-tale value; skipped.

## Leads for a future pass (India proper)
- **Knowles** *Folk-Tales of Kashmir* — no Gutenberg ed.; chase archive.org OCR.
- **Panchatantra / Hitopadesa** — no clean Gutenberg ed. surfaced (only fable
  anthologies #13815 etc.); find a pre-1929 standalone translation.
- **Swynnerton** *Romantic Tales from the Panjab* — not on Gutenberg; archive.org.
- **Natesa Sastri** *Folklore in Southern India* / *Dravidian Nights* — archive.org.
- **Ramaswami Raju** *Indian Fables* — archive.org.
- **Kathá Sarit Ságara / Ocean of Story** (Tawney, #40588) — vast but dense; needs
  a bespoke splitter. Catalogue lead.
- Remaining ~16 untranscribed **Stokes** tales; deeper **Jātaka** (Rhys Davids /
  Francis & Thomas full sets, #51880).
