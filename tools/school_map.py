"""The Banqiao school map (2026-11-11, Chris: "this map is really lackluster").

A real street map drawn as inline SVG from data/banqiao_map.json (OpenStreetMap, see tools/fetch_banqiao_map.py):
parks, rivers, main roads with their names, MRT lines and stations, 1–3 km rings around the classroom, and the
28 schools. Pins drop in when the map scrolls into view; tapping a school opens a small card with its English
editions and a link. No map tiles or third-party scripts: one SVG, a little CSS and JS.

render(schools, ae, Z, esc) -> html.  Each school: name, level (國中/國小), lat, lon, km, href, eds [(grade, publisher)].
"""
import json, math, os, re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
PAD = 54
NAVY, GREEN, CORAL = "#1A2752", "#0E9F5A", "#E8704A"
BLUE_LINE, CIRC_LINE = "#0070BD", "#F2C200"           # 板南線, 環狀線 (Taipei Metro / New Taipei Metro colours)
BANNAN = ["江子翠", "新埔", "板橋", "府中", "亞東醫院", "海山"]
CIRCULAR = ["板新", "板橋", "新埔民生", "頭前庄"]          # 板橋 is the shared interchange
ROAD_NAMES = ["文化路", "中山路", "縣民大道", "民生路", "四川路", "中正路", "漢生東路", "環河西路", "金門街", "新海路", "民族路", "南雅南路"]


