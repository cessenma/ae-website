#!/usr/bin/env python3
"""板橋區 schools' English curriculum pages (2026-11-10).

Chris 11-10: "pages with links or downloads to all of the schools surrounding our own school with this
information. the english curriculum maps / downloads with a summary to help parents as a resource. this
is confusing and it needs pictures and colors. pages need to make this information simple and easy to
digest." He chose: all 板橋區 schools; link to the official plans + our own one-page summary PDF.

    ~/.claude/skills/seo/.venv/bin/python3 tools/build_school_pages.py
    then tools/seo_build.py (chrome, SEO blocks, sitemap date)

Writes
  banqiao-school-english/index.html                 hub: map, publisher grids, how exams work
  banqiao-school-english/<slug>/index.html          one page per junior high (11)
  banqiao-school-english/elementary/index.html      all 17 elementary schools
  assets/downloads/school-english/<file>.pdf        one-page summary per school (28)
  ~/Downloads/GLOSS-2026-11-10-SCHOOL-PAGES.md      every Chinese line with its English (Chris reads English)

Data (nothing on the pages is typed from memory)
  data/school_curriculum.json   per school + grade: publisher, units, exams (week, dates, lessons covered),
                                plan URL. Built from each school's own 115-1 English plan on the city
                                platform (rrcp.ntpc.edu.tw); where a plan contradicts itself, the "note"
                                says so and the page shows it.
  data/grammar_lesson_map.json  which 康軒/翰林/南一 lesson teaches each grammar point (the grammar books'
                                lesson map) — a 段考's grammar = the points taught in the lessons it covers.

Rules carried over from tools/school_calendars.py: a wrong exam date is worse than none, so every date
says where it came from and that the school's own notice wins; schools that are not near the classroom
are never called near (distances are straight-line km, never walking minutes).
"""
import datetime as dt, html, json, os, re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://americanenglish.com.tw"
LINE = "https://lin.ee/W9J8TuQ"
HUB = "banqiao-school-english"
GLOSS_OUT = os.path.expanduser("~/Downloads/GLOSS-2026-11-10-SCHOOL-PAGES.md")
PDF_DIR = os.path.join(SITE, "assets", "downloads", "school-english")
FONTS = os.path.expanduser("~/Documents/GitHub/ae-readers/tools/fonts")   # Noto Sans TC, Baloo 2, DM Sans (OFL)

D = json.load(open(os.path.join(SITE, "data", "school_curriculum.json"), encoding="utf-8"))
GM = json.load(open(os.path.join(SITE, "data", "grammar_lesson_map.json"), encoding="utf-8"))["books"]
SCHOOLS = D["schools"]
JH = [s for s in SCHOOLS if s["level"] == "國中"]
ES = [s for s in SCHOOLS if s["level"] == "國小"]
TERM = D["term_zh"]                       # 115 學年度上學期
TERM_SHORT = D["term_short"]              # 115 上
YEAR0 = 1911 + D["year"]                  # 2026: the semester's first calendar year

esc = html.escape
GLOSS, _page = {}, ["hub"]


def Z(zh, en):
    GLOSS.setdefault(_page[0], []).append((zh, en))
    return zh


# publisher colours: the site palette, one colour per publisher everywhere (pages, map, PDFs)
PUB = {"康軒": ("#1CB0F6", "#066d9e", "#E8F7FF", "Kang Hsuan"), "翰林": ("#06C755", "#047733", "#E7F9EE", "Hanlin"),
       "南一": ("#F0997B", "#a3471f", "#FFF1EB", "Nani"), "何嘉仁": ("#CE82FF", "#7a3db8", "#F6EBFF", "Hess"),
       "佳音": ("#FFC828", "#7a5a00", "#FFF8E1", "Joy"), "自編": ("#94a3b8", "#334155", "#F1F5F9", "school-made")}
UNKNOWN = ("#cbd5e1", "#475569", "#F8FAFC", "not stated")
EXAM_C = ["#1CB0F6", "#06C755", "#CE82FF"]           # 段考 1 / 2 / 3 (國小 期中 / 期末 use the first two)
GRADE_ZH = {"1": "一年級", "2": "二年級", "3": "三年級", "4": "四年級", "5": "五年級", "6": "六年級",
            "7": "七年級", "8": "八年級", "9": "九年級"}
JH_BOOK = {("7", 1): "第一冊", ("8", 1): "第三冊", ("9", 1): "第五冊", ("7", 2): "第二冊", ("8", 2): "第四冊", ("9", 2): "第六冊"}


def book_of(s, g):
    """The junior-high volume a grade reads this semester (national numbering); elementary numbering differs by
    city and start grade, so it is not shown."""
    return JH_BOOK.get((g, D["term"]), "") if s["level"] == "國中" else ""


# the site's existing page about each school (past papers / classes): linked both ways (route_blocks.py points back)
SCHOOL_PAGE = {"板橋國中": ("/banqiao-junior-high-english-past-papers/", "板橋國中考古題", "past papers"),
               "江翠國中": ("/jiangcui-junior-high-english/", "江翠國中考古題", "past papers"),
               "海山高中": ("/haishan-junior-high-english/", "海山國中部考古題", "past papers"),
               "新埔國中": ("/xinpu-junior-high-english/", "新埔國中考古題", "past papers"),
               "中山國中": ("/zhongshan-junior-high-english-banqiao/", "中山國中段考題", "past papers"),
               "大觀國小": ("/daguan-elementary-english/", "大觀國小附近英文班", "classes near the school"),
               "海山國小": ("/haishan-elementary-english/", "海山國小英文怎麼補", "English help"),
               "新埔國小": ("/xinpu-elementary-english/", "新埔國小英文怎麼補", "English help"),
               "中山國小": ("/zhongshan-elementary-english-banqiao/", "中山國小英文怎麼補", "English help")}


BOOK_CODE = {("7", 1): "G7-1", ("8", 1): "G8-1", ("9", 1): "G9-1", ("7", 2): "G7-2", ("8", 2): "G8-2", ("9", 2): "G9-2"}


def pub_of(g):
    return g.get("publisher") if g.get("publisher") in PUB else None


def chip(p, small=False, label=None):
    c = PUB.get(p, UNKNOWN)
    txt = label or (p if p else Z("未標明", "not stated"))
    return f'<span class="sc-chip{" sm" if small else ""}" style="--c:{c[0]};--ink:{c[1]};--bg:{c[2]}">{esc(txt)}</span>'


def cell(s, g):
    p = pub_of(s["grades"].get(g, {}))
    c = PUB.get(p, UNKNOWN)
    return f'<td class="pc" style="--bg:{c[2]}">{chip(p, small=True)}</td>'


def lesson_nums(labels):
    """Lesson numbers a list of unit ids covers: L1/U1/Lesson 1 -> 1; Get Ready/Starter -> 0."""
    out = set()
    for u in labels:
        if re.search(r"get ready|starter", u, re.I):
            out.add(0)
        m = re.match(r"^\s*(?:L|U|Lesson|Unit)\s*(\d+)\s*$", u, re.I)
        if m:
            out.add(int(m.group(1)))
    return out


def map_nums(label):
    """Lesson numbers in a grammar-map label for THIS book ('Get Ready・L1・L3', 'L1–L3', 'U3（while 複習）');
    a label that names another book (第三冊 …) or 未列為重點 gives nothing."""
    if not label or "冊" in label or "未列" in label:
        return set()
    out = set()
    if re.search(r"Get Ready|Starter", label):
        out.add(0)
    for a, b in re.findall(r"[LU](\d+)\s*[–-]\s*[LU]?(\d+)", label):
        out.update(range(int(a), int(b) + 1))
    out.update(int(x) for x in re.findall(r"[LU](\d+)", label))
    return out


def grammar_for(school_grade, grade, covers):
    """The grammar points (from our books' lesson map) taught in the lessons an exam covers."""
    p = pub_of(school_grade)
    code = BOOK_CODE.get((grade, D["term"]))
    if not p or p not in ("康軒", "翰林", "南一") or code not in GM:
        return []
    nums = lesson_nums(covers)
    return [pt for pt in GM[code]["points"] if map_nums(pt["map"][p]) & nums]


def week_start(g, week):
    """Monday-ish start of a teaching week from the plan’s first week ('8/31~9/4')."""
    m = re.match(r"\s*(\d{1,2})\s*/\s*(\d{1,2})", g.get("first_week") or "")
    if not m:
        return None
    d0 = dt.date(YEAR0, int(m.group(1)), int(m.group(2)))
    return d0 + dt.timedelta(days=7 * (week - 1))


