---
description: Harvest the next queued culture into the corpus locally, then push to main
---

Harvest **one** culture into this public-domain folk/fairy-tale corpus, running
locally (this machine has full web egress, unlike the remote routine sandbox which
is blocked — see `HARVEST_QUEUE.md` history). Work end-to-end and push, then STOP
so the user can review and decide whether to run the next one.

**STEP 0 — Quick egress sanity check.** Run:
```bash
python3 .claude/skills/folktale-harvester/scripts/preflight.py
```
If a CRITICAL source (archive.org or Wikisource) is BLOCKED even here, stop and
report it — something is wrong with local connectivity; do not attempt a harvest.
If both are OK, continue. (Locally this normally passes trivially.)

**STEP 1 — Orient & choose.** Read `HARVEST_QUEUE.md`. The checkboxes are the
source of truth: `[ ]` = not started, `[~]` = started but more PD editions may
remain, `[x]` = well-covered. Pick the next `[ ]` culture from the top of the
queue working downward (within a region, left-to-right / top-to-bottom). Prefer
unstarted cultures to maximize breadth. Announce which culture you picked and why.

**STEP 2 — Harvest.** Invoke the `folktale-harvester` skill (via the Skill tool)
for that culture and run it END TO END exactly as its SKILL.md describes:
catalogue from multiple aggregators, do the second sweep, write
`sources/<culture>_survey.md` with HARVEST/CATALOGUE-ONLY/SKIP verdicts, harvest
every cleared edition into `corpus/<culture>_<author>_<lang>/`, dedup, register
collections in `scripts/build_manifest.py`, and run it. Honor the skill's
token-budget discipline — never Read raw source dumps; trust the scripts' summaries.

**HARD RULE — public domain only.** Follow
`.claude/skills/folktale-harvester/references/copyright.md` strictly. An
edition/translation published before 1929 (US) or on Project Gutenberg is
harvestable; 'Borrow'/waitlist on archive.org or any modern translation is
catalogue-only. Date the edition/translation, not the underlying folklore. When
unsure, catalogue only and record the doubt. You are the only gate.

**COLONIAL-SOURCE VIGILANCE.** Apply to every culture, with extra care for
Indigenous American, African, Aboriginal Australian, Romani, and other traditions
collected under colonial conditions. If the source author/editor is known for a
problematic colonial role or framing that may have sanitized or de-authenticated
the tales, search for an alternative PD edition closer to the tradition itself (a
native/Indigenous collector, a community-vetted text, a less-mediated ethnographic
primary source) and prefer it. If none exists you may harvest the available one
BUT must flag the provenance concern in `sources/<culture>_survey.md`. Respect
sacred or restricted material. Never let "more tales" override authenticity or the
PD rule.

**STEP 3 — Mark it off.** Edit this culture's checkbox in `HARVEST_QUEUE.md`
(`[ ]`→`[x]` if you exhausted the cleared PD editions, or `[~]` if PD editions
remain for a future pass) and append a one-line outcome, e.g.
`→ french_*: 3 collections, 88 tales; 2 editions catalogue-only (in-copyright translations)`.

**STEP 4 — Commit & push.** This repo's `origin` is the GitHub mirror over SSH —
pushing from here works (the remote routine's write-access problems do not apply
locally). Run:
```bash
git add -A
git commit -m "Harvest <Culture>: <N> tales across <M> collections"
git pull --rebase origin main && git push origin main
```
If push is rejected, rebase onto origin/main and retry. `.cache/` is gitignored —
never force-add it.

**STEP 5 — Report & STOP.** Summarize: culture harvested, collections added with
tale counts, total new tales, anything catalogue-only and why, any colonial-source
substitution or provenance flag, and leads left for a future pass. Then STOP — do
NOT roll on to the next culture. The user runs `/harvest-next` again (or
`/loop /harvest-next`) when ready. A shortfall (e.g. key collections still in
copyright) is a finding to report, not a failure.