def render(schools, ae, Z, esc):
    M = json.load(open(os.path.join(SITE, "data", "banqiao_map.json"), encoding="utf-8"))
    la = [s["lat"] for s in schools] + [ae["lat"]]
    lo = [s["lon"] for s in schools] + [ae["lon"]]
    cy, cx = (min(la) + max(la)) / 2, (min(lo) + max(lo)) / 2
    kx = math.cos(math.radians(cy))
    k = min((W - 2 * PAD) / ((max(lo) - min(lo)) * kx), (H - 2 * PAD) / (max(la) - min(la)))

    def xy(lat, lon):
        return W / 2 + (lon - cx) * kx * k, H / 2 - (lat - cy) * k

    def d(pts, close=False):
        s, last = [], None
        for lat, lon in pts:
            x, y = xy(lat, lon)
            p = (round(x), round(y))
            if p != last:
                s.append(f"{p[0]},{p[1]}")
                last = p
        if len(s) < 2:
            return ""
        return "M" + "L".join(s) + ("Z" if close else "")

    def inside(pts, m=200):
        return any(-m < x < W + m and -m < y < H + m for x, y in (xy(*p) for p in pts))

    o = [f'<svg viewBox="0 0 {W} {H}" class="smap-svg" role="img" aria-label="{esc(Z("板橋區國中、國小和埃森美語的街道地圖", "street map of Banqiao junior highs, elementary schools and the school"))}">',
         '<defs><clipPath id="smc"><rect width="1000" height="700" rx="22"/></clipPath>'
         '<filter id="smsh" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="2" stdDeviation="2.2" flood-color="#1A2752" flood-opacity=".28"/></filter></defs>',
         '<g clip-path="url(#smc)"><rect width="1000" height="700" fill="#F4F1EA"/>']
    # parks, water, rivers
    o.append('<path class="sm-park" d="' + "".join(d(p["p"], True) for p in M["parks"] if inside(p["p"])) + '"/>')
    o.append('<path class="sm-water" d="' + "".join(d(p["p"], True) for p in M["water"] if inside(p["p"])) + '"/>')
    big = [r for r in M["rivers"] if r["n"] in ("大漢溪", "新店溪", "淡水河") and inside(r["p"])]
    small = [r for r in M["rivers"] if r not in big and inside(r["p"])]
    o.append('<path class="sm-river" d="' + "".join(d(r["p"]) for r in big) + '"/>')
    o.append('<path class="sm-creek" d="' + "".join(d(r["p"]) for r in small) + '"/>')
    # roads: casing first, then fill, minor to major
    order = [("tertiary", 2.2), ("secondary", 4), ("primary", 5.5), ("trunk", 6.5), ("motorway", 7)]
    paths = {kd: "".join(d(r["p"]) for r in M["roads"] if r["k"] == kd and inside(r["p"], 40)) for kd, _ in order}
    for kd, wd in order:
        o.append(f'<path class="sm-rc sm-{kd}" d="{paths[kd]}" stroke-width="{wd + 2}"/>')
    for kd, wd in order:
        o.append(f'<path class="sm-rf sm-{kd}" d="{paths[kd]}" stroke-width="{wd}"/>')
    o.append('<path class="sm-rail" d="' + "".join(d(r["p"]) for r in M["rail"] if inside(r["p"])) + '"/>')
    # road names: one label per road, on its longest straight-ish piece in the middle of the map
    labels = []
    for nm in ROAD_NAMES:
        best = None
        for r in M["roads"]:
            if not r["n"].startswith(nm):
                continue
            pts = [xy(*p) for p in r["p"]]
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                L = math.hypot(x1 - x0, y1 - y0)
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                if not (80 < mx < W - 80 and 60 < my < H - 60):
                    continue
                score = L - 0.15 * math.hypot(mx - W / 2, my - H / 2)
                if L > len(nm) * 13 + 10 and (best is None or score > best[0]):
                    best = (score, mx, my, math.degrees(math.atan2(y1 - y0, x1 - x0)))
        if best:
            _, mx, my, a = best
            a = a + 180 if a > 90 else a - 180 if a < -90 else a
            labels.append((mx, my, nm))
            o.append(f'<text class="sm-road" transform="translate({mx:.0f},{my:.0f}) rotate({a:.0f})" dy="4">{esc(nm)}</text>')
    for r in big:
        pts = [xy(*p) for p in r["p"]]
        vis = [(x, y) for x, y in pts if 40 < x < W - 120 and 40 < y < H - 40]
        if vis:
            x, y = vis[len(vis) // 2]
            o.append(f'<text class="sm-rname" x="{x:.0f}" y="{y:.0f}">{esc(r["n"])}</text>')
    # MRT lines through their stations (the lines run underground; stations are exact)
    st = {}
    for s in M["stations"]:
        if s["kind"] == "subway" and s["name"] not in st:
            st[s["name"]] = xy(s["lat"], s["lon"])
    # the two 板橋 entries (Bannan + Circular) sit 100 m apart: use each line's own
    pb = {s["net"]: xy(s["lat"], s["lon"]) for s in M["stations"] if s["name"] == "板橋" and s["kind"] == "subway"}

    def smooth(ps):
        if len(ps) < 2:
            return ""
        out = f"M{ps[0][0]:.0f},{ps[0][1]:.0f}"
        for i in range(len(ps) - 1):
            p0, p1, p2 = ps[max(i - 1, 0)], ps[i], ps[i + 1]
            p3 = ps[min(i + 2, len(ps) - 1)]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            out += f"C{c1[0]:.0f},{c1[1]:.0f} {c2[0]:.0f},{c2[1]:.0f} {p2[0]:.0f},{p2[1]:.0f}"
        return out
    bl = [pb.get("臺北捷運", st.get("板橋")) if n == "板橋" else st.get(n) for n in BANNAN]
    cl = [pb.get("新北捷運", st.get("板橋")) if n == "板橋" else st.get(n) for n in CIRCULAR]
    for pts, col in ((bl, BLUE_LINE), (cl, CIRC_LINE)):
        pts = [p for p in pts if p]
        # run each line off the map edge in its own direction
        if len(pts) >= 2:
            (ax_, ay_), (bx_, by_) = pts[0], pts[1]
            pts = [(ax_ + (ax_ - bx_) * 2, ay_ + (ay_ - by_) * 2)] + pts
            (ax_, ay_), (bx_, by_) = pts[-1], pts[-2]
            pts = pts + [(ax_ + (ax_ - bx_) * 2, ay_ + (ay_ - by_) * 2)]
        o.append(f'<path class="sm-mrt" d="{smooth(pts)}" stroke="#fff" stroke-width="9"/><path class="sm-mrt" d="{smooth(pts)}" stroke="{col}" stroke-width="5"/>')
    seen = set()
    stl = []
    for nm in BANNAN + CIRCULAR:
        if nm in seen or nm not in st:
            continue
        seen.add(nm)
        x, y = st[nm]
        if not (0 < x < W and 0 < y < H):
            continue
        both = nm == "板橋"
        col = BLUE_LINE if nm in BANNAN else CIRC_LINE
        if both:
            for net, c in (("臺北捷運", BLUE_LINE), ("新北捷運", CIRC_LINE)):
                px, py = pb.get(net, (x, y))
                o.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="6.5" fill="#fff" stroke="{c}" stroke-width="3.5"/>')
        else:
            o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="#fff" stroke="{col}" stroke-width="3.5"/>')
        stl.append((x, y, nm, "#0B4F8A" if nm in BANNAN else "#8a6d00"))
    # 1–3 km rings around the classroom
    ax, ay = xy(ae["lat"], ae["lon"])
    km = k / 111.0
    o.append('<g class="sm-rings">')
    for r in (1, 2, 3):
        o.append(f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="{r * km:.0f}"/>'
                 f'<text x="{ax + r * km * .71 + 4:.0f}" y="{ay - r * km * .71 - 4:.0f}">{r} km</text>')
    o.append("</g>")
    # label placement for schools and stations: try right, left, above, below; skip spots that hit others
    dots = [(xy(s["lat"], s["lon"]), 13 if s["level"] == "國中" else 8) for s in schools] + [((ax, ay), 20)] + \
           [((x, y), 7) for x, y, *_ in stl]
    placed = [(14, H - 92, 300, H - 14), (W - 210, 12, W - 12, 44)]
    def spot(x, y, text, size, r, prefer=None):
        tw, th = len(text) * size * 1.0 + 6, size * 1.2
        tries = [(r + 5, size * .36, "start"), (-r - 5, size * .36, "end"), (0, -r - 6, "middle"), (0, r + size + 2, "middle")]
        for dx, dy, anchor in tries:
            x0 = x + dx - (tw if anchor == "end" else tw / 2 if anchor == "middle" else 0)
            box = (x0, y + dy - th * .85, x0 + tw, y + dy + th * .25)
            if box[0] < 6 or box[2] > W - 6 or box[1] < 6 or box[3] > H - 6:
                continue
            hit = any(not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]) for b in placed)
            hit = hit or any((px - max(box[0], min(px, box[2]))) ** 2 + (py - max(box[1], min(py, box[3]))) ** 2 < (pr + 1) ** 2
                             for (px, py), pr in dots if (px, py) != (x, y))
            if not hit:
                placed.append(box)
                return x + dx, y + dy, anchor
        return None
    # the classroom label first, then junior highs, stations, elementary schools
    o.append('<g class="sm-st">')
    st_out = []
    for x, y, nm, c in stl:
        p = spot(x, y, nm + "站", 11.5, 7)
        if p:
            st_out.append(f'<text x="{p[0]:.0f}" y="{p[1]:.0f}" text-anchor="{p[2]}" fill="{c}">{esc(nm)}站</text>')
    pins = []
    for s in sorted(schools, key=lambda s: (s["level"] != "國中", s["km"])):
        x, y = xy(s["lat"], s["lon"])
        jh = s["level"] == "國中"
        nm = s["name"] if jh else s["name"].replace("國小", "")
        p = spot(x, y, nm, 14 if jh else 11.5, 12 if jh else 8)
        eds = "|".join(f"{g}:{pub}" for g, pub in s["eds"])
        lab = f'<text x="{p[0]:.0f}" y="{p[1]:.0f}" text-anchor="{p[2]}">{esc(nm)}</text>' if p else ""
        mark = (f'<path d="M0,0c-3.5-6-10.5-10.3-10.5-17.5a10.5,10.5 0 1 1 21,0c0,7.2-7,11.5-10.5,17.5z" fill="{NAVY}" stroke="#fff" stroke-width="2.5"/>'
                f'<circle cy="-17.5" r="4" fill="#fff"/>' if jh else
                f'<circle r="7" fill="{GREEN}" stroke="#fff" stroke-width="2.5"/>')
        pins.append((s["km"], f'<a class="sm-s {"sm-j" if jh else "sm-e"}" href="{esc(s["href"])}" data-n="{esc(s["name"])}" data-km="{s["km"]:.1f}" '
                     f'data-l="{s["level"]}" data-eds="{esc(eds)}" style="--d:{s["km"] * 0.28:.2f}s">'
                     f'<g class="sm-pin" transform="translate({x:.1f},{y + (0 if not jh else 0):.1f})"><g class="sm-drop">{mark}</g></g>{lab}</a>'))
    o.append("".join(st_out) + "</g>")
    o.append("".join(h for _, h in sorted(pins, key=lambda t: -t[0])))
    # the classroom: pulsing halo + star
    o.append(f'<g class="sm-ae" transform="translate({ax:.0f},{ay:.0f})"><circle class="sm-pulse" r="16"/><circle class="sm-pulse b" r="16"/>'
             f'<circle r="17" fill="#fff" filter="url(#smsh)"/>'
             f'<path d="M0,-11l3.4,7 7.6,1-5.5,5.3 1.4,7.6-6.9-3.7-6.9,3.7 1.4-7.6-5.5-5.3 7.6-1z" fill="{CORAL}"/></g>')
    p = spot(ax, ay, "埃森美語", 15, 20)
    if p:
        o.append(f'<text class="sm-aet" x="{p[0]:.0f}" y="{p[1]:.0f}" text-anchor="{p[2]}">{esc(Z("埃森美語", "American English"))}</text>')
    # legend + credit
    o.append(f'<g transform="translate(14,{H - 92})"><rect width="286" height="78" rx="14" fill="#fff" opacity=".94" filter="url(#smsh)"/>'
             f'<g transform="translate(22,30) scale(.8)"><path d="M0,0c-3.5-6-10.5-10.3-10.5-17.5a10.5,10.5 0 1 1 21,0c0,7.2-7,11.5-10.5,17.5z" transform="translate(0,9)" fill="{NAVY}"/></g>'
             f'<text x="40" y="27" class="sm-lg">{esc(Z("國中・點一下看版本和段考", "junior high · tap for editions and exams"))}</text>'
             f'<circle cx="22" cy="54" r="6.5" fill="{GREEN}" stroke="#fff" stroke-width="2"/><text x="40" y="59" class="sm-lg">{esc(Z("國小", "elementary"))}</text>'
             f'<line x1="104" y1="54" x2="128" y2="54" stroke="{BLUE_LINE}" stroke-width="5" stroke-linecap="round"/><text x="134" y="59" class="sm-lg">{esc(Z("板南線", "Bannan line"))}</text>'
             f'<line x1="196" y1="54" x2="220" y2="54" stroke="{CIRC_LINE}" stroke-width="5" stroke-linecap="round"/><text x="226" y="59" class="sm-lg">{esc(Z("環狀線", "Circular line"))}</text></g>')
    o.append(f'<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener"><text x="{W - 14}" y="{H - 12}" text-anchor="end" class="sm-cr">{esc(Z("地圖資料 © OpenStreetMap 貢獻者", "map data © OpenStreetMap contributors"))}</text></a>')
    o.append("</g></svg>")
    svg = "".join(o)
    chips = (f'<div class="smap-f" role="group" aria-label="{esc(Z("顯示", "show"))}">'
             f'<button type="button" class="on" data-f="all">{esc(Z("全部 28 所", "all 28"))}</button>'
             f'<button type="button" data-f="j">{esc(Z("國中 11 所", "11 junior highs"))}</button>'
             f'<button type="button" data-f="e">{esc(Z("國小 17 所", "17 elementary"))}</button></div>')
    card = '<div class="smap-card" hidden><button type="button" class="x" aria-label="close">×</button><b></b><span class="km"></span><div class="eds"></div><a class="go"></a></div>'
    t_go_j, t_go_e = Z("看這所國中的段考範圍 →", "this school's exam ranges →"), Z("看這所國小的期中期末範圍 →", "this school's exam ranges →")
    t_km, t_none = Z("離埃森美語直線約", "straight-line distance from the school: about"), Z("這學期計畫沒寫版本", "edition not stated this term")
    t_g = Z("年級", "grade")
    js = """<script>(()=>{const w=document.currentScript.previousElementSibling;if(!w)return;const svg=w.querySelector("svg"),card=w.querySelector(".smap-card");
const T=%s;let cur=null;
if("IntersectionObserver" in window&&!matchMedia("(prefers-reduced-motion: reduce)").matches){w.classList.add("pre");
const io=new IntersectionObserver(es=>{if(es[0].isIntersecting){w.classList.remove("pre");w.classList.add("go");io.disconnect()}},{threshold:.25});io.observe(w);setTimeout(()=>{if(w.classList.contains("pre")){w.classList.remove("pre");io.disconnect()}},8000)}
function show(a){cur=a;w.querySelectorAll(".sm-s.sel").forEach(e=>e.classList.remove("sel"));a.classList.add("sel");
const eds=(a.dataset.eds||"").split("|").filter(Boolean).map(x=>{const[g,p]=x.split(":");return `<span><i>${g}${T.g}</i>${p||T.none}</span>`}).join("");
card.querySelector("b").textContent=a.dataset.n;card.querySelector(".km").textContent=`${T.km} ${a.dataset.km} km`;
card.querySelector(".eds").innerHTML=eds||`<span>${T.none}</span>`;const go=card.querySelector(".go");go.href=a.getAttribute("href");go.textContent=a.dataset.l==="國中"?T.j:T.e;
card.hidden=false;const r=a.querySelector(".sm-pin").getBoundingClientRect(),b=w.getBoundingClientRect(),cw=card.offsetWidth,ch=card.offsetHeight;
let x=r.left-b.left+r.width/2-cw/2,y=r.top-b.top-ch-10;if(y<4)y=r.bottom-b.top+10;x=Math.max(6,Math.min(x,b.width-cw-6));
card.style.left=x+"px";card.style.top=y+"px";}
function hide(){card.hidden=true;cur=null;w.querySelectorAll(".sm-s.sel").forEach(e=>e.classList.remove("sel"))}
svg.addEventListener("click",e=>{const a=e.target.closest(".sm-s");if(!a){hide();return}if(cur!==a){e.preventDefault();show(a)}});
card.querySelector(".x").addEventListener("click",hide);document.addEventListener("keydown",e=>{if(e.key==="Escape")hide()});
w.querySelectorAll(".smap-f button").forEach(b=>b.addEventListener("click",()=>{w.querySelectorAll(".smap-f button").forEach(x=>x.classList.toggle("on",x===b));
w.dataset.f=b.dataset.f;hide()}));
const sc=w.querySelector(".smap-sc");if(sc&&sc.scrollWidth>sc.clientWidth){const ae=w.querySelector(".sm-ae").getBoundingClientRect(),s=sc.getBoundingClientRect();sc.scrollLeft=ae.left-s.left-s.width/2}
})()</script>""" % json.dumps({"g": t_g, "none": t_none, "km": t_km, "j": t_go_j, "e": t_go_e}, ensure_ascii=False)
    return (f'<div class="smap">{chips}<div class="smap-sc">{svg}</div>{card}'
            f'<p class="smap-hint">{esc(Z("← 地圖可以左右滑動 →", "← swipe the map →"))}</p></div>{js}')


