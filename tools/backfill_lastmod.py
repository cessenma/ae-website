#!/usr/bin/env python3
"""Set every ledger date from git history: the day a page's present content first appeared.

For each page, take the content signature of the file as it is now (seo_build.content_signature:
words, link targets, picture and audio names, inline scripts — no markup, no alt text), then
walk the file's commits from newest to oldest for as long as the signature stays the same. The
date of the oldest matching commit is the page's "last updated" date. If even the newest commit
differs, the page was changed in the working tree and gets today's date. A PDF is dated by the
last commit that changed it (today if it has uncommitted changes).

Why: the ledger used to hash the body HTML, so a class rename, PNG to WebP or an attribute
edit stamped the build date on pages nobody had edited (a third of September's dates were a
day or more late, and 24 URLs sat on one commerce batch date).

Wording-only edits. Some edits change words without being a content update (a relabelled
line, one more "read next" link, a corrected button). They are recorded by day in
data/lastmod_cosmetic.json — {"2026-10-01": ["page-a", "page-b"]} — and for those pages every
change made on that day, committed or not, is skipped when the date is worked out. The file
is the record: a later plain run gives the same dates.

    python3 tools/backfill_lastmod.py --dry-run           # print the changes, write nothing
    python3 tools/backfill_lastmod.py                     # rewrite data/lastmod.json
    python3 tools/backfill_lastmod.py --cosmetic a,b      # add a,b to today's wording-only list,
                                                          #   then recompute

Run tools/seo_build.py afterwards (it prints the dates into the pages and the sitemap).
A full run parses every historical version of every page: allow a minute or two.
"""
import os, sys, json, subprocess, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_build as S

COSMETIC = os.path.join(S.SITE, "data", "lastmod_cosmetic.json")

def git(*args):
    return subprocess.run(["git", "-C", S.SITE, *args], capture_output=True, text=True, errors="replace").stdout

def commits(rel):
    """[(hash, YYYY-MM-DD)] newest first, only commits that touched the file."""
    return [l.split() for l in git("log", "--format=%H %cs", "--", rel).splitlines() if l.strip()]

def load_cosmetic():
    try:
        return {k: list(v) for k, v in json.load(open(COSMETIC, encoding="utf-8")).items() if not k.startswith("_")}
    except FileNotFoundError:
        return {}

def main():
    dry = "--dry-run" in sys.argv
    today = datetime.date.today().isoformat()
    cosmetic = load_cosmetic()
    if "--cosmetic" in sys.argv:
        add = [c.strip().strip("/") for c in sys.argv[sys.argv.index("--cosmetic") + 1].split(",") if c.strip()]
        cosmetic[today] = sorted(set(cosmetic.get(today, [])) | set(add))
        if not dry:
            json.dump(dict({"_note": "Days on which the listed pages got wording-only edits: tools/backfill_lastmod.py "
                                     "skips those days' changes when it dates the page."}, **cosmetic),
                      open(COSMETIC, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    skip_days = {}                                   # page -> {days whose edits do not count}
    for day, pages in cosmetic.items():
        for p in pages:
            skip_days.setdefault(p, set()).add(day)
    dirty = {l[3:].strip().strip('"') for l in git("status", "--porcelain").splitlines()}
    ledger = S.load_ledger()
    moved, rows = 0, []
    for key in sorted(ledger):
        if os.path.splitext(key)[1] == ".pdf":       # a binary: dated by its last commit
            path = os.path.join(S.SITE, key)
            if not os.path.exists(path):
                continue
            last = git("log", "-1", "--format=%cs", "--", key).strip()
            date = today if (key in dirty or not last) else last
            was = ledger[key].get("date")
            if was != date:
                moved += 1; rows.append((key, was, date, 1))
            ledger[key]["date"] = date
            continue
        rel = "index.html" if key == "index" else ("404.html" if key == "404" else key + "/index.html")
        path = os.path.join(S.SITE, rel)
        if not os.path.exists(path):
            continue
        now = S.authored_hash(open(path, encoding="utf-8").read())
        skip = skip_days.get(key, set())
        # versions newest first: the file on disk (today), then each commit that touched it
        versions = [(None, today)] + [tuple(c) for c in commits(rel)]
        versions = [v for v in versions if v[1] not in skip] or versions[-1:]
        sig = lambda v: now if v[0] is None else S.authored_hash(git("show", f"{v[0]}:{rel}"))
        ref, date, walked = sig(versions[0]), versions[0][1], 1
        for v in versions[1:]:
            walked += 1
            if sig(v) != ref:
                break
            date = v[1]
        was = ledger[key].get("date")
        if was != date or ledger[key].get("hash") != now:
            moved += was != date
            rows.append((key, was, date, walked))
        ledger[key] = {"hash": now, "date": date}
    for key, was, date, walked in rows:
        if was != date:
            print(f"  {key:<50} {was} -> {date}   ({walked} versions read)")
    print(f"{moved} dates corrected of {len(ledger)} entries" + (" (dry run, nothing written)" if dry else ""))
    if not dry:
        S.save_ledger(ledger)

if __name__ == "__main__":
    main()
