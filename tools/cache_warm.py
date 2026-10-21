#!/usr/bin/env python3
"""
Keep Cloudflare's cache full, so crawlers are answered by Cloudflare and never reach Hostinger.

Why (2026-10-21): Hostinger's shared-hosting server answers automated traffic (GPTBot, Meta's
crawler — confirmed by Hostinger support in the access logs) with HTTP 429 whenever a request
reaches it, and that limit cannot be changed or whitelisted on this plan. Cloudflare keeps each
page for 1 day (Cache Rule "Edge-cache HTML … 1-day TTL"; errors 400–526 are not cached), so a
crawler only reaches Hostinger when a page has dropped out of the cache. This script re-loads
every page, PDF, chart and share picture that is missing from the cache, gently, with an ordinary
user agent that Hostinger serves normally. With Cloudflare's Smart Tiered Cache on, one copy loaded
from Taiwan also serves Cloudflare's other locations (GPTBot crawls from the US).

It runs from Chris's Mac (launchd, every 2 h): GitHub-hosted runners are answered 403 by Cloudflare.
Installed copy: ~/Library/Application Support/ae-cache-warm/cache_warm.py (outside ~/Documents, which
macOS privacy rules hide from background jobs). Log: ~/Library/Logs/ae-cache-warm.log (one JSON line a run).

    python3 tools/cache_warm.py            # one run
    python3 tools/cache_warm.py --verbose  # print every URL that was missing from the cache
"""
import gzip, json, os, re, sys, time, urllib.request, urllib.error, datetime

ORIGIN = "https://americanenglish.com.tw"
UA = "Mozilla/5.0 (compatible; AE-cache-warm/1.0; +https://americanenglish.com.tw/)"
LOG = os.path.expanduser("~/Library/Logs/ae-cache-warm.log")
VERBOSE = "--verbose" in sys.argv

def req(url, method="GET"):
    """(status, cf-cache-status, body bytes) — retries 429/5xx with a growing pause."""
    for wait in (0, 20, 60):
        if wait:
            time.sleep(wait)
        r = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
        try:
            with urllib.request.urlopen(r, timeout=40) as resp:
                body = resp.read() if method == "GET" else b""
                if resp.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return resp.status, resp.headers.get("cf-cache-status", "-"), body
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504, 520, 521, 522, 523, 524):
                return e.code, e.headers.get("cf-cache-status", "-") if e.headers else "-", b""
            last = (e.code, e.headers.get("cf-cache-status", "-") if e.headers else "-", b"")
        except Exception:
            last = (0, "-", b"")
    return last

def main():
    t0 = time.time()
    stats = {"HIT": 0, "filled": 0, "failed": 0}
    missing = []
    st, cs, sm = req(ORIGIN + "/sitemap.xml")
    if st != 200:
        print(f"sitemap.xml answered {st}; stopping"); return 1
    sm = sm.decode("utf-8", "replace")
    pages = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if u.endswith("/")]
    files = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if not u.endswith("/")]
    images = re.findall(r"<image:loc>([^<]+)</image:loc>", sm)
    extra = {ORIGIN + "/robots.txt", ORIGIN + "/llms.txt"}

    def touch(url, need_body=False):
        """HEAD first: a cached URL costs nothing. Otherwise GET it, which puts it in the cache."""
        if not need_body:
            st, cs, _ = req(url, "HEAD")
            if st == 200 and cs == "HIT":
                stats["HIT"] += 1; time.sleep(0.05); return b""
        st, cs, body = req(url, "GET")
        if st == 200 and cs == "HIT":
            stats["HIT"] += 1; time.sleep(0.05)
        elif st == 200:
            stats["filled"] += 1; missing.append(url); time.sleep(1.0)    # gentle on Hostinger
        else:
            stats["failed"] += 1; missing.append(f"{url} → {st}"); time.sleep(2.0)
        return body

    # pages: GET (compressed, ~10 KB each) so their share picture and stylesheet can be found
    for u in pages:
        body = touch(u, need_body=True).decode("utf-8", "replace")
        for m in re.finditer(r'<meta property="og:image" content="([^"]+)"', body):
            extra.add(m.group(1))
        for m in re.finditer(r'(?:href|src)="(/assets/(?:styles\.css|app\.js)\?v=[0-9a-f]+)"', body):
            extra.add(ORIGIN + m.group(1))
    for u in files + images + sorted(extra):
        if u.startswith(ORIGIN):
            touch(u)
    secs = int(time.time() - t0)
    line = dict(at=datetime.datetime.now().isoformat(timespec="seconds"), secs=secs, pages=len(pages),
                other=len(files) + len(images) + len(extra), **stats)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    open(LOG, "a").write(json.dumps(line) + "\n")
    print(json.dumps(line))
    if VERBOSE:
        for m in missing:
            print("  ", m)
    return 0

if __name__ == "__main__":
    sys.exit(main())
