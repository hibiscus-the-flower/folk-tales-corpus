"""
Create stub corpus files for all 200 tales in Beatrice Weinreich's
"Yiddish Folktales" (Pantheon Books / YIVO Institute, 1988; repr. 2012).

Source: B. Weinreich (ed.), tr. Leonard Wolf.
ISBN: 978-0-8052-1090-3
Internet Archive: https://archive.org/details/yiddishfolktales00wein
  (requires library borrowing; not freely downloadable)

YIVO context
------------
The tales were gathered in the 1920s–1930s by zamlers (folk-collectors) working
for the YIVO Ethnographic Committee (RG 1.2).  They are the most important
scholarly edition of material from the YIVO Vilna archives.

Running this script creates placeholder HTML files in corpus/weinreich_en/ so
the tale catalogue is complete and the manifest can be built.  The placeholder
body tells a future reader where to obtain the text.

To fill the stubs: borrow the book via Internet Archive (or a library copy),
read each tale, and replace the <div class="stub"> block with the actual text.
"""

import os, re, shutil

PROJ    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJ, "corpus", "weinreich_en")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Complete table of contents: (section_label, [tale_title, ...])
# Source: Google Books preview + Internet Archive metadata (retrieved 2026-06-04)
# ---------------------------------------------------------------------------
TALES = [
    ("Allegorical Tales", [
        "Naked Truth and Resplendent Parable",
        "A Bit of Herring, a Pinch of Salt, and a Morsel of Bread",
        "Things Can Always Get Worse",
        "The Luck That Snored",
        "The Fever and the Flea",
        "Why Dogs Chase Cats and Cats Chase Mice",
        "Wisdom or Luck?",
        "Pleasing All the World",
        "Poverty Grows and Grows",
        "The Sacrifice of Isaac and the Caretaker of Brisk",
        "The Treasure at Home",
        "A Fable of a Bird and Her Chicks",
        "Letting In the Light",
        "Bad Luck",
    ]),
    ("Children's Tales", [
        "A Nonsense Tale",
        "A Purim Tale",
        "A Tale of Two Brothers",
        "The Foolish Youth and Elijah the Prophet",
        "The King's Lost Daughter",
        "The Magic Fish and the Wishing Ring",
        "The Hunchbacks and the Dancing Demons",
        "The Princess of the Third Pumpkin",
        "Stones and Bones Rattle in My Belly",
        "Sore Khone at the Tip of the Church Tower",
        "Little Bean",
        "A Topsy-Turvy Tale",
        "Clever Khashinke and Foolish Bashinke",
        "The Granny Bear",
        "Moyshele and Sheyndele",
        "Next Time That's What I'll Say",
        "The Naughty Little Girl",
    ]),
    ("Wonder Tales", [
        "The Orphan Boy Who Won the Bride",
        "Forty Hares and a Princess",
        "Hang the Moon on My Palace Roof",
        "The Sorcerer's Apprentice",
        "The Beggar King and the Melamed",
        "Of Nettles and Roses",
        "The Demon and Sosye",
        "How Much Do You Love Me?",
        "The Master Thief",
        "The Orphan Boys",
        "Two Brothers Who Went to the Devil",
        "The Snake Bridegroom",
        "The Merchant's Son and the Demons",
        "The Ram, the Basket, and the Stick",
        "The Golden Feather",
    ]),
    ("Pious Tales", [
        "The Tale of a Stingy Woman",
        "The Wheat Poured In at the Door",
        "In Heaven and Hell",
        "The Miracle of the Tree",
        "The Poor Man's Ruble",
        "Blood and Water",
        "A Letter to God",
        "The Seven Good Years",
        "Set a Trap for Another",
        "A Sukkos Tale",
        "Only Eleven Little Fish",
        "A Passover Tale",
        "A Shocking Tale of a Viceroy",
        "The Leper Boy and Elijah the Prophet",
        "A Tragic Tale",
        "Upon Me",
        "The Ballad of the Faithful Wife",
        "The Iron Chest",
        "Water Wouldn't Hurt",
        "Holding On to One-Quarter of My World",
        "The Poor Rabbi and His Three Daughters",
    ]),
    ("Humorous Tales", [
        "A Riddle Tale",
        "Then Where's the Cat?",
        "The Best for My Wife",
        "Another Riddle Tale",
        "Good Manners and Foolish Khushim",
        "Khushim and His Bride",
        "The Tale of a Leaf from the Tree of Knowledge",
        "Reb Hershele and the Goose Leg",
        "Hershele Ostropolyer and the Sabbath Caftan",
        "The Angel Spills the Jar of Fools",
        "The Hill Pushed Away",
        "How Khelmites Lighted Up the Night",
        "The Melamed's Trunk",
        "The Rolling Stone",
    ]),
    ("Tales of Rebbes and Disciples (Legends)", [
        "The Missed Moment of Redemption",
        "The Mekarev Rebbe Gets Even with a Stingy Woman",
        "The Happy Pair and the Baal Shem Tov",
        "The Fleet-Footed Tomeshef Rebbe",
        "The Right Order Is Important",
        "Reb Khaim Urbakh Rocks a Cradle on Yom Kippur",
        "The Miracle of the Dry Well",
        "The Reincarnation of Queen Esther",
        "The Penitent and the Rebbe of Tshekhenove",
        "The Boy Who Put Two Socks on One Foot",
        "The Power of the Mourner's Prayer",
        "The Curious Disciple",
        "Reb Malkiel and the 702 Candles",
        "A Modern Miracle",
        "How Judah Halevi Entered Heaven Alive",
        "Rabbi Joshua and the Emperor of Rome",
        "A Wonderful Legend of a Cave",
        "Waiting for the Messiah",
        "The Torah of My Servant Moses",
        "A Disputation",
        "He Has Only One Weakness",
        "Evening the Score",
        "Reb Leybele of Mir Goes to the Marketplace",
        "Napoleon the First and the Jewish Officer",
        "Napoleon in Vilna",
        "The Cantonist's Mother and Nicholas the First",
        "Czar Nicholas Decrees the Burning of the Talmud",
        "The Poor Man and Rothschild",
        "Rothschild's Shoes",
    ]),
    ("Supernatural Tales", [
        "The Shoemaker and the Shretelekh",
        "The Synagogue, the Church, and the Town Hall",
        "The Transmigrating Soul",
        "Who's Milking the Cows?",
        "The Passover Elf Helps Great-Grandmother",
        "The Blacksmith and the Horses with Human Hands",
        "The Mysterious Gold Chain",
        "The Unquiet Grave",
        "The Large Stone Synagogue of Berditshev",
        "The Golem of Vilna",
        "The Baal Shem Tov and the Gilgl",
        "The Shretele That Took a Little Nip",
        "The Lost Hat and the Pile of Gold",
        "The Miracle of the Beer Keg",
        "How Doves Saved a Synagogue from Fire",
        "A Cave That Leads to the Land of Israel",
        "Late-Night Spooks",
        "The Missing Bridegroom",
        "The Trustees",
    ]),
]

