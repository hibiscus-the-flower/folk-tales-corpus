# YIVO Archive Survey — Yiddish Folk Tales
*Compiled 2026-06-04*

## Summary

The YIVO Institute for Jewish Research holds the most important repository of Yiddish folk-tale materials in the world. This document surveys what exists, what is digitized, and where to find it.

---

## 1. Primary YIVO Archival Holdings

### Records of the YIVO Ethnographic Committee (RG 1.2)
- **Dates:** 1911–1940
- **Extent:** 7.7 linear feet (18 boxes)
- **Location:** Center for Jewish History, 15 West 16th St, New York NY
- **Finding aid:** https://yivoarchives.yivo.org (search RG 1.2)
- **Access:** By appointment; archives@yivo.cjh.org
- **Digitization status:** Not fully digitized; no public online text

**Contents relevant to folk tales:**
- ~93 tales and legends concerning rabbis; 39 anecdotes
- Stories about eminent Lithuanian rabbis
- 15 jokes with 2 riddles
- Lying stories, Hershele Ostropolyer tales, Chelm fool stories, Hasidic tales
- Historical legends (Chmielnicki era, blood libel, pogroms)
- From the Invayskult sub-series: 228 anecdotes, tales, and jokes (ca. 1927)
- From the Invayskult sub-series: 35 wonder tales transcribed phonetically (ca. 1930)

**Series structure:**
- Series I: YIVO Ethnographic Committee (1909–1940)
  - Subseries 1: Administrative Records
  - Subseries 2: Folklore Materials (Boxes 1–6)
  - Subseries 3: Linguistic Materials
- Series II: S. Ansky Jewish Historical Ethnographic Society (1885–1940)
- Series III: Invayskult (1907–1941)
  - Subseries 2: Proverbs and Folktales (Boxes 11–13)

### RG 125: Jewish Folklore
- Miscellaneous materials: folk poetry, proverbs, sayings, marriage contracts, amulets
- Chairperson: Judah Loeb Cahan (YIVO Folklore Section)

### RG 202: Judah Loeb Cahan Papers
- Major folk-tale collections used in *Shtudyes vegn yidishe folksshaung* (1952)
- Cahan chaired the YIVO Folklore Section

### RG 206: Papers of A. Litwin
- Series III: Jewish folklore materials compiled by Yiddish journalist/ethnographer

### RG 2299: YIVO Folksong Project
- 320 hours of 2,000 folk songs (dir. Barbara Kirshenblatt-Gimblett, 1973–75)

---

## 2. Key Published YIVO Collection (Primary Target)

### Beatrice Weinreich (ed.), *Yiddish Folktales* (Pantheon / YIVO, 1988)
- **ISBN:** 978-0-8052-1090-3
- **Translator:** Leonard Wolf
- **Source:** Drawn directly from YIVO Ethnographic Committee (RG 1.2) collections
- **Content:** ~200 tales gathered by zamlers in Eastern Europe, 1920s–1930s
- **Internet Archive:** https://archive.org/details/yiddishfolktales00wein — requires library borrowing
- **Corpus status:** 129 stub files created in `corpus/weinreich_en/` (titles recovered from Google Books preview); estimated 71 additional tales exist in sections not visible in the preview

**Tale categories:**
1. Allegorical Tales (14 titles recovered)
2. Children's Tales (17 titles recovered)
3. Wonder Tales (15 titles recovered)
4. Pious Tales (21 titles recovered)
5. Humorous Tales (14 titles recovered)
6. Legends — Rebbes & Disciples (29 titles recovered)
7. Supernatural Tales (19 titles recovered)

**To complete the corpus:** Borrow the book via Internet Archive or a library and fill in the stub files in `corpus/weinreich_en/`.

---

## 3. Related J.L. Cohen Source

### J.L. Cohen, *Folks mayses* (Yiddish folk tales)
- Source for the Ruth Rubin tape recordings held in the YIVO Ruth Rubin Legacy Archive
- Includes: "Der royfe un der shuster," "Ali Baba" retelling, "The Musicians of Bremen" retelling, "Tom Thumb" retelling
- Online: recorded audio at https://ruthrubin.yivo.org/categories/browse/Item+Type+Metadata/Tape+Name/Tape+55+-+Yiddish+Folktales

---

## 4. YIVO Digital Resources (Online)

| Resource | URL | Folk-tale relevant? |
|---|---|---|
| YIVO Encyclopedia of Jews in Eastern Europe | encyclopedia.yivo.org | Yes — articles on Folklore, Cahan, Bastomski, etc. |
| Ruth Rubin Legacy: Archive of Yiddish Folksongs | ruthrubin.yivo.org | Partial — "Tape 55" is folk tales |
| People of A Thousand Towns | yivo1000towns.cjh.org | Images only |
| Edward Blank Vilna Collections | vilnacollections.yivo.org | Possible manuscripts — search needed |
| YIVO Digital Archive on Jewish Life in Poland | polishjews.yivoarchives.org | Partial |
| Guide to the YIVO Archives | yivoarchives.yivo.org | Finding aids |

---

## 5. Full English Texts Collected (in Corpus)

### 5a. Public-domain full texts — HARVESTED ✓

