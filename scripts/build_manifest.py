import os, re, csv, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (subdir under corpus/, label, author, language, source short-name)
COLLECTIONS = [
    ("andersen_en",     "Hans Christian Andersen", "en", "Gutenberg #27200 (Paull tr.)"),
    ("andersen_ru",     "Hans Christian Andersen", "ru", "Russian Wikisource (Hansen tr.)"),
    ("grimm_en",        "Brothers Grimm",          "en", "Gutenberg #5314 (Hunt tr.)"),
    # Japanese folk-tale collections
    ("japanese_ozaki_en", "Yei Theodora Ozaki",    "en", "Gutenberg #4018 (Japanese Fairy Tales, 1908)"),
    ("japanese_james_en", "Grace James",           "en", "Gutenberg #35853 (Green Willow, 1910)"),
    # Persian folk-tale collections
    ("persian_lorimer_en", "D. L. R. & E. O. Lorimer", "en", "archive.org cu31924029903881 OCR (Persian Tales, 1919)"),
    ("persian_bakhtyar_en", "trans. W. A. Clouston",   "en", "Gutenberg #60316 (The Bakhtyar Nama, 1883)"),
    ("persian_catmouse_en", "Anon. (Altemus Series)",  "en", "Gutenberg #24473 (The Cat and the Mouse)"),
    ("persian_levy_en",     "Reuben Levy",             "en", "archive.org threedervischeso00levyuoft OCR (Three Dervishes, 1923)"),
    # Yiddish / Jewish folk-tale collections
    ("landa_en",            "Gertrude Landa",      "en", "Gutenberg #26711 (Landa)"),
    ("friedlander_en",      "Gerald Friedlander",  "en", "Gutenberg #72880 (Friedlander)"),
    ("jewish_fairy_book_en","Gerald Friedlander",  "en", "Wikisource (Jewish Fairy Book, 1920)"),
    ("hebrew_tales_en",     "Hyman Hurwitz",       "en", "Wikisource (Hebrew Tales, 1826)"),
    ("ginzberg_legends_en", "Louis Ginzberg",      "en", "Gutenberg #1493/1494/2881/2882 (Legends of the Jews)"),
    ("isaacs_en",           "Abram S. Isaacs",     "en", "archive.org OCR (Stories from the Rabbis, 1893)"),
    ("rapaport_en",         "Samuel Rapaport",     "en", "archive.org OCR (Tales and Maxims from the Midrash, 1907)"),
    ("weinreich_en",        "Various (YIVO zamlers)","en","Weinreich/YIVO 1988 (stub)"),

    ("indian_steel_en",     "Flora Annie Steel",   "en", "Gutenberg #6145 (Tales of the Punjab, 1894)"),
    ("indian_jacobs_en",    "Joseph Jacobs",       "en", "Gutenberg #7128 (Indian Fairy Tales, 1892)"),
    ("indian_day_en",       "Lal Behari Day",      "en", "Gutenberg #38488 (Folk-Tales of Bengal, 1883)"),
    ("indian_bompas_en",    "Cecil Henry Bompas",  "en", "Gutenberg #11938 (Folklore of the Santal Parganas, 1909)"),
    ("indian_frere_en",     "Mary Frere",          "en", "Gutenberg #36696 (Old Deccan Days, 1868)"),
    ("indian_kingscote_en", "G. Kingscote & S. M. Natesa Sastri", "en", "Gutenberg #37002 (Tales of the Sun, 1890)"),
    ("indian_crooke_en",    "W. Crooke & W. H. D. Rouse", "en", "Gutenberg #30635 (The Talking Thrush, 1899)"),
    ("indian_rouse_en",     "W. H. D. Rouse",      "en", "Gutenberg #36039 (The Giant Crab, 1897)"),
    ("indian_dracott_en",   "Alice Elizabeth Dracott", "en", "Gutenberg #58816 (Simla Village Tales, 1906)"),
    ("indian_campbell_en",  "A. Campbell",         "en", "Gutenberg #35060 (Santal Folk Tales, 1891)"),
    ("indian_kincaid_en",   "C. A. Kincaid",       "en", "Gutenberg #76982 (Folk Tales of Sind and Guzarat, 1925)"),
    ("indian_babbitt_jataka_en", "Ellen C. Babbitt", "en", "Gutenberg #62514 (Jataka Tales, 1912)"),
    ("indian_babbitt_more_en",   "Ellen C. Babbitt", "en", "Gutenberg #7518 (More Jataka Tales, 1922)"),
    ("indian_stokes_en",      "Maive Stokes",        "en", "Wikisource — Indian Fairy Tales (Stokes, 1879)"),
    ("indian_deccan_nursery_en", "C. A. Kincaid",    "en", "Gutenberg #11167 (Deccan Nursery Tales, 1914)"),
    ("indian_hindu_sanskrit_en", "S. M. Mitra & Mrs. Arthur Bell", "en", "Gutenberg #11310 (Hindu Tales from the Sanskrit, 1919)"),
    ("indian_magic_bed_en",   "Hartwell James",      "en", "Gutenberg #37708 (The Magic Bed: East Indian Fairy-Tales, 1906)"),
    ("indian_vikram_en",      "Richard F. Burton",   "en", "Gutenberg #2400 (Vikram and the Vampire, 1870)"),
    ("indian_goblins_en",     "Arthur W. Ryder",     "en", "Gutenberg #2290 (Twenty-Two Goblins, 1917)"),
    ("indian_tibetan_en",     "F. A. von Schiefner & W. R. S. Ralston", "en", "Gutenberg #66870 (Tibetan Tales, Derived from Indian Sources, 1882)"),

    ("ceylon_parker_v1_en",   "Henry Parker",        "en", "Gutenberg #56614 (Village Folk-Tales of Ceylon, Vol. 1, 1910)"),
    ("ceylon_parker_v2_en",   "Henry Parker",        "en", "Gutenberg #57399 (Village Folk-Tales of Ceylon, Vol. 2, 1914)"),
    ("ceylon_parker_v3_en",   "Henry Parker",        "en", "Gutenberg #58889 (Village Folk-Tales of Ceylon, Vol. 3, 1914)"),

    ("burmese_pagoda_en",     "Told on the Pagoda (Mrs. A. M. B. Irwin)", "en", "Gutenberg #36171 (Told on the Pagoda: Tales of Burmah, 1895)"),
    ("shan_griggs_en",        "William C. Griggs",   "en", "Gutenberg #32375 (Shan Folk Lore Stories, 1902)"),
    ("tibetan_folktales_en",  "A. L. Shelton",       "en", "Gutenberg #75000 (Folk Tales from Tibet, 1925)"),

    # Russian and Slavic folk-tale collections
    ("russian_ralston_en",    "W. R. S. Ralston",         "en", "Gutenberg #22373 (Russian Fairy Tales, 1873)"),
    ("russian_polevoi_en",    "R. Nisbet Bain (trans.)",  "en", "Gutenberg #34705 (Skazki of Polevoi, 1894)"),
    ("cossack_bain_en",       "R. Nisbet Bain",           "en", "Gutenberg #29672 (Cossack Fairy Tales, 1894)"),
    ("slavic_sixty_en",       "R. Nisbet Bain (trans.)",  "en", "Gutenberg #48761 (Sixty Slavonic Folk-Tales, 1894)"),
    ("russian_story_book_en", "Richard Wilson",           "en", "Gutenberg #48605 (The Russian Story Book, 1916)"),

    # Norwegian folk-tale collections
    ("norwegian_dasent_en", "Asbjørnsen & Moe (trans. Dasent)", "en", "Gutenberg #8933 (Popular Tales from the Norse, 1859)"),
    ("norwegian_fjeld_en",  "Asbjørnsen (trans. Dasent)",       "en", "Gutenberg #36385 (Tales from the Fjeld, 1874)"),

    # Portuguese folk-tale collections
    ("portuguese_eells_azores_en", "Elsie Spicer Eells", "en", "Gutenberg #34431 (Islands of Magic: Azores, 1922)"),

    # Icelandic, Welsh, Finnish collections
    ("icelandic_hall_en",  "Mrs. Angus W. Hall",            "en", "Gutenberg #67085 (Icelandic Fairy Tales, 1897)"),
    ("welsh_guest_en",     "Lady Charlotte Guest (trans.)",  "en", "Gutenberg #5160 (The Mabinogion, 1849)"),
    ("finnish_eivind_en",  "R. Eivind (Kalevala adaptation)","en", "Gutenberg #24948 (Finnish Legends for English Children, c1893)"),

        # Swedish folk-tale collections
    ("swedish_hofberg_en",  "Herman Hofberg (trans. W. H. Myers)", "en", "Gutenberg #73093 (Swedish Fairy Tales, 1893)"),
    ("swedish_stroebe_en",  "Clara Stroebe (trans. Frederick Herman Martens)", "en", "Gutenberg #37193 (The Swedish Fairy Book, 1921)"),

    # English folk-tale collections
    ("english_jacobs_en",      "Joseph Jacobs", "en", "Gutenberg #7439 (English Fairy Tales, 1890)"),
    ("english_jacobs_more_en", "Joseph Jacobs", "en", "Gutenberg #14241 (More English Fairy Tales, 1894)"),

    # Scottish folk-tale collections
    ("scottish_grierson_en",  "Elizabeth W. Grierson", "en", "Gutenberg #37532 (The Scottish Fairy Book, 1910)"),
    ("scottish_campbell_en",  "John Gregorson Campbell", "en", "Gutenberg #67609 (Clan Traditions Western Highlands, 1895)"),

    # Dutch/Flemish/Belgian folk-tale collections
    ("dutch_griffis_en",   "William Elliot Griffis",          "en", "Gutenberg #7871 (Dutch Fairy Tales, 1918)"),
    ("belgian_griffis_en", "William Elliot Griffis",          "en", "Gutenberg #67256 (Belgian Fairy Tales, 1919)"),
    ("flemish_coster_en",  "Charles de Coster (trans. Taylor)","en", "Gutenberg #37668 (Flemish Legends, trans. 1920)"),

    # Irish folk-tale collections
    ("irish_yeats_folk_en",    "W. B. Yeats (ed.)",           "en", "Gutenberg #33887 (Fairy & Folk Tales of Irish Peasantry, 1888)"),
    ("irish_jacobs_celtic_en", "Joseph Jacobs",               "en", "Gutenberg #35862 (Celtic Folk and Fairy Tales, 1892)"),
    ("irish_croker_en",        "T. Crofton Croker",           "en", "Gutenberg #39752 (Fairy Legends of South of Ireland, 1825)"),
    ("irish_jacobs_more_en",   "Joseph Jacobs",               "en", "Gutenberg #34453 (More Celtic Fairy Tales, 1894)"),
    ("irish_larminie_en",      "William Larminie",            "en", "Gutenberg #57858 (West Irish Folk-Tales, 1893)"),

    # Basque folk-tale collections
    ("basque_webster_en", "Wentworth Webster", "en", "Gutenberg #34902 (Basque Legends, 1877)"),

    # Spanish folk-tale collections
    ("spanish_munoz_en",  "José Muñoz Escámez",          "en", "Gutenberg #43212 (Fairy Tales from Spain, 1913)"),
    ("spanish_eells_en",  "Charles Sellers (trans.)",     "en", "Gutenberg #31481 (Tales from Nuts and Grapes, 1888)"),
    ("spanish_busk_en",   "R. H. Busk",                   "en", "Gutenberg #45859 (Patrañas, 1870)"),

    # Italian folk-tale and fairy-tale collections
    ("italian_crane_en",       "Thomas Frederick Crane",    "en", "Gutenberg #23634 (Italian Popular Tales, 1885)"),
    ("italian_basile_en",      "Giambattista Basile",       "en", "Gutenberg #2198 (Stories from the Pentamerone, orig. 1634)"),
    ("italian_busk_en",        "Rachel Harriette Busk",     "en", "Gutenberg #48771 (Roman Legends, 1877)"),
    ("italian_straparola_v1_en","Giovanni F. Straparola (trans. Waters)", "en", "Gutenberg #75257 (Nights of Straparola Vol. 1, 1894)"),

    # French folk-tale and fairy-tale collections
    ("french_perrault_en",   "Charles Perrault",    "en", "Gutenberg #29021 (Fairy Tales of Perrault, Harrap 1922)"),
    ("french_daulnoy_en",    "Madame d'Aulnoy (trans. Macdonell & Lee)", "en", "archive.org fairytalesmadam00dgoog (1892)"),
    ("french_planche_en",    "J. R. Planché (trans.)", "en", "Gutenberg #52719 (Four and Twenty Fairy Tales, 1858)"),
    ("french_laboulaye_en",  "Édouard Laboulaye (trans. Booth)", "en", "Gutenberg #26386 (Laboulaye's Fairy Book, 1866)"),
    ("french_segur_en",      "Comtesse de Ségur",   "en", "Gutenberg #30129 (Old French Fairy Tales, c1920)"),
    ("french_cosquin_fr",    "Emmanuel Cosquin",    "fr", "Gutenberg #57892 (Contes populaires de Lorraine, 1886)"),
]

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
# Grimm titles start with the KHM number ("50 Briar-Rose") or "Legend N ...".
KHM_RE = re.compile(r"^\s*(?:(Legend)\s+)?(\d+)\s+")


def title_of(path):
    m = TITLE_RE.search(open(path, encoding="utf-8").read())
    return html.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""


rows = []
for label, author, lang, source in COLLECTIONS:
    d = os.path.join(ROOT, "corpus", label)
    for fn in sorted(f for f in os.listdir(d) if f.endswith(".html")):
        seq = fn.split("_", 1)[0]
        title = title_of(os.path.join(d, fn))
        khm = ""
        if label == "grimm_en":
            m = KHM_RE.match(title)
            if m:
                khm = ("L" if m.group(1) else "") + m.group(2)
                title = title[m.end():].strip()
        rows.append({
            "tale_id": f"{label}:{seq}",
            "author": author,
            "language": lang,
            "collection": label,
            "seq": seq,
            "khm": khm,
            "title": title,
            "filename": f"corpus/{label}/{fn}",
            "source": source,
        })

out = os.path.join(ROOT, "index", "manifest.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"{len(rows)} tales written to {out}")
for label, *_ in COLLECTIONS:
    print(f"  {label}: {sum(1 for r in rows if r['collection']==label)}")
