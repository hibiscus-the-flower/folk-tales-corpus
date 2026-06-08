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