def wk(e):
    """An exam's week as (first, last); a plan may give a range such as '9~10'."""
    w = e.get("week")
    if isinstance(w, int):
        return w, w
    nums = [int(x) for x in re.findall(r"\d+", str(w or ""))]
    return (nums[0], nums[-1]) if nums else (None, None)


def exam_when(e):
    a, b = wk(e)
    w = (f"第 {a} 週" if a == b else f"第 {a}–{b} 週") if a else ""
    return w + (f'（{e["dates"]}）' if e.get("dates") else "")


# ---------------------------------------------------------------- pictures (inline SVG)

def timeline_svg(g, exams, weeks=None, w=760):
    """The semester as a strip of weeks with each exam marked in its colour."""
    weeks = weeks or g.get("weeks") or 21
    pad, h, top = 18, 128, 38
    step = (w - 2 * pad) / weeks
    out = [f'<svg viewBox="0 0 {w} {h}" class="sc-tl" role="img" aria-label="{esc(Z("學期週次與段考位置", "semester weeks and exam positions"))}">']
    for i in range(weeks):
        x = pad + i * step
        out.append(f'<rect x="{x + 1:.1f}" y="{top}" width="{step - 2:.1f}" height="26" rx="5" fill="#EEF2F7"/>')
        if (i + 1) in (1, 5, 10, 15, 20) or i + 1 == weeks:
            out.append(f'<text x="{x + step / 2:.1f}" y="{top + 44}" text-anchor="middle" class="t-w">{i + 1}</text>')
    # month labels from the plan's first week
    seen = set()
    for i in range(weeks):
        d = week_start(g, i + 1)
        if d and d.month not in seen and (i == 0 or d.day <= 7):
            seen.add(d.month)
            out.append(f'<text x="{pad + i * step + 2:.1f}" y="{top - 8}" class="t-m">{d.month} 月</text>')
    for k, e in enumerate(exams):
        a, b = wk(e)
        if not a:
            continue
        b = min(b, weeks)
        x = pad + (a - 1) * step
        span = (b - a + 1) * step
        c = EXAM_C[k % 3]
        out.append(f'<rect x="{x + 1:.1f}" y="{top - 2}" width="{span - 2:.1f}" height="30" rx="6" fill="{c}"/>')
        lab = esc(e.get("short") or e.get("label") or f"段考 {k + 1}")
        mid = x + span / 2
        anchor = "end" if b > weeks - 2 else ("start" if a < 3 else "middle")
        tx = x + span if anchor == "end" else (x if anchor == "start" else mid)
        out.append(f'<text x="{tx:.1f}" y="{top + 64}" text-anchor="{anchor}" class="t-e" fill="{c}">{lab}</text>')
        if e.get("dates"):
            out.append(f'<text x="{tx:.1f}" y="{top + 80}" text-anchor="{anchor}" class="t-d">{esc(e["dates"])}</text>')
    out.append("</svg>")
    return "".join(out)


def map_svg(link_jh=True, w=680, h=520):
    """Schools around the classroom, positioned by latitude/longitude (straight-line, not walking)."""
    ae = D["ae"]
    pts = [(s["lat"], s["lon"]) for s in SCHOOLS] + [(ae["lat"], ae["lon"])]
    la0, la1 = min(p[0] for p in pts), max(p[0] for p in pts)
    lo0, lo1 = min(p[1] for p in pts), max(p[1] for p in pts)
    pad = 46
    kx = (w - 2 * pad) / (lo1 - lo0)
    ky = (h - 2 * pad) / (la1 - la0)
    k = min(kx, ky / 1.1)                                       # y is stretched by 1.1 below (latitude)
    cx, cy = (lo0 + lo1) / 2, (la0 + la1) / 2

    def xy(lat, lon):
        return w / 2 + (lon - cx) * k, h / 2 - (lat - cy) * k * 1.1

    out = [f'<svg viewBox="0 0 {w} {h}" class="sc-map" role="img" aria-label="{esc(Z("板橋區國中、國小和埃森美語的位置圖", "map of Banqiao junior highs, elementary schools and the school"))}">',
           f'<rect width="{w}" height="{h}" rx="22" fill="#F4FAFF"/>']
    ax, ay = xy(ae["lat"], ae["lon"])
    km = k / 111.0                                              # px per km (latitude)
    for r in (1, 2, 3):
        out.append(f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="{r * km * 1.1:.0f}" fill="none" stroke="#C9DFF0" stroke-dasharray="4 6"/>')
        out.append(f'<text x="{ax + r * km * 1.1 * .72:.0f}" y="{ay - r * km * 1.1 * .72:.0f}" class="m-r">{r} km</text>')
    # labels: junior highs first (bigger, linked), then elementary; each tries right, left, above, below and
    # takes the first spot that hits no dot and no label already placed
    dots = [(xy(s["lat"], s["lon"]), 10 if s["level"] == "國中" else 7) for s in SCHOOLS] + [((ax, ay), 14)]
    placed = [(18, h - 66, 228, h - 16)]                        # the legend box
    def spot(x, y, text, size, r):
        tw, th = len(text) * size * 1.02, size * 1.15
        for dx, dy, anchor in ((r + 4, size * .38, "start"), (-r - 4, size * .38, "end"),
                               (0, -r - 5, "middle"), (0, r + size, "middle")):
            x0 = x + dx - (tw if anchor == "end" else tw / 2 if anchor == "middle" else 0)
            box = (x0, y + dy - th * .85, x0 + tw, y + dy + th * .2)
            if box[0] < 4 or box[2] > w - 4 or box[1] < 4 or box[3] > h - 4:
                continue
            hit = any(not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]) for b in placed)
            hit = hit or any((px - max(box[0], min(px, box[2]))) ** 2 + (py - max(box[1], min(py, box[3]))) ** 2 < (pr + 1) ** 2
                             for (px, py), pr in dots if (px, py) != (x, y))
            if not hit:
                placed.append(box)
                return x + dx, y + dy, anchor
        placed.append((x + r + 4, y - th, x + r + 4 + tw, y))
        return x + r + 4, y + size * .38, "start"
    for s in sorted(SCHOOLS, key=lambda s: s["level"] != "國中"):
        x, y = xy(s["lat"], s["lon"])
        if s["level"] == "國中":
            tx, ty, an = spot(x, y, s["name"], 12.5, 10)
            dot = (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="#1A2752" stroke="#fff" stroke-width="3"/>'
                   f'<text x="{tx:.0f}" y="{ty:.0f}" text-anchor="{an}" class="m-j">{esc(s["name"])}</text>')
            out.append(f'<a href="/{HUB}/{s["slug"]}/">{dot}</a>' if link_jh else dot)
        else:
            nm = s["name"].replace("國小", "")
            tx, ty, an = spot(x, y, nm, 10.5, 7)
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="#FFC828" stroke="#fff" stroke-width="2"/>'
                       f'<text x="{tx:.0f}" y="{ty:.0f}" text-anchor="{an}" class="m-e">{esc(nm)}</text>')
    out.append(f'<path d="M{ax:.0f},{ay - 13:.0f} l4,9 10,1 -7,7 2,10 -9,-5 -9,5 2,-10 -7,-7 10,-1z" fill="#F0997B" stroke="#fff" stroke-width="2"/>'
               f'<text x="{ax + 14:.0f}" y="{ay + 20:.0f}" class="m-ae">{esc(Z("埃森美語", "American English (our school)"))}</text>')
    out.append(f'<g transform="translate(18,{h - 66})"><rect width="210" height="50" rx="12" fill="#fff" opacity=".92"/>'
               f'<circle cx="18" cy="16" r="7" fill="#1A2752"/><text x="32" y="21" class="m-l">{esc(Z("國中（點一下看那所學校）", "junior high (tap to open its page)"))}</text>'
               f'<circle cx="18" cy="36" r="6" fill="#FFC828"/><text x="32" y="41" class="m-l">{esc(Z("國小", "elementary school"))}</text></g>')
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------------- shared page parts