CSS = """
.smap{position:relative;max-width:1060px;margin:6px auto 0}
.smap-sc{border-radius:22px;overflow:hidden;box-shadow:0 10px 34px rgba(26,39,82,.14);border:2px solid rgba(26,39,82,.07);background:#F4F1EA}
.smap-svg{display:block;width:100%;height:auto}
.smap-hint{display:none;text-align:center;font-size:12.5px;color:#64748b;margin:8px 0 0}
@media(max-width:720px){.smap-sc{overflow-x:auto;-webkit-overflow-scrolling:touch}.smap-svg{width:760px;max-width:none}.smap-hint{display:block}}
.smap-f{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:0 0 14px}
.smap-f button{border:2px solid rgba(26,39,82,.12);background:#fff;color:var(--navy);font-weight:800;font-size:14px;border-radius:99px;padding:7px 16px;cursor:pointer}
.smap-f button.on{background:var(--navy);border-color:var(--navy);color:#fff}
.smap[data-f=j] .sm-e,.smap[data-f=e] .sm-j{opacity:.12;pointer-events:none}
.sm-park{fill:#D7EDCF}.sm-water{fill:#B7DDF2}.sm-river{fill:none;stroke:#B7DDF2;stroke-width:16;stroke-linecap:round;stroke-linejoin:round}
.sm-creek{fill:none;stroke:#B7DDF2;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
.sm-rc,.sm-rf,.sm-rail,.sm-mrt{fill:none;stroke-linecap:round;stroke-linejoin:round}
.sm-rc{stroke:#E2DCCF}.sm-rf{stroke:#fff}.sm-rc.sm-primary,.sm-rc.sm-trunk,.sm-rc.sm-motorway{stroke:#EBCB8B}
.sm-rf.sm-primary{stroke:#FFF3C9}.sm-rf.sm-trunk,.sm-rf.sm-motorway{stroke:#FFE39A}
.sm-rail{stroke:#B9B2A4;stroke-width:2;stroke-dasharray:7 5}
.sm-road{font:700 11.5px 'DM Sans','Noto Sans TC',sans-serif;fill:#8C8272;text-anchor:middle;paint-order:stroke;stroke:#fff;stroke-width:3.5px;letter-spacing:.08em}
.sm-rname{font:italic 700 14px 'DM Sans','Noto Sans TC',sans-serif;fill:#3E8DBA;letter-spacing:.3em;paint-order:stroke;stroke:#F4F1EA;stroke-width:3px}
.sm-st text{font:800 11.5px 'DM Sans','Noto Sans TC',sans-serif;paint-order:stroke;stroke:#fff;stroke-width:3.5px}
.sm-rings circle{fill:none;stroke:#E8704A;stroke-opacity:.45;stroke-width:1.6;stroke-dasharray:3 6}
.sm-rings text{font:800 11px 'DM Sans',sans-serif;fill:#C55A36;paint-order:stroke;stroke:#F4F1EA;stroke-width:3px}
.sm-s{cursor:pointer}.sm-s text{paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round}
.sm-j text{font:800 14px 'DM Sans','Noto Sans TC',sans-serif;fill:#1A2752}
.sm-e text{font:700 11.5px 'DM Sans','Noto Sans TC',sans-serif;fill:#0B7A45}
.sm-drop{transition:transform .25s}.sm-j .sm-drop{filter:drop-shadow(0 3px 3px rgba(26,39,82,.3))}
.sm-s:hover .sm-drop,.sm-s.sel .sm-drop,.sm-s:focus-visible .sm-drop{transform:scale(1.25)}
.sm-s.sel.sm-j path{fill:#1CB0F6}.sm-s.sel.sm-e circle{fill:#1CB0F6}
.sm-aet{font:900 15px 'DM Sans','Noto Sans TC',sans-serif;fill:#B4482A;paint-order:stroke;stroke:#fff;stroke-width:4.5px}
.sm-pulse{fill:#E8704A;opacity:0;transform-box:fill-box;transform-origin:center;animation:smp 2.8s ease-out infinite}.sm-pulse.b{animation-delay:1.4s}
@keyframes smp{0%{opacity:.45;transform:scale(1)}100%{opacity:0;transform:scale(3.4)}}
.sm-lg{font:700 12px 'DM Sans','Noto Sans TC',sans-serif;fill:#1A2752}.sm-cr{font:600 10.5px 'DM Sans',sans-serif;fill:#8C8272}
.smap.pre .sm-drop{opacity:0;transform:translateY(-40px)}.smap.pre .sm-s text{opacity:0}.smap.pre .sm-rings circle{stroke-dashoffset:0;opacity:0}
.smap.go .sm-drop{animation:smd .7s cubic-bezier(.3,1.5,.5,1) var(--d) backwards}.smap.go .sm-s text{animation:smf .5s ease var(--d) backwards;animation-delay:calc(var(--d) + .35s)}
.smap.go .sm-rings circle{animation:smr 1.2s cubic-bezier(.2,.8,.2,1) backwards;transform-box:fill-box;transform-origin:center}
.smap.go .sm-rings circle:nth-of-type(2){animation-delay:.2s}.smap.go .sm-rings circle:nth-of-type(3){animation-delay:.4s}
@keyframes smd{0%{opacity:0;transform:translateY(-40px)}60%{opacity:1}100%{opacity:1;transform:none}}
@keyframes smf{from{opacity:0}to{opacity:1}}@keyframes smr{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}
.smap-card{position:absolute;z-index:5;width:250px;background:#fff;border-radius:16px;padding:14px 16px 12px;box-shadow:0 14px 40px rgba(26,39,82,.25);border-top:5px solid #1A2752}
.smap-card b{display:block;font-size:17px;color:var(--navy);padding-right:22px}.smap-card .km{display:block;font-size:12.5px;color:#64748b;margin:2px 0 8px}
.smap-card .eds{display:flex;flex-wrap:wrap;gap:6px}.smap-card .eds span{background:#F1F5FB;border-radius:10px;padding:4px 9px;font-size:13px;font-weight:800;color:var(--navy)}
.smap-card .eds i{font-style:normal;color:#64748b;font-weight:700;margin-right:4px}
.smap-card .go{display:block;margin-top:10px;font-weight:800;font-size:14px;color:#0B6FB8}
.smap-card .x{position:absolute;top:6px;right:8px;border:0;background:none;font-size:22px;color:#94a3b8;cursor:pointer;line-height:1}
@media(prefers-reduced-motion:reduce){.sm-pulse{animation:none}}
"""
