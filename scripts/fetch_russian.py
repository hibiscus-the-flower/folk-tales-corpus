import subprocess, urllib.parse, json, re, os, time, html as htmlmod

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "tales_ru")
API = "https://ru.wikisource.org/w/api.php"
UA = "fairy-tales-research/1.0 (daniel.hiterer@gmail.com)"
SUFFIX = " (Андерсен; Ганзен)"

DOC = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<style>
body{{font-family:Georgia,serif;max-width:42em;margin:2em auto;line-height:1.5;padding:0 1em}}
h1{{text-align:center}}
.src{{color:#777;font-size:.85em;text-align:center;margin-bottom:2em}}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="src">Ганс Христиан Андерсен · перевод А. В. Ганзен · источник: Русская Викитека</p>
{body}
</body>
</html>
"""


def api(params, tries=4):
    params = dict(params, format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    for n in range(tries):
        out = subprocess.run(["curl", "-s", "-A", UA, url],
                             capture_output=True, text=True).stdout
        if out.strip():
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                pass
        time.sleep(1.5 * (n + 1))
    raise RuntimeError(f"failed: {params.get('page') or params.get('apprefix')}")


def parse_html(title):
    d = api({"action": "parse", "page": title, "prop": "text"})
    return d.get("parse", {}).get("text", "")


def subpages(title):
    d = api({"action": "query", "list": "allpages",
             "apprefix": title + "/", "apnamespace": "0", "aplimit": "50"})
    return [p["title"] for p in d.get("query", {}).get("allpages", [])]


def remove_balanced(s, open_pos, tag):
    """Remove the element (start tag at open_pos) and its balanced subtree."""
    depth = 0
    i = open_pos
    pat = re.compile(rf"<(/?){tag}\b", re.IGNORECASE)
    while True:
        m = pat.search(s, i)
        if not m:
            return s[:open_pos]
        if m.group(1):           # closing tag
            depth -= 1
            if depth == 0:
                close_end = s.find(">", m.end())
                close_end = len(s) if close_end == -1 else close_end + 1
                return s[:open_pos] + s[close_end:]
        else:                    # opening tag
            depth += 1
        i = m.end()


def clean(raw):
    s = raw
    s = re.sub(r"<!--.*?-->", "", s, flags=re.DOTALL)
    s = re.sub(r"<style\b.*?</style>", "", s, flags=re.DOTALL | re.IGNORECASE)
    # Strip every ws-noexport subtree (header nav, edition notes, footer).
    while True:
        m = re.search(r'class="[^"]*ws-noexport[^"]*"', s)
        if not m:
            break
        start = s.rfind("<", 0, m.start())
        tagm = re.match(r"<(\w+)", s[start:])
        s = remove_balanced(s, start, tagm.group(1))
    # Drop edit-section and the textquality marker leftovers.
    s = re.sub(r'<span[^>]*id="textquality"[^>]*>\s*</span>', "", s)
    return s.strip()


def slug(title):
    t = title.replace(SUFFIX, "").strip()
    t = t.replace("«", "").replace("»", "").replace("'", "")
    t = re.sub(r"[^\w\s-]", "", t, flags=re.UNICODE)
    t = re.sub(r"\s+", "-", t.strip())
    return t


titles = sorted(json.load(open(os.path.join(BASE, "_ru_titles.json"), encoding="utf-8")))

if os.path.isdir(OUT):
    import shutil
    shutil.rmtree(OUT)
os.makedirs(OUT)

seq = 0
problems = []
for title in titles:
    raw = parse_html(title)
    body = clean(raw)
    prose = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()
    if len(prose) < 800:                       # wrapper page -> assemble modern text
        subs = subpages(title)
        vt = [s for s in subs if s.endswith("(ВТ:Ё)")]
        if vt:
            body = clean(parse_html(vt[0]))
        else:
            # Multi-chapter tale: modern chapters are leaves like ".../12" or
            # ".../Глава 3" (the "/ДО" variants are the old orthography).
            chap_re = re.compile(re.escape(title) + r"/(?:Глава )?(\d+)$")
            chaps = sorted((int(chap_re.match(s).group(1)), s)
                           for s in subs if chap_re.match(s))
            body = "\n<hr/>\n".join(clean(parse_html(s)) for _, s in chaps)
        prose = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()
        if len(prose) < 300:
            problems.append(title)
            continue
    seq += 1
    name = title.replace(SUFFIX, "").strip()
    fn = f"{seq:03d}_{slug(title)}.html"
    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        f.write(DOC.format(title=htmlmod.escape(name), body=body))
    if seq % 25 == 0:
        print(f"  ...{seq} saved")
    time.sleep(0.25)

print(f"\n{seq} Russian tales written to {OUT}")
if problems:
    print("Skipped (no usable modern text):", len(problems))
    for p in problems:
        print("   ", p)
