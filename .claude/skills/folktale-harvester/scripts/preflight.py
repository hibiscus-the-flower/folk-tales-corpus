#!/usr/bin/env python3
"""
preflight — probe whether the harvester's data sources are reachable from THIS
environment, over the same curl/egress path the harvester scripts use.

Run this first (especially inside the remote routine sandbox, whose network
egress may be allowlisted). It tells you which aggregators are usable before a
harvest is attempted, so a block surfaces as a one-line verdict at the top of
the run instead of a deep failure.

    python3 .claude/skills/folktale-harvester/scripts/preflight.py

Always exits 0 — it is a diagnostic, not a gate. The harvester's own scripts
already degrade gracefully when a single source is blocked; this just makes the
situation visible (and decidable) up front.
"""
import subprocess
import sys

UA = "Mozilla/5.0 (compatible; folktale-harvester/1.0; +research, public-domain)"

# (label, url, critical?) — `critical` sources are load-bearing: if they are
# blocked the routine can catalogue but cannot harvest text, so a local run is
# the better path. Each URL is a light real endpoint on the host the scripts hit.
CHECKS = [
    ("archive.org (OCR full text)",
     "https://archive.org/metadata/grimmsfairytale00grimuoft", True),
    ("wikisource API (clean prose)",
     "https://en.wikisource.org/w/api.php?action=query&meta=siteinfo&format=json", True),
    ("gutendex.com (Gutenberg search)",
     "https://gutendex.com/books/?search=fairy", False),
    ("gutenberg.org (EPUB downloads)",
     "https://www.gutenberg.org/robots.txt", False),
    ("pitt.edu / Ashliman (catalogue only)",
     "https://www.pitt.edu/~dash/folktexts.html", False),
]


def probe(url):
    """Return (ok, detail) for a single host using the curl egress path."""
    proc = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "20", "-A", UA,
         "-o", "/dev/null", "-w", "%{http_code}", url],
        capture_output=True, text=True)
    http_code = (proc.stdout or "").strip() or "000"
    if proc.returncode == 0 and http_code.startswith(("2", "3")):
        return True, f"HTTP {http_code}"
    # curl exit 6/7/28 = DNS/connect/timeout (typical of an egress block);
    # 4xx/5xx = reached the host but it refused.
    err = (proc.stderr or "").strip().splitlines()
    reason = err[-1] if err else f"curl exit {proc.returncode}"
    return False, f"HTTP {http_code} / {reason}"


def main():
    print("=== Harvester connectivity preflight (curl/egress path) ===")
    crit_blocked = []
    for label, url, critical in CHECKS:
        ok, detail = probe(url)
        tag = "OK     " if ok else "BLOCKED"
        star = " *critical*" if critical else ""
        print(f"  [{tag}] {label}{star}  ({detail})")
        if critical and not ok:
            crit_blocked.append(label)

    print()
    if crit_blocked:
        print("VERDICT: a CRITICAL source is unreachable from this environment:")
        for c in crit_blocked:
            print(f"  - {c}")
        print("This environment can catalogue (via WebFetch/WebSearch, which route\n"
              "through Anthropic infra) but likely cannot HARVEST TEXT over curl.\n"
              "Recommendation: run the harvest LOCALLY (full egress) and push, rather\n"
              "than from this sandbox. Report this verdict and stop before a deep\n"
              "harvest that would fail on fetch.")
    else:
        print("VERDICT: all critical sources reachable — safe to harvest here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
