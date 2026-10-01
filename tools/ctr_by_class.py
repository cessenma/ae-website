#!/usr/bin/env python3
"""Search Console clicks, impressions and click rate grouped by page class.

Why: the site-wide click rate is a mix. One navigational page (/cool-english-guide/) and ten
instant-lookup pages hold about half of all impressions at 0.1-0.4% and no title can move
them, so the total falls whenever those pages gain impressions. Judge each class against its
own history instead. Classes live in data/page_classes.json (one per folder).

    python3 tools/ctr_by_class.py                 # last 28 days against the 28 before
    python3 tools/ctr_by_class.py --days 7
    python3 tools/ctr_by_class.py --pages         # also list each class's biggest movers

Reads the Search Console API with the token the GSC connector keeps in
~/Library/Application Support/mcp-gsc/token.json (read-only use; nothing is written to GSC).
"""
import argparse, collections, datetime, json, os, sys, urllib.parse, urllib.request

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROP = "sc-domain:americanenglish.com.tw"
ORIGIN = "https://americanenglish.com.tw"
TOKEN = os.path.expanduser("~/Library/Application Support/mcp-gsc/token.json")

def access():
    t = json.load(open(TOKEN))
    data = urllib.parse.urlencode({"client_id": t["client_id"], "client_secret": t["client_secret"],
                                   "refresh_token": t["refresh_token"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data)))["access_token"]

def pages(tok, start, end):
    url = "https://www.googleapis.com/webmasters/v3/sites/" + urllib.parse.quote(PROP, safe="") + "/searchAnalytics/query"
    body = {"startDate": str(start), "endDate": str(end), "dimensions": ["page"], "rowLimit": 2000}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    out = {}
    for r in json.load(urllib.request.urlopen(req)).get("rows", []):
        path = r["keys"][0].replace(ORIGIN, "").split("#")[0].split("?")[0]
        a = out.setdefault(path, [0, 0, 0.0])
        a[0] += r["clicks"]; a[1] += r["impressions"]; a[2] += r["position"] * r["impressions"]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--pages", action="store_true")
    a = ap.parse_args()
    classes = json.load(open(os.path.join(SITE, "data", "page_classes.json"), encoding="utf-8"))["classes"]
    end = datetime.date.today() - datetime.timedelta(days=3)          # Search Console lags about two days
    start = end - datetime.timedelta(days=a.days - 1)
    pend = start - datetime.timedelta(days=1); pstart = pend - datetime.timedelta(days=a.days - 1)
    tok = access()
    now, before = pages(tok, start, end), pages(tok, pstart, pend)
    def klass(path):
        key = path.strip("/") or "index"
        return classes.get(key) or ("home" if key == "index" else "PDF / file" if "." in key.split("/")[-1] else "not classed")
    def group(d):
        g = collections.defaultdict(lambda: [0, 0, 0.0, 0])
        for p, (c, i, pos) in d.items():
            x = g[klass(p)]; x[0] += c; x[1] += i; x[2] += pos; x[3] += 1
        return g
    gn, gb = group(now), group(before)
    print(f"{start} to {end}   (before: {pstart} to {pend})")
    print(f"{'class':<30}{'pages':>6}{'clicks':>8}{'before':>8}{'impr.':>9}{'before':>9}{'CTR':>7}{'before':>8}{'pos':>6}{'before':>8}")
    tot = [0, 0, 0, 0]
    for k in sorted(gn, key=lambda k: -gn[k][1]):
        c, i, pos, n = gn[k]; bc, bi, bpos, _ = gb.get(k, [0, 0, 0.0, 0])
        ctr = c / i * 100 if i else 0; bctr = bc / bi * 100 if bi else 0
        print(f"{k:<30}{n:>6}{int(c):>8}{int(bc):>8}{int(i):>9}{int(bi):>9}{ctr:>6.2f}%{bctr:>7.2f}%{pos / i if i else 0:>6.1f}{bpos / bi if bi else 0:>8.1f}")
        tot[0] += c; tot[1] += i; tot[2] += bc; tot[3] += bi
    print(f"{'ALL':<30}{len(now):>6}{int(tot[0]):>8}{int(tot[2]):>8}{int(tot[1]):>9}{int(tot[3]):>9}"
          f"{tot[0] / tot[1] * 100 if tot[1] else 0:>6.2f}%{tot[2] / tot[3] * 100 if tot[3] else 0:>7.2f}%")
    if a.pages:
        for k in sorted(gn, key=lambda k: -gn[k][1]):
            moves = sorted(((now[p][0] - before.get(p, [0, 0, 0])[0], p) for p in now if klass(p) == k), key=lambda x: abs(x[0]), reverse=True)[:5]
            print(f"\n{k}: biggest click changes")
            for d, p in moves:
                print(f"   {int(d):>+6}  {p}")

if __name__ == "__main__":
    main()
