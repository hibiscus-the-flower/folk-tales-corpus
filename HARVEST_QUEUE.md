# Harvest Queue

Shared, durable to-do list for the scheduled `folktale-harvester` routine.
Each run reads this file, picks the **next unstarted culture** (top-to-bottom,
within a region work left-to-right), runs the harvester end-to-end, then **checks
the box and commits this file** so the next run continues where this one stopped.

Legend: `[ ]` not started · `[~]` started, more PD editions likely remain ·
`[x]` well-covered (revisit only if a major untouched PD edition surfaces).

Rules of thumb:
- **Prefer `[ ]` cultures first** — maximize breadth across the list before going
  deeper on one tradition.
- A culture is "done for now" once you've harvested every cleared PD edition you
  can find for it (the harvester's floors are 150 catalogued / 100 harvested, but
  those are floors, not ceilings — keep going while the public domain gives).
- Record per-culture outcome inline (e.g. `→ french_*: 3 collections, 88 tales`).

## Already in the corpus (pre-existing, before scheduling)
German (Grimm), Danish (Andersen — literary), Japanese, Persian, Sinhalese/Ceylon
(Parker), Burmese & Shan, Tibetan, the large Indian cluster, and the Jewish/Yiddish
cluster (Ashkenazi + several Mizrahi). These are marked `[~]`/`[x]` below.

---

## Western Europe
- [ ] French
- [ ] Italian
- [ ] Spanish
- [ ] Basque
- [ ] Portuguese
- [ ] Dutch/Flemish
- [ ] Norwegian
- [ ] Swedish
- [ ] Icelandic
- [ ] English
- [ ] Scottish
- [ ] Irish
- [ ] Welsh (Mabinogion)
- [ ] Cornish / Breton
- [ ] Greek (folk, modern — distinct from the myth layer below)
- [ ] Finnish
- [ ] Sámi
- [~] German — Grimm present; more PD exists (Bechstein, Musäus, regional)
- [~] Danish — Andersen present (literary); folk collections (e.g. Grundtvig) untouched

## Eastern Europe & Slavic
- [ ] Russian
- [ ] Ukrainian
- [ ] Polish
- [ ] Czech
- [ ] Slovak
- [ ] Serbian
- [ ] Croatian
- [ ] Bulgarian
- [ ] Bosnian
- [ ] Slovenian
- [ ] Hungarian
- [ ] Romanian
- [ ] Lithuanian
- [ ] Latvian
- [ ] Estonian
- [ ] Romani (Roma) — be especially mindful of source framing (see colonial note)

## Caucasus
- [ ] Armenian
- [ ] Georgian
- [ ] Nart sagas (Circassian, Ossetian, other Caucasian peoples)

## Middle East & North Africa
- [ ] Arabian (the Nights tradition)
- [ ] Turkish
- [ ] Kurdish
- [ ] Berber / Amazigh — French-language collections likely; watch colonial framing
- [ ] Maghrebi Arabic — ditto
- [ ] Egyptian (folk; distinct from the ancient layer below)
- [~] Persian — several collections present; more PD may remain

## Jewish (plural tradition)
- [ ] Sephardic (Judeo-Spanish / Ladino)
- [ ] Mizrahi gaps (Iraqi/Babylonian, Yemenite, Syrian, Kurdish, Bukharan, Georgian, Mountain Jews)
- [ ] Beta Israel (Ethiopian)
- [ ] Aggadic / Midrashic legend layer (tag separately)
- [~] Ashkenazi — Yiddish cluster present; gaps may remain

## South Asia
- [ ] Punjabi
- [ ] Bengali
- [ ] Tamil & other Dravidian
- [ ] Kashmiri
- [ ] Nepali
- [ ] Hindi / Hindustani (beyond what the Indian cluster already covers)
- [~] Sanskrit / classical — Jataka present; Panchatantra/Kathasaritsagara may remain
- [x] Sinhalese (Parker v1–v3) · [x] Tibetan · [x] broad Indian cluster

## East Asia
- [ ] Chinese
- [ ] Korean
- [ ] Mongolian
- [x] Japanese (Ozaki, James) — revisit only for a major untouched PD edition

## Central Asia
- [ ] Kazakh
- [ ] Kyrgyz
- [ ] Uzbek
- [ ] Turkmen
- [ ] Tajik

## Southeast Asia
- [ ] Filipino
- [ ] Indonesian / Malay
- [ ] Vietnamese
- [ ] Thai
- [ ] Lao
- [ ] Khmer (Cambodian)
- [x] Burmese & Shan (Pagoda, Griggs) — revisit only for a major untouched PD edition

## Sub-Saharan Africa
- [ ] Akan / Anansi (West African)
- [ ] Yoruba
- [ ] Hausa
- [ ] Igbo
- [ ] Fulani
- [ ] Wolof
- [ ] Bambara
- [ ] Zulu
- [ ] Xhosa
- [ ] Swahili (East African)
- [ ] Kongo
- [ ] Ethiopian / Amharic
- [ ] Malagasy (Madagascar)

## The Americas — Indigenous
(Heightened colonial-source vigilance — see note. Prefer BAE/ethnographic primary
texts and, where they exist, Indigenous-authored or community-vetted collections.)
- [ ] North America — Cherokee
- [ ] North America — Iroquois
- [ ] North America — Lakota / Sioux
- [ ] North America — Navajo
- [ ] North America — Pueblo
- [ ] North America — Pacific Northwest
- [ ] North America — Inuit / Arctic
- [ ] Maya
- [ ] Nahuatl / Aztec
- [ ] Quechua
- [ ] Aymara
- [ ] Taíno / Caribbean
- [ ] Amazonian

## The Americas — Diaspora & Settler
- [ ] African American (Brer Rabbit / Uncle Remus) — see colonial/dialect note
- [ ] Caribbean Anansi
- [ ] Latin American mestizo folklore

## Oceania
- [ ] Hawaiian
- [ ] Māori
- [ ] Samoan
- [ ] Tahitian
- [ ] Tongan
- [ ] Fijian
- [ ] broader Polynesian
- [ ] Melanesian
- [ ] Aboriginal Australian — heightened vigilance; respect any sacred/restricted material
- [ ] Papuan

## Classical & Ancient (myth / literary layer — tag separately)
- [ ] Aesop
- [ ] Greek mythology
- [ ] Roman mythology
- [ ] Norse mythology (Eddas)
- [ ] Mesopotamian (Gilgamesh)
- [ ] Egyptian (ancient)
- [ ] Vedic / Hindu
- [ ] Celtic mythological cycles

---

## Colonial-source vigilance (applies to every run)
Some of these traditions were collected under colonial conditions, which can
de-authenticate or sanitize the tales. When the **source author/editor is known
for a problematic colonial role or framing**, search again for an alternative
public-domain edition closer to the tradition itself — a native collector, a
community-vetted text, or a less-mediated ethnographic primary source. If no
better PD source exists, harvest the available one **but flag the provenance
concern** in the survey (`sources/<culture>_survey.md`) so the choice is auditable.
Never let "more tales" override authenticity or the public-domain rule.