CSS = """
.sc-hero{text-align:center}
.sc-facts{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:16px}
.sc-facts span{background:#fff;border-radius:999px;padding:6px 13px;font-size:13px;font-weight:700;color:var(--navy);box-shadow:0 3px 10px rgba(26,39,82,.08)}
.sc-chip{display:inline-block;border-radius:999px;padding:5px 14px;font-weight:800;font-size:14px;color:#fff;background:var(--ink);white-space:nowrap;box-shadow:0 2px 0 rgba(0,0,0,.12)}
.sc-chip.sm{font-size:13px;padding:3px 11px}
.sc-grades{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:18px}
.sc-grades .g{background:#fff;border-radius:16px;padding:10px 14px;box-shadow:0 4px 14px rgba(26,39,82,.08);display:flex;gap:8px;align-items:center;font-weight:800;color:var(--navy);font-size:14px}
.sc-box{background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:20px;padding:20px 22px;box-shadow:0 4px 0 rgba(26,39,82,.05);margin-top:18px}
.sc-tl{width:100%;height:auto;display:block}
.sc-tl .t-w{font:700 12px 'DM Sans',sans-serif;fill:#94a3b8}.sc-tl .t-m{font:800 14px 'DM Sans',sans-serif;fill:#1A2752}
.sc-tl .t-e{font:800 16px 'DM Sans',sans-serif}.sc-tl .t-d{font:700 13px 'DM Sans',sans-serif;fill:#475569}
@media (max-width:640px){.sc-tl .t-e{font-size:22px}.sc-tl .t-d{font-size:18px}.sc-tl .t-m{font-size:18px}.sc-tl .t-w{display:none}}
.sc-map{width:100%;height:auto;display:block;max-width:760px;margin:0 auto}
.sc-map .m-j{font:800 12.5px 'DM Sans',sans-serif;fill:#1A2752}.sc-map .m-e{font:600 10.5px 'DM Sans',sans-serif;fill:#64748b}
.sc-map .m-ae{font:800 13px 'DM Sans',sans-serif;fill:#a3471f}.sc-map .m-r{font:700 10px 'DM Sans',sans-serif;fill:#94a3b8}
.sc-map .m-l{font:700 11px 'DM Sans',sans-serif;fill:#1A2752}.sc-map a:hover circle{fill:#1CB0F6}
.sc-table{width:100%;border-collapse:separate;border-spacing:0 6px;font-size:14px}
.sc-table th{font-size:12.5px;color:#64748b;font-weight:800;text-align:center;padding:2px 6px}
.sc-table th:first-child{text-align:left}
.sc-table td{background:#fff;padding:10px 8px;text-align:center}
.sc-table td.pc{background:var(--bg)}
.sc-table td:first-child{text-align:left;border-radius:12px 0 0 12px;font-weight:800;color:var(--navy);padding-left:14px}
.sc-table td:last-child{border-radius:0 12px 12px 0}
.sc-table a{color:var(--navy)}
.sc-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.sc-legend{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:14px 0 0}
.sc-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:20px}
.sc-card{background:#fff;border-radius:18px;padding:18px 20px;border-top:6px solid var(--c,#1CB0F6);box-shadow:0 6px 18px rgba(26,39,82,.08)}
.sc-card h3{margin:0 0 4px;font-size:18px;color:var(--navy)}
.sc-card .when{font-size:13px;font-weight:800;color:var(--c);margin-bottom:10px}
.sc-card .lbl{font-size:12px;font-weight:800;color:#64748b;margin:10px 0 4px;letter-spacing:.5px}
.sc-card ul{margin:0;padding-left:18px;font-size:14.5px;line-height:1.7;color:var(--text-body)}
.sc-card .lessons{display:flex;flex-wrap:wrap;gap:6px}
.sc-card .lessons span{background:#F4F7FB;border-radius:8px;padding:3px 8px;font-size:13px;color:var(--navy);font-weight:700}
.sc-card .lessons span i{font-style:normal;font-weight:600;color:#64748b}
.sc-card .note{font-size:12.5px;color:#a3471f;background:#FFF6F1;border-radius:10px;padding:8px 10px;margin-top:10px;line-height:1.6}
.sc-grade{margin-top:36px}
.sc-grade h2{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center}
.sc-dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin-top:14px}
.sc-dl a{display:flex;gap:10px;align-items:center;background:#fff;border-radius:14px;padding:12px 14px;text-decoration:none;color:var(--navy);font-weight:800;font-size:14px;box-shadow:0 3px 12px rgba(26,39,82,.08)}
.sc-dl a small{display:block;font-weight:600;color:#64748b;font-size:12px}
.sc-dl a .ic{flex:0 0 34px;height:34px;border-radius:10px;display:grid;place-items:center;color:#fff;font-size:15px;font-weight:800}
.sc-src{font-size:12.5px;color:#64748b;text-align:center;margin-top:10px;line-height:1.7}
.sc-why{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:20px}
.sc-why div{background:#fff;border-radius:18px;padding:18px 20px;box-shadow:0 4px 14px rgba(26,39,82,.07)}
.sc-why b{display:block;font-size:16px;color:var(--navy);margin:6px 0}
.sc-why p{margin:0;font-size:14.5px;line-height:1.8;color:var(--text-body)}
.sc-why .big{font:800 30px 'Baloo 2',sans-serif;color:var(--c,#1CB0F6);line-height:1}
.sc-others{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:14px}
.sc-others a{background:#fff;border-radius:999px;padding:7px 14px;font-weight:800;font-size:14px;color:var(--navy);text-decoration:none;box-shadow:0 3px 10px rgba(26,39,82,.08)}
.sc-es{background:#fff;border-radius:18px;margin-top:12px;box-shadow:0 4px 14px rgba(26,39,82,.07);overflow:hidden}
.sc-es summary{list-style:none;cursor:pointer;display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:14px 18px}
.sc-es summary::-webkit-details-marker{display:none}
.sc-es summary b{font-size:17px;color:var(--navy);min-width:90px}
.sc-es summary .km{margin-left:auto;font-size:12.5px;color:#64748b;font-weight:700}
.sc-es[open] summary{border-bottom:1px solid rgba(26,39,82,.08)}
.sc-es .in{padding:14px 18px 18px}
.sc-es table{width:100%;border-collapse:collapse;font-size:14px}
.sc-es th{font-size:12px;color:#64748b;text-align:left;padding:4px 6px;font-weight:800}
.sc-es td{padding:8px 6px;border-top:1px solid #eef2f7;vertical-align:top;line-height:1.6}
.sc-es td small{color:#64748b}
@media (max-width:640px){.sc-box{padding:16px}.sc-table{font-size:13px}}
"""


def head(slug, title, desc, ld):
    ldtags = "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
                     + "</script>\n" for x in ld)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#1A2752">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{ORIGIN}/{slug}/">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_TW">
