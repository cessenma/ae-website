#!/usr/bin/env python3
"""Set every page's ledger date from git history: the day its present content first appeared.

For each page, take the content signature of the file as it is now (seo_build.content_signature:
words, alt text, link targets, pictures, practice data — no markup), then walk the file's
commits from newest to oldest for as long as the signature stays the same. The date of the
oldest matching commit is the page's "last updated" date. If even the newest commit differs,
the page was changed in the working tree and gets today's date.

Why: the ledger used to hash the body HTML, so a class rename, PNG to WebP or an attribute
edit stamped the build date on pages nobody had edited (a third of September's dates were a
day or more late, and 24 URLs sat on one commerce batch date).

    python3 tools/backfill_lastmod.py --dry-run           # print the changes, write nothing
    python3 tools/backfill_lastmod.py                     # rewrite data/lastmod.json
    python3 tools/backfill_lastmod.py --cosmetic a,b      # these pages' uncommitted edits are
                                                          #   wording only: date them from history

Run tools/seo_build.py afterwards (it prints the dates into the pages and the sitemap).
"""
import os, sys, json, subprocess, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_build as S

def git(*args):
    return subprocess.run(["git", "-C", S.SITE, *args], capture_output=True, text=True, errors="replace").stdout

def commits(rel):
    """[(hash, YYYY-MM-DD)] newest first, only commits that touched the file."""
    return [l.split() for l in git("log", "--format=%H %cs", "--", rel).splitlines() if l.strip()]

def main():
    dry = "--dry-run" in sys.argv
    cosmetic = set()
    if "--cosmetic" in sys.argv:
        cosmetic = {c.strip().strip("/") for c in sys.argv[sys.argv.index("--cosmetic") + 1].split(",") if c.strip()}
    ledger = S.load_ledger()
    today = datetime.date.today().isoformat()
    moved, rows = 0, []
    for key in sorted(ledger):
        if os.path.splitext(key)[1] == ".pdf":
            continue
        rel = "index.html" if key == "index" else ("404.html" if key == "404" else key + "/index.html")
        path = os.path.join(S.SITE, rel)
        if not os.path.exists(path):
            continue
        now = S.authored_hash(open(path, encoding="utf-8").read())
        hist = commits(rel)
        ref, date, walked = now, today, 0
        if key in cosmetic and hist:           # judge by the last committed version instead
            ref = S.authored_hash(git("show", f"{hist[0][0]}:{rel}"))
        for h, d in hist:
            old = git("show", f"{h}:{rel}")
            walked += 1
            if not old or S.authored_hash(old) != ref:
                break
            date = d
        was = ledger[key].get("date")
        if was != date or ledger[key].get("hash") != now:
            moved += was != date
            rows.append((key, was, date, walked))
        ledger[key] = {"hash": now, "date": date}
    for key, was, date, walked in rows:
        if was != date:
            print(f"  {key:<50} {was} -> {date}   ({walked} commits read)")
    print(f"{moved} dates corrected of {len(ledger)} entries" + (" (dry run, nothing written)" if dry else ""))
    if not dry:
        S.save_ledger(ledger)

if __name__ == "__main__":
    main()