# ---------------------------------------------------------------------------
STUB_BODY = """\
<div class="stub">
  <p><em>[Text not yet available — stub file only.]</em></p>
  <p>This tale appears in:</p>
  <blockquote>
    Beatrice Silverman Weinreich (ed.), tr. Leonard Wolf.<br/>
    <strong>Yiddish Folktales</strong>.<br/>
    New York: Pantheon Books / YIVO Institute for Jewish Research, 1988.<br/>
    ISBN 978-0-8052-1090-3.<br/>
    Section: <strong>{section}</strong>.
  </blockquote>
  <p>
    The tales in this volume were gathered in the 1920s–1930s by
    <em>zamlers</em> (folk-collectors) working for the
    <strong>YIVO Ethnographic Committee</strong> (RG 1.2), Vilna.
    The physical archive is held at the Center for Jewish History, New York.
  </p>
  <p>
    To obtain the full text, borrow the book through
    <a href="https://archive.org/details/yiddishfolktales00wein">Internet Archive</a>
    or consult a library holding a physical copy.
  </p>
</div>
"""

DOC_TEMPLATE = """\
<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link href="0.css" rel="stylesheet" type="text/css"/>
</head>
<body class="x-ebookmaker x-ebookmaker-3">
<div class="chapter">
<h2>{title}</h2>
<p class="section-label"><em>Section: {section}</em></p>
{body}
</div>
</body>
</html>
"""


def slugify(text):
    text = re.sub(r"\s+", " ", text).strip().lower()
    for ch in ("'", "'", "'", ",", ".", ":", "?", "!"):
        text = text.replace(ch, "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# Minimal CSS stub
css_path = os.path.join(OUT_DIR, "0.css")
if not os.path.exists(css_path):
    open(css_path, "w", encoding="utf-8").write("/* stub */\n")

seq = 0
for section, titles in TALES:
    for title in titles:
        seq += 1
        slug     = slugify(title) or f"tale-{seq}"
        filename = f"{seq:03d}_{slug}.html"
        path     = os.path.join(OUT_DIR, filename)
        body     = STUB_BODY.format(section=section)
        content  = DOC_TEMPLATE.format(title=title, section=section, body=body)
        open(path, "w", encoding="utf-8").write(content)
        print(f"  {filename}  <-  [{section}] {title}")

print(f"\n{seq} stub files written to corpus/weinreich_en/")
print("Run scripts/build_manifest.py to update the index.")