<meta property="og:site_name" content="American English 埃森美語">
<meta property="og:title" content="{esc(title.split('｜')[0])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{ORIGIN}/{slug}/">
<meta property="og:image" content="{ORIGIN}/assets/img/school-english/og-map.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(Z("板橋區國中小英文版本地圖", "map of Banqiao schools' English textbooks"))}">
<meta name="twitter:card" content="summary_large_image">
{ldtags}<style>{CSS}</style>
</head>
<body>
<main id="top">
"""


FOOT = """
</main>
<script src="/assets/app.js"></script>
</body>
</html>
"""


def h2(eyebrow, hid, text, color=""):
    return (f'<div class="center stack reveal"><span class="eyebrow{(" eyebrow-" + color) if color else ""}">{eyebrow}</span>'
            f'<h2 id="{hid}">{text}</h2></div>')


def faq(items):
    out = []
    for q, a in items:
        qid = re.sub(r"[^\w一-鿿]+", "", re.sub(r"<[^>]+>", "", q))
        out.append(f'<div class="faq-item"><h3 id="{qid}" class="faq-h"><button class="faq-q" aria-expanded="false">{q}'
                   f'<span class="pm"></span></button></h3><div class="faq-a"><p>{a}</p></div></div>')
    return '<div class="faq reveal" style="margin-top:22px;max-width:820px;margin-left:auto;margin-right:auto">' + "".join(out) + "</div>"


def faq_ld(items):
    strip = lambda t: re.sub(r"<[^>]+>", "", t)
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in items]}


def cta():
    zh = Z("想知道孩子學校的版本和這學期的段考範圍，對應到我們的課程哪裡？加 LINE 告訴我們學校和年級，我們幫你對一次。",
           "Want to know how your child’s school edition and this semester’s exam range line up with our classes? Tell us the school and grade on LINE and we’ll check it with you.")
    return (f'<section class="section"><div class="container"><div class="sc-box reveal center" style="background:#F2FBF5;border-color:#bfe8cd">'
            f'<p style="margin:0 0 12px;font-size:16px;line-height:1.8;color:var(--navy);font-weight:700">{zh}</p>'
            f'<a class="btn btn-green" href="{LINE}" target="_blank" rel="noopener" data-line="school-english">{Z("LINE 問我們", "ask us on LINE")}</a></div></div></section>')


def source_line():
    return (f'<p class="sc-src">{Z("資料來源：各校", "Source: each school’s")} {TERM} {Z("英語課程計畫（", "English curriculum plan (")}'
            f'<a href="{D["source"]["url"]}" target="_blank" rel="noopener">{Z("新北市中小學課程備查網", "New Taipei curriculum platform")}</a>'
            f'{Z("），埃森美語整理於", "), summarised by American English on")} {D["checked"]}{Z("。段考日期和範圍以學校公告為準。", ". The school’s own notice decides exam dates and ranges.")}</p>')


def summary_pdf_name(s):
    return f'{s["slug"] or s["key"]}-{D["year"]}-{D["term"]}.pdf'


# ---------------------------------------------------------------- the hub

def es_grid_html(link=True):
    rows = []
    for s in sorted(ES, key=lambda x: x["km"]):
        cells = "".join(cell(s, g) for g in ("3", "4", "5", "6"))
        nm = f'<a href="/{HUB}/elementary/#{esc(s["name"])}">{esc(s["name"])}</a>' if link else esc(s["name"])
        rows.append(f'<tr><td>{nm}</td>{cells}</tr>')
    return (f'<div class="sc-scroll"><table class="sc-table"><thead><tr><th>{Z("學校", "school")}</th><th>{Z("三年級", "grade 3")}</th><th>{Z("四年級", "grade 4")}</th>'
            f'<th>{Z("五年級", "grade 5")}</th><th>{Z("六年級", "grade 6")}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def hub_page():
    _page[0] = "hub"
    title = Z("板橋國中小英文版本與段考範圍總覽（115學年）", "Banqiao schools: English editions and exam ranges (2026-27)") + "｜埃森美語"
    desc = Z("板橋區 11 所國中、17 所國小這學期英文用哪個版本、段考考哪幾課、什麼時候考：地圖和彩色圖表一次看懂，附各校官方課程計畫連結和免費一頁重點整理 PDF。",
             "Which English edition each of Banqiao’s 11 junior highs and 17 elementary schools uses this semester, what each exam covers and when: a map and colour charts, with links to every official plan and a free one-page summary PDF.")
    # junior-high publisher grid
    rows = []
    for s in sorted(JH, key=lambda x: x["km"]):
        cells = "".join(cell(s, g) for g in ("7", "8", "9"))
        rows.append(f'<tr><td><a href="/{HUB}/{s["slug"]}/">{esc(s["name"])}</a></td>{cells}</tr>')
    jh_grid = (f'<div class="sc-scroll"><table class="sc-table"><thead><tr><th>{Z("學校", "school")}</th><th>{Z("七年級", "grade 7")}</th>'
               f'<th>{Z("八年級", "grade 8")}</th><th>{Z("九年級", "grade 9")}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    rows = []
    for s in sorted(ES, key=lambda x: x["km"]):
        cells = "".join(cell(s, g) for g in ("3", "4", "5", "6"))
        rows.append(f'<tr><td><a href="/{HUB}/elementary/#{esc(s["name"])}">{esc(s["name"])}</a></td>{cells}</tr>')
    es_grid = es_grid_html()
    _unused = (f'<div class="sc-scroll"><table class="sc-table"><thead><tr><th>{Z("學校", "school")}</th><th>{Z("三年級", "grade 3")}</th><th>{Z("四年級", "grade 4")}</th>'
               f'<th>{Z("五年級", "grade 5")}</th><th>{Z("六年級", "grade 6")}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    used = sorted({pub_of(g) for s in SCHOOLS for g in s["grades"].values() if pub_of(g)}, key=list(PUB).index)
    legend = '<div class="sc-legend">' + "".join(chip(p) for p in used) + "</div>"
    # facts computed from the data, never typed
    jh_weeks = sorted({tuple(e["week"] for e in g["exams"] if e.get("week")) for s in JH for g in s["grades"].values() if g.get("exams")})
    common = max(jh_weeks, key=lambda t: sum(1 for s in JH for g in s["grades"].values() if tuple(e["week"] for e in g["exams"] if e.get("week")) == t))
    n_mixed = sum(1 for s in JH if len({pub_of(g) for g in s["grades"].values()} - {None}) > 1)   # unknown is not "different"
    ex = next(s for s in JH if s["name"] == "板橋國中")
    ex_txt = "、".join(f'{GRADE_ZH[g]}{pub_of(ex["grades"][g]) or ""}' for g in ("7", "8", "9"))
    es_two = sum(1 for s in ES for g in s["grades"].values() if len(g.get("exams") or []) == 2)
    es_all = sum(1 for s in ES for g in s["grades"].values() if g.get("exams") is not None)
    why = (f'<div class="sc-why">'
           f'<div style="--c:#1CB0F6"><span class="big">3</span><b>{Z("國中一學期三次段考", "junior high: three exams a semester")}</b><p>'
           + Z(f"板橋區國中的課程計畫大多把段考排在第 {common[0]}、{common[1]}、{common[2]} 週左右，每次考兩課左右；九年級另有模擬考。",
               f"Most Banqiao junior-high plans put the exams around weeks {common[0]}, {common[1]} and {common[2]}, about two lessons each; grade 9 also has mock exams.")
           + f'</p></div><div style="--c:#06C755"><span class="big">2</span><b>{Z("國小多半兩次", "elementary: usually two")}</b><p>'
           + Z(f"國小英文多是期中、期末兩次評量（{es_all} 份年級計畫裡有 {es_two} 份是兩次）。", f"Elementary English is mostly a midterm and a final ({es_two} of {es_all} grade plans have two).")
           + f'</p></div><div style="--c:#CE82FF"><span class="big">{n_mixed}</span><b>{Z("所國中各年級版本不一樣", "junior highs use different editions by grade")}</b><p>'
           + Z(f"同一所學校，不同年級可能用不同版本，例如板橋國中：{ex_txt}。看孩子那一個年級就好。",
               f"One school can use different editions in different grades — e.g. 板橋國中: {ex_txt}. Look at your child’s grade only.")
           + f'</p></div><div style="--c:#FFC828"><span class="big">1</span><b>{Z("文法清單只有一份", "one national grammar list")}</b><p>'
           + Z("版本不同，國中三年要學的文法是同一份課綱清單，只是先教後教不一樣。我們的國中文法書每一個重點都標出康軒、翰林、南一在哪一課。",
               "Editions differ, but the three years' grammar is one national list taught in a different order. Our junior-high grammar books mark the 康軒, 翰林 and 南一 lesson for every point.")
           + '</p></div></div>')
    dl_jh = "".join(f'<a href="/assets/downloads/school-english/{summary_pdf_name(s)}" download><span class="ic" style="background:#1A2752">PDF</span>'
                    f'<span>{esc(s["name"])}<small>{Z("一頁重點整理", "one-page summary")}</small></span></a>' for s in sorted(JH, key=lambda x: x["km"]))
    dl_es = "".join(f'<a href="/assets/downloads/school-english/{summary_pdf_name(s)}" download><span class="ic" style="background:#e0a800">PDF</span>'
                    f'<span>{esc(s["name"])}<small>{Z("一頁重點整理", "one-page summary")}</small></span></a>' for s in sorted(ES, key=lambda x: x["km"]))
    faqs = [(Z("這些資料是從哪裡來的？", "Where does this come from?"),
             Z(f"每所學校每學期都要把課程計畫上傳到新北市中小學課程備查網，公開給大家看。我們把 {TERM} 每校的英語課程計畫逐份讀過，整理出版本、各次段考的週次和範圍；每一頁都附原始計畫的連結。",
               f"Every school uploads its curriculum plans to New Taipei’s public curriculum platform each semester. We read each school’s {TERM} English plan and pulled out the edition, each exam’s week and range; every page links the original plan.")),
            (Z("段考日期會不會變？", "Can the exam dates change?"),
             Z("會。課程計畫是學期前寫的，日期偶爾會調整；學校網站和聯絡簿的公告才是最後版本。我們在每個日期旁邊都寫出它來自哪一份計畫。",
               "Yes. Plans are written before the semester and dates sometimes move; the school’s website and the contact book have the final word. Every date here says which plan it comes from.")),
            (Z("找不到孩子的學校？", "My child’s school isn’t here?"),
             Z("這裡只整理板橋區的公私立國中、國小。其他區的學校，課程計畫也都在同一個平台上，或加 LINE 告訴我們，我們幫你找。",
               "This covers Banqiao’s public and private junior highs and elementary schools only. Other districts' plans are on the same platform — or ask us on LINE and we’ll find it.")),
            (Z("多久更新一次？", "How often is it updated?"),
             Z("每學期一次：學校把下學期的課程計畫上傳後，我們就重新整理。頁面上方寫著目前是哪一個學期。",
               "Once a semester: when schools upload next semester’s plans, we redo it. The top of each page says which semester it shows."))]
    body = f"""
