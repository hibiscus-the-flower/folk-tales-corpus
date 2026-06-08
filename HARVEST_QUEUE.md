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
- [~] French → french_perrault_en (10), french_daulnoy_en (24), french_planche_en (24), french_laboulaye_en (10), french_segur_en (5), french_cosquin_fr (30) = 103 tales; Sébillot (no djvu.txt) + Luzel (OCR heading gaps) + Bladé = high-priority future pass
- [~] Italian → italian_crane_en (99), italian_basile_en (32), italian_busk_en (93), italian_straparola_v1_en (25) = 249 tales; Pitrè/Comparetti/Imbriani (Italian-lang), Straparola Vol.2, Gonzenbach (German-lang) = future passes
- [~] Spanish → spanish_munoz_en (19), spanish_eells_en (21), spanish_busk_en (48) = 88 tales; Espinosa (Spanish-lang 280 tales), Fernán Caballero = future passes
- [x] Basque → basque_webster_en (28 tales; Webster 1877); more Basque folk collections exist in French/Spanish but no other English PD editions found
- [~] Portuguese → portuguese_eells_azores_en (34 tales; Eells Azores 1922); mainland Portuguese collections (Coelho, Athaide Oliveira) in Portuguese-lang = future pass
- [~] Dutch/Flemish → dutch_griffis_en (21), belgian_griffis_en (26), flemish_coster_en (78) = 125 tales; Wolff Nederlandsche sprookjes (Dutch-lang) = future pass
- [~] Norwegian → norwegian_dasent_en (74), norwegian_fjeld_en (39) = 113 tales; Grundtvig, Thorpe = future passes
- [~] Swedish → swedish_hofberg_en (83), swedish_stroebe_en (28) = 111 tales; Grundtvig overlap with Norwegian noted
- [x] Icelandic → icelandic_hall_en (18 tales; Hall 1897); Árnason Icelandic Legends (in Icelandic/Danish) = future pass
- [~] English → english_jacobs_en (43), english_jacobs_more_en (40) = 83 tales; Halliwell Nursery Rhymes, Steel English Tales = future passes
- [~] Scottish → scottish_grierson_en (27), scottish_campbell_en (38) = 65 tales; J. F. Campbell Popular Tales (4 vols) = future pass
- [~] Irish → irish_yeats_folk_en (58), irish_jacobs_celtic_en (26), irish_croker_en (37), irish_jacobs_more_en (20), irish_larminie_en (19) = 160 tales; Kennedy Legendary Fictions, Hyde Beside the Fire = future passes
- [x] Welsh (Mabinogion) → welsh_guest_en (12 tales; Guest trans. 1849); complete Mabinogion
- [ ] Cornish / Breton
- [ ] Greek (folk, modern — distinct from the myth layer below)
- [~] Finnish → finnish_eivind_en (38 Kalevala-legend chapters; Eivind c1893); actual folk tale collections in Finnish = future pass
- [ ] Sámi
- [~] German — Grimm present; more PD exists (Bechstein, Musäus, regional)
- [~] Danish — Andersen present (literary); folk collections (e.g. Grundtvig) untouched

## Eastern Europe & Slavic
- [~] Russian → russian_ralston_en (51), russian_polevoi_en (24), russian_story_book_en (15) = 90 tales; Afanasyev full collection (Russian-lang, 600+ tales) = major future pass
- [~] Ukrainian → cossack_bain_en (27 Cossack tales) partly covers; Ukrainian-specific collections = future pass
- [~] Polish → polish_biggs_en (7 tales; small Gliński selection); Gliński full 4 vols in Polish = future pass
- [x] Czech → czech_fillmore_en (15), czech_folk_tales_en (23) = 38 tales
- [ ] Slovak
- [x] Serbian → serbian_mijatovich_en (26 tales; Mijatovich 1874) — merged with Serbian Fairy Tales (near-dups removed)
- [x] Croatian → croatian_brlic_en (6 tales; Brlić-Mažuranić 1916 — Croatian author)
- [ ] Bulgarian
- [ ] Bosnian
- [ ] Slovenian
- [x] Hungarian → hungarian_magyars_en (106 tales; Jones/Various 1889)
- [~] Romanian → romanian_kremnitz_en (19), romanian_bird_beast_en (130) = 149 tales; Ispirescu (Romanian-lang) = future pass
- [ ] Lithuanian
- [ ] Latvian
- [ ] Estonian
- [~] Romani (Roma) → romani_groome_en (135 tales; Groome 1899 — respected Romani scholar); no native-authored PD English collection found

## Caucasus
- [x] Armenian → armenian_seklemian_en (30 tales; Seklemian 1898)
- [x] Georgian → georgian_wardrop_en (39 tales; Wardrop trans. 1894)
- [ ] Nart sagas (Circassian, Ossetian, other Caucasian peoples)

## Middle East & North Africa
- [~] Arabian → arabian_nights_en (10 best-known tales, Wiggin/Smith 1909); Burton full 10 vols, Lane 3 vols = major future pass
- [~] Turkish → turkish_bain_en (21 tales; Kúnos/Bain 1901); Kúnos Turkish Fairy Tales (full 2 vols) = future pass
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
- [~] Chinese → chinese_wilhelm_en (74 tales; Wilhelm 1921); Werner Myths & Legends = catalogue-only; Giles Strange Stories = future pass
- [x] Korean → korean_folk_tales_en (54), korean_fairy_tales_en (27) = 81 tales
- [ ] Mongolian
- [x] Japanese (Ozaki, James) — revisit only for a major untouched PD edition

