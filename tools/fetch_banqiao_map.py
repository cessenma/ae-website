#!/usr/bin/env python3
"""Street-map layers for the Banqiao school map (2026-11-11, Chris: "this map is really lackluster").

Downloads roads, rail, MRT stations, rivers and parks around the 28 schools from OpenStreetMap (Overpass API)
and writes a small, simplified copy to data/banqiao_map.json, so the page build never needs the internet.
Map data © OpenStreetMap contributors (ODbL) — the map credits it on the page.

  python3 tools/fetch_banqiao_map.py                 download + write
  python3 tools/fetch_banqiao_map.py raw.json        reuse a saved Overpass answer
Run again only if the map area changes (new schools far outside the current box).
"""
import json, math, os, sys, urllib.parse, urllib.request

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "data", "banqiao_map.json")
BOX = (24.978, 121.418, 25.043, 121.496)           # s, w, n, e: the schools plus a margin
WBOX = (24.96, 121.40, 25.06, 121.51)              # rivers: a little wider so they run off the edges
Q = f"""[out:json][timeout:90];(
way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]{BOX};
way["railway"~"^(subway|rail)$"]{BOX};
node["railway"="station"]{BOX};
way["waterway"="river"]{WBOX};
way["natural"="water"]{WBOX};
relation["natural"="water"]{WBOX};
way["leisure"="park"]{BOX};
);out geom;"""


def fetch():
    if len(sys.argv) > 1:
        return json.load(open(sys.argv[1], encoding="utf-8"))
    req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                                 data=urllib.parse.urlencode({"data": Q}).encode(),
                                 headers={"User-Agent": "static-site-map-builder/1.0", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=180))


def simplify(pts, tol):
    """Douglas–Peucker on (lat, lon) in metres-ish units."""
    if len(pts) < 3:
        return pts
    k = math.cos(math.radians(25))
    def d(p, a, b):
        ax, ay, bx, by, px, py = a[1] * k, a[0], b[1] * k, b[0], p[1] * k, p[0]
        dx, dy = bx - ax, by - ay
        if dx == dy == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - ax - t * dx, py - ay - t * dy)
    i, dm = 0, 0
    for j in range(1, len(pts) - 1):
        dd = d(pts[j], pts[0], pts[-1])
        if dd > dm:
            i, dm = j, dd
    if dm > tol:
        return simplify(pts[:i + 1], tol)[:-1] + simplify(pts[i:], tol)
    return [pts[0], pts[-1]]


def line(e, tol=0.00004):
    return [[round(p["lat"], 5), round(p["lon"], 5)] for p in e["geometry"]] and \
        [[round(a, 5), round(b, 5)] for a, b in simplify([(p["lat"], p["lon"]) for p in e["geometry"]], tol)]


def rings(members):
    """Join a multipolygon's outer member ways end to end into closed rings."""
    segs = [[(p["lat"], p["lon"]) for p in m["geometry"]] for m in members if m.get("role") == "outer" and m.get("geometry")]
    out = []
    while segs:
        ring = segs.pop(0)
        grown = True
        while ring[0] != ring[-1] and grown:
            grown = False
            for i, s in enumerate(segs):
                if s[0] == ring[-1]:
                    ring += s[1:]
                elif s[-1] == ring[-1]:
                    ring += s[::-1][1:]
                elif s[-1] == ring[0]:
                    ring = s + ring[1:]
                elif s[0] == ring[0]:
                    ring = s[::-1] + ring[1:]
                else:
                    continue
                segs.pop(i)
                grown = True
                break
        out.append(ring)
    return out


def main():
    E = fetch()["elements"]
    tag = lambda e: e.get("tags", {})
    roads, rail, water, rivers, parks, stations = [], [], [], [], [], []
    for e in E:
        t = tag(e)
        if e["type"] == "node":
            stations.append({"name": t.get("name", ""), "kind": t.get("station") or "train",
                             "net": t.get("network", ""), "lat": round(e["lat"], 5), "lon": round(e["lon"], 5)})
        elif e["type"] == "way" and t.get("highway"):
            roads.append({"k": t["highway"], "n": t.get("name", ""), "tunnel": t.get("tunnel") == "yes", "p": line(e)})
        elif e["type"] == "way" and t.get("railway") == "rail":
            if t.get("tunnel") != "yes" and t.get("service") is None:
                rail.append({"n": t.get("name", ""), "p": line(e)})
        elif e["type"] == "way" and t.get("waterway") == "river":
            rivers.append({"n": t.get("name", ""), "p": line(e, 0.00006)})
        elif e["type"] == "way" and t.get("natural") == "water":
            p = line(e, 0.00005)
            if len(p) > 3:
                water.append({"n": t.get("name", ""), "p": p})
        elif e["type"] == "relation" and t.get("natural") == "water":
            for r in rings(e.get("members", [])):
                p = [[round(a, 5), round(b, 5)] for a, b in simplify(r, 0.00005)]
                if len(p) > 3:
                    water.append({"n": t.get("name", ""), "p": p})
        elif e["type"] == "way" and t.get("leisure") == "park":
            p = line(e, 0.00003)
            if len(p) > 3:
                parks.append({"n": t.get("name", ""), "p": p})
    out = {"_source": "OpenStreetMap contributors (ODbL), via Overpass API; tools/fetch_banqiao_map.py",
           "box": BOX, "roads": roads, "rail": rail, "rivers": rivers, "water": water, "parks": parks, "stations": stations}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{os.path.relpath(OUT, SITE)}: {len(roads)} roads, {len(rail)} rail, {len(rivers)} rivers, {len(water)} water, "
          f"{len(parks)} parks, {len(stations)} stations, {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