These are now in the corpus as per-tale HTML with complete text. NOTE: all three
are English **retellings of Jewish legendary / Talmudic-Midrashic material for
children**, not transcriptions of East-European oral Yiddish *mayses*. They share
the tradition but are a different register from the YIVO zamler collection.

| Corpus label | Source | Tales | Source type |
|---|---|---|---|
| `landa_en` | Gertrude Landa, *Jewish Fairy Tales and Legends* (Gutenberg #26711, 1919) | 25 | Talmud/Midrash retellings |
| `friedlander_en` | Gerald Friedlander, *Jewish Fairy Stories* (Gutenberg #72880, 1918) | 8 | Talmud/Midrash retellings |
| `jewish_fairy_book_en` | Gerald Friedlander, *The Jewish Fairy Book* (Wikisource, 1920) | 23 | Talmud/Midrash retellings; each tale cites its rabbinic source |
| `hebrew_tales_en` | Hyman Hurwitz, *Hebrew Tales* (Wikisource, 1826) | 65 | Talmud/Midrash tales, fables & facetiae (3 furnished by S.T. Coleridge); some entries are moral maxims/commentary |
| `ginzberg_legends_en` | Louis Ginzberg, *The Legends of the Jews*, vols 1–4 (Gutenberg #1493/1494/2881/2882, 1909–1913, tr. Szold/Radin) | 451 | Canonical English synthesis of Jewish aggadah from Talmud/Midrash; biblical legend (Creation→Esther), a different register from oral folk *mayses*. Each file tagged with its "book" (biblical figure/era). |

**Total harvested clean PD texts: 572 tales/legends.**

Fetchers: `scripts/fetch_yiddish.py` (Landa, Friedlander Stories),
`scripts/fetch_jewishfairybook.py` (Jewish Fairy Book via MediaWiki API),
`scripts/fetch_hebrewtales.py` (Hebrew Tales via MediaWiki API),
`scripts/fetch_ginzberg.py` (Legends of the Jews, vols 1–4, from Gutenberg HTML).

### 5d. OCR-sourced full texts — HARVESTED ✓ (lower fidelity)

Only on Internet-Archive OCR (no clean Gutenberg/Wikisource edition). Text is
lightly cleaned but contains occasional OCR errors and drop-cap garble; flagged
as OCR in each file and in the manifest `source`. Fetcher: `scripts/fetch_ocr_tales.py`.

| Corpus label | Source | Items | Notes |
|---|---|---|---|
| `isaacs_en` | Abram S. Isaacs, *Stories from the Rabbis* (1893) | 17 | Discrete titled tales — good fit |
| `rapaport_en` | Samuel Rapaport, *Tales and Maxims from the Midrash* (1907) | 18 | One file per Midrash source-book (Gen. Rabba, Exod. Rabba…); each file is many short tales/maxims run together, not a single tale |

**Total OCR texts: 35.**  **Grand total harvested PD: 607.**

### 5e. Assessed and SKIPPED

- H. Polano, *The Talmud: Selections* (1876) — continuous biblical-history retelling
  in Parts/Chapters, garbled OCR headings, not discrete tales, and heavily redundant
  with Ginzberg (which we already hold at higher fidelity). Sacred-texts copy is
  Cloudflare-gated. Not worth harvesting.

### 5b. Authentic Yiddish *mayses* — CATALOGUED, text copyright-restricted

| Corpus label | Source | Tales | Status |
|---|---|---|---|
| `weinreich_en` | B. Weinreich / YIVO, *Yiddish Folktales* (1988) | 129 cataloged | Stubs only — borrow-only on Internet Archive |

### 5c. Major copyright-restricted full-text sources (NOT harvested)

The authentic Yiddish oral folk *mayses* in English are concentrated in three
copyrighted collections, all **borrow-only** on Internet Archive:

| Work | Year | Notes |
|---|---|---|
| B. Weinreich (ed.), *Yiddish Folktales* | 1988 | ~200 tales straight from YIVO RG 1.2 — the gold standard |
| Nathan Ausubel (ed.), *A Treasury of Jewish Folklore* | 1948 | 800+ items; Bantam abridged ed. has an open `_djvu.txt` on archive.org (item B-001-013-718) but is still under copyright |
| Moses Gaster (tr.), *Ma'aseh Book* | 1934 | English of the classic 1602 Yiddish *Mayse-bukh* — the foundational printed mayse collection; borrow-only |

---

## 6. Next Steps

1. **Borrow and transcribe Weinreich** — Use Internet Archive lending to fill `corpus/weinreich_en/` stubs
2. **Search Vilna Collections** — Search vilnacollections.yivo.org for folk tale manuscripts in the prewar Vilna YIVO archive
3. **S. Ansky Ethnographic Expedition materials** — The YIVO collection includes materials from Ansky's 1912–1914 expedition; contact YIVO archivist
4. **Hebrew/Yiddish primary texts** — Yiddish Book Center has 11,000+ digitized Yiddish books; search for *mayse* collections (folk tale books)
5. **Additional Gutenberg sources:**
   - Helena Frank, *Yiddish Tales* (Gutenberg #33707) — literary Yiddish stories (Peretz, Sholem Aleichem, etc.)
   - *Stories and Pictures* by I.L. Perez (Gutenberg #37242)