<section class="section section-light" style="padding-top:28px"><div class="container">
  <div class="breadcrumb reveal"><a href="/">首頁</a> ／ {Z("板橋國中小英文課程地圖", "Banqiao school English curriculum maps")}</div>
  <div class="sc-hero reveal">
    <span class="eyebrow">{TERM} · {Z("家長資源", "parent resource")}</span>
    <h1>{Z("板橋國中小英文課程地圖", "Banqiao school English curriculum maps")}</h1>
    <div class="divider"></div>
    <p class="lead" style="max-width:760px;margin:0 auto">{Z("板橋區 11 所國中、17 所國小：這學期英文用哪一個版本、段考考哪幾課、什麼時候考，整理成一眼看得懂的圖。每一所都附學校原始課程計畫的連結和免費一頁 PDF。",
       "Banqiao’s 11 junior highs and 17 elementary schools: which English edition this semester, what each exam covers and when — in pictures you can read at a glance, each with a link to the school’s own plan and a free one-page PDF.")}</p>
    <div class="sc-facts"><span>{Z("資料來自學校課程計畫", "from the schools' own plans")}</span><span>{Z("28 所學校", "28 schools")}</span><span>{Z("每學期更新", "updated every semester")}</span></div>
  </div>
</div></section>
<section class="section"><div class="container">
  {h2(Z("地圖", "map"), "地圖", Z("學校在哪裡", "where the schools are"))}
  <div class="sc-box reveal">{map_svg()}</div>
  <p class="sc-src">{Z("位置依地址換算，圓圈是直線距離，不是步行時間。點國中可以看那所學校的英文課程地圖。", "Positions come from addresses; the rings are straight-line distance, not walking time. Tap a junior high to open its page.")}</p>
</div></section>
<section class="section section-light"><div class="container">
  {h2(Z("國中", "junior high"), "國中版本", Z("國中：每個年級用哪個版本", "junior high: the edition in each grade"), "green")}
  {legend}
  <div class="sc-box reveal">{jh_grid}</div>
  <p class="sc-src">{Z("點學校名字，看三次段考各考哪幾課、哪些文法。", "Tap a school to see what each of the three exams covers.")}</p>
</div></section>
<section class="section"><div class="container">
  {h2(Z("國小", "elementary"), "國小版本", Z("國小：三到六年級用哪個版本", "elementary: the edition in grades 3–6"), "purple")}
  <div class="sc-box reveal">{es_grid}</div>
  <p class="sc-src">{Z("沙崙、重慶國小一、二年級也有英文課，詳見國小頁。", "沙崙 and 重慶 also teach English in grades 1–2; see the elementary page.")} <a href="/{HUB}/elementary/">{Z("看 17 所國小的期中、期末範圍", "see all 17 elementary schools' exam ranges")}</a></p>
</div></section>
<section class="section section-light"><div class="container">
  {h2(Z("一次看懂", "the short version"), "段考怎麼排", Z("段考怎麼排、版本為什麼不一樣", "how exams work and why editions differ"), "yellow")}
  {why}
</div></section>
<section class="section"><div class="container">
  {h2(Z("下載", "downloads"), "免費下載", Z("免費下載：每校一頁整理", "free download: one page per school"))}
  <h3 class="center" style="margin-top:18px">{Z("國中", "junior high")}</h3><div class="sc-dl reveal">{dl_jh}</div>
  <h3 class="center" style="margin-top:22px">{Z("國小", "elementary")}</h3><div class="sc-dl reveal">{dl_es}</div>
  {source_line()}
</div></section>
<section class="section section-light"><div class="container">
  {h2("FAQ", "常見問題", Z("常見問題", "questions"))}
  {faq(faqs)}
</div></section>
{cta()}
"""
    ld = [faq_ld(faqs)]
    write(f"{HUB}/index.html", head(HUB, title, desc, ld) + body + FOOT)


# ---------------------------------------------------------------- one junior high

def exam_card(s, g, grade, k, e, total):
    c = EXAM_C[k % 3]
    unit_title = {u["id"]: u.get("title") for u in g.get("units", [])}
    lessons = "".join(f'<span>{esc(u)}{(" <i>" + esc(unit_title[u]) + "</i>") if unit_title.get(u) else ""}</span>' for u in e.get("covers", []))
    pts = grammar_for(g, grade, e.get("covers", []))
    code = BOOK_CODE.get((grade, D["term"]))
    gram = ""
    if pts:
        gram = (f'<div class="lbl">{Z("文法重點", "grammar points")}</div><ul>'
                + "".join(f'<li>{esc(p["zh"])}</li>' for p in pts) + "</ul>"
                + f'<p style="margin:8px 0 0;font-size:13px"><a href="/english-grammar-books/#{code}">{Z("對應的文法書：", "matching grammar book: ")}{esc(GM[code]["title"])}</a></p>')
    name = e.get("label") or f"第{'一二三'[k]}次段考"
    note = f'<div class="note">{esc(Z(e["note"], e.get("note_en", "")))}</div>' if e.get("note") else ""
    return (f'<div class="sc-card reveal" style="--c:{c}"><h3>{esc(name)}</h3><div class="when">{esc(exam_when(e)) or Z("計畫裡沒有寫日期", "no date in the plan")}</div>'
            f'<div class="lbl">{Z("考試範圍", "covers")}</div><div class="lessons">{lessons or esc(Z("計畫裡沒有寫範圍", "no range in the plan"))}</div>{gram}{note}</div>')


def own_page(s):
    if s["name"] not in SCHOOL_PAGE:
        return ""
    href, zh, en = SCHOOL_PAGE[s["name"]]
    return (f'<a href="{href}"><span class="ic" style="background:#06C755">★</span><span>{Z(zh, en)}'
            f'<small>{Z("埃森美語整理", "our guide")}</small></span></a>')


def jh_page(s):
    _page[0] = s["slug"]
    nm = s["name"]
    title = Z(f"{nm}英文版本與段考範圍（115學年上學期）", f"{nm}: English editions and exam ranges (2026 fall)") + "｜埃森美語"
    pp = {g: (pub_of(s["grades"].get(g, {})) or "版本未標明") for g in ("7", "8", "9")}
    has_exams = any(gd.get("exams") for gd in s["grades"].values())
    if has_exams:
        desc = Z(f"{nm}這學期英文：七年級{pp['7']}、八年級{pp['8']}、九年級{pp['9']}。三次段考各考哪幾課、哪些文法、第幾週考，整理成彩色時間軸，附學校官方課程計畫連結和免費一頁 PDF。",
                 f"{nm} English this semester: grade 7 {pp['7']}, grade 8 {pp['8']}, grade 9 {pp['9']}. What each of the three exams covers and when, as a colour timeline, with the school’s official plans and a free one-page PDF.")
    else:
        desc = Z(f"{nm}這學期英文：七年級{pp['7']}、八年級{pp['8']}、九年級{pp['9']}。學校上傳的英語計畫是下學期的，上學期段考週次請看學校行事曆；附學校官方課程計畫連結和免費一頁 PDF。",
                 f"{nm} English this semester: grade 7 {pp['7']}, grade 8 {pp['8']}, grade 9 {pp['9']}. The plans the school uploaded are for spring, so see its calendar for this semester's exams; with the official plans and a free one-page PDF.")
    chips = "".join(f'<span class="g">{GRADE_ZH[g]} {chip(pub_of(s["grades"][g]))}</span>' for g in ("7", "8", "9") if g in s["grades"])
    grades_html, faqs = [], []
    for g in ("7", "8", "9"):
        if g not in s["grades"]:
            continue
        gd = s["grades"][g]
        exams = gd.get("exams") or []
        for k, e in enumerate(exams):
            e.setdefault("short", f"段考 {k + 1}")
        cards = "".join(exam_card(s, gd, g, k, e, len(exams)) for k, e in enumerate(exams))
        book = f'（{book_of(s, g)}）' if book_of(s, g) else ""
        pnote = "".join(f'<p class="sc-src" style="color:#a3471f">{esc(Z(gd[k], gd.get(k + "_en", "")))}</p>'
                        for k in ("publisher_note", "grade_note") if gd.get(k))
        other = ""
        if gd.get("other_tests"):
            other = ('<p class="sc-src">' + Z("其他考試：", "other tests: ") + "；".join(
                esc(f'{o.get("label", "")} {("第 " + str(o["week"]) + " 週") if o.get("week") else ""} {o.get("dates") or ""}'.strip()) for o in gd["other_tests"]) + "</p>")
        grades_html.append(f"""
