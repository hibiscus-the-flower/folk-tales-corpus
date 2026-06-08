import os, csv, json, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, "index")


def load_csv(name):
    with open(os.path.join(IDX, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


tales = load_csv("manifest.csv")
mapping = load_csv("mapping.csv")
types = {r["atu"]: r["short_title"] for r in load_csv("atu_types.csv")}
cats = load_csv("atu_categories.csv")

# Top-level division lookup: rows whose subgroup is empty are the 7 divisions.
divisions = [(int(r["range_start"]), int(r["range_end"]), r["division"])
             for r in cats if not r["subgroup"]]


def division_of(atu):
    n = int(re.match(r"\d+", atu).group())
    for lo, hi, name in divisions:
        if lo <= n <= hi:
            return name
    return ""


# Index mapping rules by field for quick lookup.
khm_map = {r["match_value"]: r for r in mapping if r["match_field"] == "khm"}
title_map = {r["match_value"]: r for r in mapping if r["match_field"] == "title"}

groups = defaultdict(list)
mapped = 0
for t in tales:
    rule = khm_map.get(t["khm"]) if t["khm"] else None
    if not rule:
        rule = title_map.get(t["title"])
    if rule:
        atu = rule["atu"]
        t["atu"] = atu
        t["atu_title"] = types.get(atu, "")
        t["atu_division"] = division_of(atu)
        t["atu_note"] = rule["note"]
        groups[atu].append(t["tale_id"])
        mapped += 1
    else:
        t["atu"] = t["atu_title"] = t["atu_division"] = t["atu_note"] = ""

# Cross-cultural / cross-language groups: same ATU type, >1 tale.
group_view = []
for atu, ids in sorted(groups.items(), key=lambda kv: (int(re.match(r"\d+", kv[0]).group()), kv[0])):
    members = [t for t in tales if t["tale_id"] in ids]
    group_view.append({
        "atu": atu,
        "short_title": types.get(atu, ""),
        "division": division_of(atu),
        "members": [{"tale_id": m["tale_id"], "author": m["author"],
                     "language": m["language"], "title": m["title"]} for m in members],
    })

out = {"tales": tales, "groups": group_view}
with open(os.path.join(IDX, "index.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# ---- coverage report ----
print(f"Tales:        {len(tales)}")
print(f"Mapped → ATU: {mapped}  ({100*mapped/len(tales):.0f}%)")
print(f"ATU types in play: {len(groups)}")
print(f"ATU seed table:    {len(types)} types, {len([c for c in cats if not c['subgroup']])} divisions")
print()
by_coll = defaultdict(lambda: [0, 0])
for t in tales:
    by_coll[t["collection"]][0] += 1
    if t["atu"]:
        by_coll[t["collection"]][1] += 1
for coll, (tot, m) in by_coll.items():
    print(f"  {coll:12} {m:>3}/{tot:<3} mapped")
print()
print("Cross-language / cross-author groups (same ATU type):")
for g in group_view:
    langs = sorted({m["language"] for m in g["members"]})
    auths = sorted({m["author"].split()[-1] for m in g["members"]})
    if len(g["members"]) > 1:
        print(f"  ATU {g['atu']:<5} {g['short_title'][:34]:<34} "
              f"{len(g['members'])} tales [{','.join(langs)}] {{{','.join(auths)}}}")
print(f"\nWrote {os.path.join('index','index.json')}")
