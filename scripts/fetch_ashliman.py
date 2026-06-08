import os, re, csv, json, time, html as htmlmod, subprocess

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(PROJ, ".cache", "ashliman")
PAGES_JSON = os.path.join(PROJ, ".cache", "ashliman_pages.json")
OUT = os.path.join(PROJ, "index", "compendium_ashliman.csv")
ROOT = "https://www.pitt.edu/~dash/"
UA = "fairy-tales-research/1.0 (daniel.hiterer@gmail.com)"

# Headings that are navigation/apparatus, not tales.
STOP = re.compile(r"^(contents|table of contents|links?( to related sites)?|"
                  r"related links|notes?|bibliography|sources?|return to|"
                  r"d\.?\s*l\.?\s*ashliman|revised|other links|see also|"
                  r"folklore and mythology|legends|external links)\b", re.I)


def fetch(page):
    fp = os.path.join(CACHE, page)
    if os.path.exists(fp):
        return open(fp, encoding="utf-8", errors="replace").read()
    raw = subprocess.run(["curl", "-sL", "-A", UA, ROOT + page],
                         capture_output=True).stdout
    out = raw.decode("utf-8", "replace")
    open(fp, "w", encoding="utf-8").write(out)
    time.sleep(0.3)
    return out


def text_of(raw):
    return htmlmod.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw))).strip()


def parse_origin(s):
    """'Norway (Asbjornsen and Moe)' -> ('Norway', 'Asbjornsen and Moe')."""
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", s)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return s, ""


NAV = {"ashliman.html", "folktexts.html", "folktexts2.html", "folklinks.html",
       "index.html"}
LINK_RE = re.compile(r'href="([a-z0-9_]+\.html)(?:#[^"]*)?"', re.I)
CAP = 1500
os.makedirs(CACHE, exist_ok=True)


def crawl():
    """BFS over internal dash pages starting from the two alpha indexes."""
    seen = set()
    queue = ["folktexts.html", "folktexts2.html"]
    order = []
    while queue and len(seen) < CAP:
        page = queue.pop(0)
        if page in seen:
            continue
        seen.add(page)
        h = fetch(page)
        if page not in NAV:
            order.append(page)
        for href in LINK_RE.findall(h):
            href = href.lower()
            if href not in seen:
                queue.append(href)
    return order


pages = crawl()
json.dump(sorted(pages), open(PAGES_JSON, "w"))
print(f"crawled {len(pages)} topic pages")

rows = []
seen = set()
for page in pages:
    h = fetch(page)
    body = re.sub(r"<(script|style)\b.*?</\1>", "", h, flags=re.DOTALL | re.I)
    atu = ""
    m = re.match(r"type0*(\d+[a-z]?)", page, re.I)
    if m:
        atu = m.group(1).upper()
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.DOTALL | re.I)
    topic = text_of(h1.group(1)) if h1 else page.replace(".html", "")

    # Ordered list of (level, text) for h2..h4.
    heads = [(int(l), text_of(t)) for l, t in
             re.findall(r"<h([2-4])[^>]*>(.*?)</h\1>", body, re.DOTALL | re.I)]
    heads = [(l, t) for l, t in heads if t and not STOP.match(t)]

    i = 0
    while i < len(heads):
        lvl, title = heads[i]
        origin = ""
        # An immediately-following deeper heading is the origin line.
        if i + 1 < len(heads) and heads[i + 1][0] > lvl:
            origin = heads[i + 1][1]
            i += 2
        else:
            i += 1
        if origin:
            culture, author = parse_origin(origin)
        else:
            # No origin heading: the country may be parenthetical in the title.
            base, paren = parse_origin(title)
            if paren:
                title, culture, author = base, paren, ""
            else:
                culture, author = "", ""
        # Drop section markers / numbering used as headings ("22", "XV.", "54a").
        if re.match(r"^[\dIVXLCM]+\.?[a-z]?$", title):
            continue
        key = (page, title, origin)
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "atu": atu, "topic": topic, "title": title,
            "culture": culture, "author": author,
            "origin_raw": origin, "source_page": page,
        })

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["atu", "topic", "title", "culture",
                                      "author", "origin_raw", "source_page"])
    w.writeheader()
    w.writerows(rows)

print(f"{len(rows)} tale entries from {len(pages)} topic pages -> {OUT}")
print(f"  with ATU type:   {sum(1 for r in rows if r['atu'])}")
print(f"  with culture:    {sum(1 for r in rows if r['culture'])}")
print(f"  with author:     {sum(1 for r in rows if r['author'])}")
print(f"  distinct cultures: {len(set(r['culture'] for r in rows if r['culture']))}")