<section class="section {'section-light' if g == '8' else ''} sc-grade"><div class="container">
  <div class="center stack reveal"><span class="eyebrow">{GRADE_ZH[g]}</span><h2 id="{GRADE_ZH[g]}">{GRADE_ZH[g]}{chip(pub_of(gd))}<span style="font-size:.7em;color:#64748b">{esc(book)}</span></h2></div>
  {pnote}
  <div class="sc-box reveal">{timeline_svg(gd, exams)}</div>
  <div class="sc-cards">{cards}</div>
  {other}
  <p class="sc-src"><a href="{gd["plan_url"]}" target="_blank" rel="noopener">{Z("看學校原始的", "open the school’s original")} {GRADE_ZH[g]}{Z("英語課程計畫（PDF）", " English plan (PDF)")}</a></p>
</div></section>""")
        if exams:
            first = exams[0]
            faqs.append((Z(f"{nm}{GRADE_ZH[g]}英文用哪個版本？第一次段考考什麼？", f"Which edition does {nm} grade {g} use, and what is on the first exam?"),
                         Z(f"依學校{TERM}的課程計畫，{GRADE_ZH[g]}英文是{pub_of(gd) or '（計畫未標明版本）'}{book_of(s, g)}；第一次段考在{exam_when(first) or '（計畫未寫週次）'}，範圍是 {'、'.join(first.get('covers', [])) or '（計畫未寫）'}。以學校公告為準。",
                           f"Per the school’s {TERM} plan, grade {g} uses {pub_of(gd) or 'an edition the plan does not name'}; the first exam is {exam_when(first)} covering {', '.join(first.get('covers', []))}. The school’s notice decides.")))
    faqs.append((Z("段考日期以什麼為準？", "Which date counts?"),
                 Z("課程計畫是學期開始前寫的，日期偶爾會調整；最後以學校網站、行事曆和聯絡簿的公告為準。",
                   "Plans are written before the semester and dates can move; the school’s website, calendar and contact book have the final word.")))
    others = "".join(f'<a href="/{HUB}/{o["slug"]}/">{esc(o["name"])}</a>' for o in sorted(JH, key=lambda x: x["km"]) if o is not s)
    plans = "".join(f'<a href="{s["grades"][g]["plan_url"]}" target="_blank" rel="noopener"><span class="ic" style="background:{PUB.get(pub_of(s["grades"][g]), UNKNOWN)[0]}">{g}</span>'
                    f'<span>{GRADE_ZH[g]}{Z("課程計畫", " plan")}<small>{Z("學校原始 PDF", "the school’s PDF")}</small></span></a>' for g in ("7", "8", "9") if g in s["grades"])
    body = f"""
<section class="section section-light" style="padding-top:28px"><div class="container">
  <div class="breadcrumb reveal"><a href="/">首頁</a> ／ <a href="/{HUB}/">{Z("板橋國中小英文課程地圖", "Banqiao school English curriculum maps")}</a> ／ {esc(nm)}</div>
  <div class="sc-hero reveal">
    <span class="eyebrow">{TERM} · {Z("國中英文課程地圖", "junior-high English curriculum map")}</span>
    <h1>{Z(f"{nm}英文版本與段考範圍", f"{nm}: English editions and exam ranges")}</h1>
    <div class="divider"></div>
    <p class="lead" style="max-width:740px;margin:0 auto">{Z("把學校公告的英文課程計畫整理成一頁：這學期三次段考各考哪幾課、哪些文法、大概什麼時候考。", "The school’s published English plans on one page: what each of this semester’s three exams covers, which grammar, and roughly when.")}</p>
    <div class="sc-grades">{chips}</div>
  </div>
</div></section>
{"".join(grades_html)}
<section class="section"><div class="container">
  {h2(Z("下載", "downloads"), "下載", Z("原始課程計畫和一頁整理", "the original plans and a one-page summary"))}
  <div class="sc-dl reveal">{plans}
    <a href="/assets/downloads/school-english/{summary_pdf_name(s)}" download><span class="ic" style="background:#F0997B">PDF</span><span>{Z("一頁重點整理", "one-page summary")}<small>{Z("埃森美語整理，免費", "made by us, free")}</small></span></a>
    <a href="{s["home"]}" target="_blank" rel="noopener"><span class="ic" style="background:#1A2752">⌂</span><span>{Z("學校網站", "school website")}<small>{Z("行事曆、段考公告", "calendar and exam notices")}</small></span></a>
    {own_page(s)}
  </div>
  {source_line()}
</div></section>
<section class="section section-light"><div class="container">
  {h2("FAQ", "常見問題", Z("常見問題", "questions"))}
  {faq(faqs)}
  <h3 class="center" style="margin-top:34px">{Z("其他板橋國中", "other Banqiao junior highs")}</h3>
  <div class="sc-others">{others}<a href="/{HUB}/elementary/">{Z("國小", "elementary")}</a></div>
</div></section>
{cta()}
"""
    write(f'{HUB}/{s["slug"]}/index.html', head(f'{HUB}/{s["slug"]}', title, desc, [faq_ld(faqs)]) + body + FOOT)


# ---------------------------------------------------------------- the elementary schools

def es_page():
    _page[0] = "elementary"
    title = Z("板橋區國小英文版本與期中期末範圍（115學年上學期）", "Banqiao elementary schools: English editions and exam ranges") + "｜埃森美語"
    desc = Z("板橋區 17 所國小這學期英文：三到六年級各用康軒、翰林還是何嘉仁，期中、期末考哪幾課、第幾週考。附學校官方課程計畫連結和免費一頁 PDF。",
             "Banqiao’s 17 elementary schools this semester: which edition (康軒, 翰林 or 何嘉仁) in grades 3–6, what the midterm and final cover and when, with the official plans and a free one-page PDF.")
    blocks = []
    for s in sorted(ES, key=lambda x: x["km"]):
        rows = []
        for g in sorted(s["grades"], key=int):
            gd = s["grades"][g]
            ex = []
            for k, e in enumerate(gd.get("exams") or []):
                ex.append(f'<b style="color:{EXAM_C[k % 3]}">{esc(e.get("label") or "")}</b> {esc(exam_when(e))}<br><small>{esc("、".join(e.get("covers", [])))}</small>')
            gn = "".join(f'<br><small style="color:#a3471f">{esc(Z(gd[k], gd.get(k + "_en", "")))}</small>' for k in ("publisher_note", "grade_note") if gd.get(k))
            rows.append(f'<tr><td><b>{GRADE_ZH[g]}</b></td><td>{chip(pub_of(gd), small=True)}</td><td>{"<br>".join(ex) or esc(Z("計畫裡沒有標出考試週", "no exam week marked in the plan"))}{gn}</td>'
                        f'<td><a href="{gd["plan_url"]}" target="_blank" rel="noopener">{Z("計畫", "plan")}</a></td></tr>')
        chips = "".join(f'<span style="font-size:12px;font-weight:800;color:#64748b">{g}年</span>{chip(pub_of(s["grades"][g]), small=True)}'
                        for g in sorted(s["grades"], key=int))
        blocks.append(f'<details class="sc-es reveal" id="{esc(s["name"])}"><summary><b>{esc(s["name"])}</b>{chips}<span class="km">{Z("直線約", "about")} {s["km"]:.1f} km</span></summary>'
                      f'<div class="in"><table><thead><tr><th>{Z("年級", "grade")}</th><th>{Z("版本", "edition")}</th><th>{Z("期中、期末", "midterm / final")}</th><th></th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
                      f'<p style="margin:12px 0 0;font-size:13.5px"><a href="/assets/downloads/school-english/{summary_pdf_name(s)}" download>{Z("下載一頁整理（PDF）", "download the one-page summary (PDF)")}</a> · '
                      f'<a href="{s["home"]}" target="_blank" rel="noopener">{Z("學校網站", "school website")}</a>'
                      + (f' · <a href="{SCHOOL_PAGE[s["name"]][0]}">{Z(SCHOOL_PAGE[s["name"]][1], SCHOOL_PAGE[s["name"]][2])}</a>' if s["name"] in SCHOOL_PAGE else "")
                      + '</p></div></details>')
    faqs = [(Z("國小英文有段考嗎？", "Do elementary schools have exams in English?"),
             Z("有，多半是期中、期末兩次評量，範圍是那段時間上過的單元。每所學校實際的週次見上面各校。",
               "Yes, usually a midterm and a final covering the units taught in that stretch; see each school above for its weeks.")),
            (Z("為什麼同一所國小每個年級版本不一樣？", "Why do grades in one school use different editions?"),
             Z("各年級的版本是學校分別選的，所以常常不一樣；看孩子那一個年級就好。", "Each grade’s edition is chosen separately, so they often differ; look at your child’s grade only."))]
    body = f"""