## Central Asia
- [ ] Kazakh
- [ ] Kyrgyz
- [ ] Uzbek
- [ ] Turkmen
- [ ] Tajik

## Southeast Asia
- [~] Filipino → philippine_folk_tales_en (62 tales; Bayliss et al. 1908); Fansler Filipino Popular Tales = future pass
- [ ] Indonesian / Malay
- [ ] Vietnamese
- [ ] Thai
- [ ] Lao
- [ ] Khmer (Cambodian)
- [x] Burmese & Shan (Pagoda, Griggs) — revisit only for a major untouched PD edition

## Sub-Saharan Africa
- [~] Akan/Anansi → west_african_barker_en (38 tales; Barker/Sinclair 1917); Anansi Jamaica Beckwith = future pass
- [~] Yoruba/Nigerian → nigerian_dayrell_en (47 tales; Dayrell 1910 — colonial admin, provenance flagged); Yoruba-specific collections = future pass
- [ ] Hausa
- [ ] Igbo
- [ ] Fulani
- [ ] Wolof
- [ ] Bambara
- [~] Zulu/Bushmen → south_african_honey_en (45 tales Honey 1910; South African Bushmen/San/Xhosa); Callaway Zulu = future pass
- [ ] Xhosa
- [ ] Swahili (East African)
- [ ] Kongo
- [ ] Ethiopian / Amharic
- [ ] Malagasy (Madagascar)

## The Americas — Indigenous
(Heightened colonial-source vigilance — see note. Prefer BAE/ethnographic primary
texts and, where they exist, Indigenous-authored or community-vetted collections.)
- [x] North America — Cherokee → cherokee_mooney_en (127 myths; Mooney BAE 1900)
- [x] North America — Iroquois → iroquois_cornplanter_en (26, Cornplanter elder), seneca_parker_en (90, Parker SENECA AUTHOR) = 116 tales
- [x] N. America Lakota/Sioux → zitkala_sa_legends_en (14, ZITKALA-SA LAKOTA AUTHOR), sioux_mclaughlin_en (39) = 53 tales
- [~] N. America Navajo/Apache → apache_goddard_en (13, White Mountain Apache BAE); Navajo BAE reports = future pass (not found on Gutenberg; BAE Annual Reports = future archive.org pass)
- [ ] North America — Pueblo
- [~] N. America Pacific Northwest → northwest_gordon_en (6); larger collections = future pass
- [~] North America — Inuit/Arctic → north_american_folklore_en (34, mixed tribes c1891); Eskimo Bayliss = future pass
- [~] Maya/Latin American → latin_american_myth_en (73, incl. Aztec/Maya/Inca/Caribbean; Alexander 1920); great_plains_judson_en (73 multi-tribe Plains tales)
- [ ] Nahuatl / Aztec
- [ ] Quechua
- [ ] Aymara
- [ ] Taíno / Caribbean
- [ ] Amazonian

## The Americas — Diaspora & Settler
- [~] African American (Brer Rabbit/Uncle Remus) → uncle_remus_songs_en (56), uncle_remus_nights_en (71) = 127 tales; COLONIAL FRAMING NOTE: Harris (white journalist) in African American dialect — tales are authentic African-origin trickster lore, framing is paternalistic; More Uncle Remus volumes = future pass
- [x] Caribbean Anansi → anansi_jamaica_en (283 stories; Beckwith 1924 Jamaica)
- [~] Latin American mestizo folklore → Brazilian Tales (Goldberg) too literary, OCR needed; Latin American Mythology (Alexander) = future pass

## Oceania
- [x] Hawaiian → hawaiian_kalakaua_en (23, INDIGENOUS AUTHOR Kalakaua 1888), hawaiian_folk_tales_en (28, Thrum 1907) = 51 tales
- [~] Māori → maori_dittmer_en (20 tales; Dittmer 1907 from Grey sources); Grey Polynesian Mythology (colonial but primary PD source) = future pass
- [ ] Samoan
- [ ] Tahitian
- [ ] Tongan
- [ ] Fijian
- [ ] broader Polynesian
- [ ] Melanesian
- [ ] Aboriginal Australian — heightened vigilance; respect any sacred/restricted material
- [ ] Papuan

## Classical & Ancient (myth / literary layer — tag separately)
- [x] Aesop → aesop_fables_en (83 fables; Townsend 1887)
- [x] Greek mythology → greek_baldwin_en (15), greek_roman_berens_en (119) = 134 tales
- [~] Roman mythology → partially covered in greek_roman_berens_en; dedicated Roman collection = future pass
- [~] Norse mythology → norse_guerber_en (281 entries; Guerber 1909); Prose Edda, Poetic Edda translations = future pass
- [x] Mesopotamian → babylonian_spence_en (222 myth entries; Spence 1916)
- [x] Egyptian ancient → egyptian_spence_en (186 myth entries; Spence 1915)
- [~] Vedic/Hindu → indian_myth_legend_en (27 narrative sections; Mackenzie 1913); dedicated tale collections (Kathasaritsagara etc.) = future pass
- [x] Celtic mythological cycles → celtic_squire_en (25 chapters; Squire 1905)

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