<section class="section section-light" style="padding-top:28px"><div class="container">
  <div class="breadcrumb reveal"><a href="/">首頁</a> ／ <a href="/{HUB}/">{Z("板橋國中小英文課程地圖", "Banqiao school English curriculum maps")}</a> ／ {Z("國小", "elementary")}</div>
  <div class="sc-hero reveal">
    <span class="eyebrow">{TERM} · {Z("國小英文課程地圖", "elementary English curriculum map")}</span>
    <h1>{Z("板橋區國小英文版本總覽", "Banqiao elementary schools: English editions")}</h1>
    <div class="divider"></div>
    <p class="lead" style="max-width:740px;margin:0 auto">{Z("17 所國小，依離埃森美語的直線距離排列。點學校名字展開：每個年級的版本、期中和期末考哪幾個單元、大概第幾週考。", "17 schools, nearest first. Tap a school: each grade’s edition, what the midterm and final cover, and roughly which week.")}</p>
  </div>
</div></section>
<section class="section"><div class="container">
  <div class="sc-legend">{"".join(chip(p) for p in ("康軒", "翰林", "何嘉仁"))}</div>
  <div class="sc-box reveal">{es_grid_html()}</div>
  <p class="sc-src">{Z("點學校名字，看那所學校每個年級的期中、期末範圍。", "Tap a school to see each grade’s midterm and final.")}</p>
  {"".join(blocks)}
  {source_line()}
</div></section>
<section class="section section-light"><div class="container">
  {h2("FAQ", "常見問題", Z("常見問題", "questions"))}
  {faq(faqs)}
</div></section>
{cta()}
"""
    write(f"{HUB}/elementary/index.html", head(f"{HUB}/elementary", title, desc, [faq_ld(faqs)]) + body + FOOT)


# ---------------------------------------------------------------- one-page summary PDFs

PDF_CSS = f"""
@font-face{{font-family:NotoTC;src:url(file://{FONTS}/NotoSansTC-Regular.ttf)}}
@font-face{{font-family:NotoTC;font-weight:700;src:url(file://{FONTS}/NotoSansTC-Bold.ttf)}}
@font-face{{font-family:Baloo;font-weight:800;src:url(file://{FONTS}/Baloo2-ExtraBold.ttf)}}
@font-face{{font-family:DM;src:url(file://{FONTS}/DMSans-Regular.ttf)}}
@font-face{{font-family:DM;font-weight:700;src:url(file://{FONTS}/DMSans-Bold.ttf)}}
@page{{size:A4;margin:10mm 11mm 12mm}}
body{{font-family:DM,NotoTC,sans-serif;color:#1A2752;font-size:9pt;margin:0}}
.band{{background:#1A2752;color:#fff;border-radius:5mm;padding:5mm 6mm;display:flex;justify-content:space-between;align-items:flex-end}}
.band h1{{margin:0;font-size:19pt;font-weight:700}}.band p{{margin:1mm 0 0;font-size:9pt;opacity:.85}}
.band .ae{{text-align:right;font-size:8pt;opacity:.9}}.band .ae b{{font-family:Baloo;font-size:12pt;display:block}}
.chips{{margin:4mm 0 2mm}}
.chip{{display:inline-block;border-radius:99px;padding:.6mm 3mm;font-weight:700;border:1.2pt solid;margin-right:2mm;font-size:9pt}}
.grade{{border:1pt solid #e2e8f0;border-radius:4mm;padding:3mm 4mm;margin-top:3mm;page-break-inside:avoid}}
.grade h2{{margin:0 0 2mm;font-size:12pt}}
.ex{{display:flex;gap:3mm}}.ex>div{{flex:1;border-radius:3mm;padding:2mm 3mm;background:#F8FAFC;border-top:2.2mm solid}}
.ex b{{display:block;font-size:9.5pt}}.ex .w{{font-size:8pt;font-weight:700}}.ex .c{{font-size:8pt;margin-top:1mm;line-height:1.45}}
.ex .gp{{font-size:7.6pt;color:#475569;margin-top:1mm;line-height:1.45}}
.foot{{position:fixed;bottom:-6mm;left:0;right:0;font-size:7pt;color:#64748b;text-align:center}}
.note{{font-size:7.5pt;color:#a3471f;margin-top:1.5mm}}
.six .grade{{padding:2mm 3.5mm;margin-top:2mm}}.six .grade h2{{font-size:11pt;margin-bottom:1mm}}.six .ex .c{{font-size:7.6pt}}
.ex>div.none{{border-top:0;background:none;color:#64748b;padding-left:0}}
.tips{{margin-top:4mm;background:#FFF8E1;border-radius:4mm;padding:3mm 5mm;page-break-inside:avoid}}
.tips b{{font-size:10pt}}.tips ol{{margin:1.5mm 0 0;padding-left:5mm;font-size:9pt;line-height:1.6}}
"""


def pdf_html(s):
    grades = []
    for g in sorted(s["grades"], key=int):
        gd = s["grades"][g]
        p = pub_of(gd)
        c = PUB.get(p, UNKNOWN)
        exs = []
        for k, e in enumerate(gd.get("exams") or []):
            pts = grammar_for(gd, g, e.get("covers", [])) if s["level"] == "國中" else []
            gp = f'<div class="gp">{esc("、".join(pt["zh"] for pt in pts))}</div>' if pts else ""
            exs.append(f'<div style="border-color:{EXAM_C[k % 3]}"><b>{esc(e.get("label") or "")}</b><span class="w">{esc(exam_when(e))}</span>'
                       f'<div class="c">{esc("、".join(e.get("covers", [])))}</div>{gp}</div>')
        none_div = '<div class="none">' + Z("計畫裡沒有標出考試週", "no exam week marked in the plan") + "</div>"
        note = "".join(f'<div class="note">{esc(gd[k])}</div>' for k in ("publisher_note", "grade_note") if gd.get(k))
        note += "".join(f'<div class="note">{esc(e["label"])}：{esc(e["note"])}</div>' for e in (gd.get("exams") or []) if e.get("note"))
        grades.append(f'<div class="grade"><h2>{GRADE_ZH[g]}　<span class="chip" style="color:{c[1]};border-color:{c[0]};background:{c[2]}">{esc(p or Z("版本未標明", "edition not stated"))}</span> '
                      f'<span style="font-size:9pt;color:#64748b">{esc(book_of(s, g))}</span></h2>'
                      f'<div class="ex">{"".join(exs) or none_div}</div>{note}</div>')
    url = f"americanenglish.com.tw/{HUB}/" + (f'{s["slug"]}/' if s["slug"] else "elementary/")
    _page[0] = "pdf"
    tips = [Z("考前兩週：對照範圍，把每一課的單字唸過、寫過。", "Two weeks before: go through each lesson's words, aloud and in writing."),
            Z("文法：每個重點做幾題，錯的那題回頭看規則。", "Grammar: do a few questions per point; when one is wrong, go back to the rule."),
            Z("考前一天：把課本對話大聲唸一次，聽力題比較不慌。", "The day before: read the textbook dialogues aloud once, so the listening part feels familiar.")]
    exam_word = Z("段考", "exam") if s["level"] == "國中" else Z("期中、期末", "midterm and final")
    tipbox = (f'<div class="tips"><b>{Z("準備", "getting ready for the")}{exam_word}{Z("的三個小步驟", ": three small steps")}</b><ol>'
              + "".join(f"<li>{esc(t)}</li>" for t in tips) + "</ol></div>")
    title = Z("英文課程地圖", "English curriculum map")
    sub = Z("版本、段考週次與範圍（依學校課程計畫整理）", "edition, exam weeks and ranges (from the school's own plan)")
    foot = (Z("資料來源：", "Source: ") + esc(s["name"]) + f" {TERM} " + Z("英語課程計畫（新北市中小學課程備查網 rrcp.ntpc.edu.tw），整理於", "English plan (New Taipei curriculum platform rrcp.ntpc.edu.tw), summarised on")
            + f' {D["checked"]}' + Z("。日期與範圍以學校公告為準。線上完整版：", ". The school's notice decides dates and ranges. Full version online: ") + url)
    six = ' class="six"' if len(grades) > 4 else ""
    return f"""<html><head><meta charset="utf-8"><style>{PDF_CSS}</style></head><body{six}>
<div class="band"><div><h1>{esc(s["name"])} {title}</h1><p>{TERM}・{sub}</p></div>
<div class="ae"><b>American English 埃森美語</b>{Z("板橋區中正路89巷4號", "No. 4, Ln. 89, Zhongzheng Rd, Banqiao")}</div></div>
{"".join(grades)}
{tipbox if len(grades) <= 4 else ""}
<div class="foot">{foot}</div>
</body></html>"""


def pdfs():
    from weasyprint import HTML
    os.makedirs(PDF_DIR, exist_ok=True)
    for s in SCHOOLS:
        HTML(string=pdf_html(s)).write_pdf(os.path.join(PDF_DIR, summary_pdf_name(s)))
    print(f"  {len(SCHOOLS)} summary PDFs -> {os.path.relpath(PDF_DIR, SITE)}")


# ---------------------------------------------------------------- gloss + write

def write(rel, text):
    p = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)
    print("  wrote", rel)


def write_gloss():
    L = [f"# Gloss — Banqiao school English pages ({D['checked']})", "",
         "Every Chinese line on the new pages with its English, so Chris can approve. Per-school pages repeat the same",
         "template with the school’s own data; only the first junior-high page is listed in full.", ""]
    seen = set()
    for page, items in GLOSS.items():
        if page not in ("hub", "elementary", "pdf") and page != JH[0]["slug"]:
            continue
        L += [f"## {page}", ""]
        for zh, en in items:
            if (zh, en) in seen:
                continue
            seen.add((zh, en))
            L += [f"- {zh}", f"  - *{en}*"]
        L.append("")
    L += ["## Other pages that now link here", "",
          "- Banqiao school calendar page, green box: 想知道孩子學校這學期英文用哪個版本、三次段考各考哪幾課？看 板橋國中小英文課程地圖（板橋區 28 所國中小，依各校課程計畫整理）。",
          "  - *Want to know which English edition your child's school uses this semester and what each of the three exams covers? See the Banqiao school English curriculum maps (28 Banqiao schools, from each school's own plan).*",
          "- Grammar books FAQ 「適用哪一個版本的課本？」 adds: 段考範圍表再告訴你每次段考要讀哪幾頁 … 不知道孩子學校用哪個版本？看板橋國中小英文課程地圖。",
          "  - *…and the exam-range page shows which pages to study before each exam … Not sure which edition your school uses? See the Banqiao curriculum maps.*",
          "- 'What next' boxes on the 4 junior-high past-paper pages: 考古題之外 · 考古題有了，這學期考哪幾課？ · [school]這學期英文用哪個版本、三次段考各考哪幾課、哪些文法，整理成彩色時間軸，附學校官方課程計畫。",
          "  - *Beyond past papers · You have the past papers — what's on this semester's exams? · [school]'s English edition this semester, what each of the three exams covers and which grammar, as a colour timeline, with the school's official plans.*",
          "  - 中山國中 version: 這學期用哪個版本？ … 附學校官方課程計畫和行事曆連結；板橋其他國中的段考範圍也在同一份地圖。 *(which edition this semester … with the official plan and calendar links; the other Banqiao junior highs' exam ranges are on the same map)*",
          "- 'What next' boxes on the 4 elementary pages: 課本之外 · [school]這學期考哪幾課？／用哪個版本？ · 三到六年級英文用哪個版本、期中和期末考哪幾個單元，依學校課程計畫整理。",
          "  - *Beyond the textbook · What's on [school]'s exams this semester? / Which edition? · Grades 3–6: the English edition, what the midterm and final cover, from the school's own plan.*",
          "- Buttons: [school]英文版本與段考範圍 = *[school] English edition and exam range* · 板橋國中小英文課程地圖 = *Banqiao school English curriculum maps*", ""]
    open(GLOSS_OUT, "w", encoding="utf-8").write("\n".join(L))
    print("  gloss:", GLOSS_OUT, sum(len(v) for v in GLOSS.values()), "strings")


def sitemap():
    """seo_build fills <lastmod> but only for URLs already listed; add ours once."""
    sm = os.path.join(SITE, "sitemap.xml")
    xml = open(sm, encoding="utf-8").read()
    urls = [f"{ORIGIN}/{HUB}/", f"{ORIGIN}/{HUB}/elementary/"] + [f'{ORIGIN}/{HUB}/{s["slug"]}/' for s in JH]
    add = [u for u in urls if f"<loc>{u}</loc>" not in xml]
    if add:
        xml = xml.replace("</urlset>", "".join(f"  <url><loc>{u}</loc></url>\n" for u in add) + "</urlset>")
        open(sm, "w", encoding="utf-8").write(xml)
    print(f"  sitemap: {len(add)} URLs added")


def og_image():
    """1200x630 share image: the title over the school map dots, publisher colours as the legend."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#1A2752")
    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(os.path.join(FONTS, "NotoSansTC-Bold.ttf"), 64)
    mid = ImageFont.truetype(os.path.join(FONTS, "NotoSansTC-Bold.ttf"), 30)
    small = ImageFont.truetype(os.path.join(FONTS, "NotoSansTC-Regular.ttf"), 26)
    # map dots on the right
    ae = D["ae"]
    la = [x["lat"] for x in SCHOOLS] + [ae["lat"]]
    lo = [x["lon"] for x in SCHOOLS] + [ae["lon"]]
    box = (650, 70, 1150, 560)
    k = min((box[2] - box[0]) / (max(lo) - min(lo)), (box[3] - box[1]) / (max(la) - min(la)) / 1.1)
    def xy(lat, lon):
        return box[0] + (lon - min(lo)) * k, box[3] - (lat - min(la)) * k * 1.1
    d.rounded_rectangle((630, 50, 1170, 580), 30, fill="#24356b")
    for x in ES:
        cx, cy = xy(x["lat"], x["lon"]); d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill="#FFC828")
    for x in JH:
        g = x["grades"]; p = pub_of(g.get("7", {})) or pub_of(g.get("8", {}))
        cx, cy = xy(x["lat"], x["lon"]); col = PUB.get(p, UNKNOWN)[0]
        d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=col, outline="#ffffff", width=4)
    cx, cy = xy(ae["lat"], ae["lon"]); d.regular_polygon((cx, cy, 18), 5, fill="#F0997B", outline="#ffffff")
    d.text((70, 120), "板橋國中小", font=big, fill="#ffffff")
    d.text((70, 200), "英文課程地圖", font=big, fill="#FFC828")
    d.text((70, 300), "版本・段考週次・範圍", font=mid, fill="#ffffff")
    d.text((70, 350), f"28 所學校　{TERM}", font=small, fill="#cbd5e1")
    x0 = 70
    for p in ("康軒", "翰林", "南一", "何嘉仁"):
        c = PUB[p]; w = d.textlength(p, font=small) + 36
        d.rounded_rectangle((x0, 430, x0 + w, 476), 23, fill=c[2], outline=c[0], width=3)
        d.text((x0 + 18, 437), p, font=small, fill=c[1]); x0 += w + 14
    d.text((70, 540), "americanenglish.com.tw　埃森美語", font=small, fill="#94a3b8")
    out = os.path.join(SITE, "assets", "img", "school-english", "og-map.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, optimize=True)
    print("  og image:", os.path.relpath(out, SITE))


if __name__ == "__main__":
    og_image()
    sitemap()
    hub_page()
    for s in JH:
        jh_page(s)
    es_page()
    pdfs()
    write_gloss()
