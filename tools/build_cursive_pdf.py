#!/usr/bin/env python3
"""
A4 cursive practice book for /english-cursive/: an A–Z chart, then a tracing row and a blank
four-line row for every letter pair, then the page's common words.

Why its own builder: the chart PDFs (build_chart_pdfs.py) print a page's table, and a cursive
learner needs ruled handwriting lines and grey letters to trace, which no table can give.
The searches it answers are file searches (英文草寫練習pdf, 練習字帖下載, 學習單 列印), where
the site already earns 19–57% CTR from the alphabet worksheet.

Letters are Google's "Playwrite US Trad" (US school cursive, OFL); the tracing rows use its
"Guides" twin, which draws the four handwriting lines inside every glyph, so the grey letters
always sit on their lines. Words come from the page's own spec (the table whose heads include
草寫), so the PDF and the page never disagree.

Usage:  python3 tools/build_cursive_pdf.py
"""
import os, re, json, html, base64

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "assets/downloads")
FNAME = "ae-english-cursive-practice-a4.pdf"
SPEC = os.path.join(SITE, "tools/data/topic_pages/english-cursive.json")
TITLE = "英文草寫練習本 A–Z"
SUB = "26 個字母大小寫描寫＋常用單字練習"
FS = 34          # px; one handwriting row is 1.5 em tall (ascender → descender)

def words():
    try:
        sp = json.load(open(SPEC, encoding="utf-8"))
    except FileNotFoundError:
        return []
    out = []
    for s in sp["sections"][1:]:
        if s.get("heads", [])[:2] == ["英文", "草寫"]:
            rows = [r for g in s.get("groups", []) for r in g["rows"]] + s.get("rows", [])
            out += [r[0] for r in rows]
    return out

CSS = f"""
@page{{size:A4 portrait;margin:11mm 12mm 14mm}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'DM Sans','PingFang TC','Noto Sans TC','Microsoft JhengHei',sans-serif;color:#26324d}}
.head{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid #F5C518;padding-bottom:6px;margin-bottom:10px}}
.head h1{{font-family:'DM Serif Display',Georgia,serif;font-size:20pt;color:#1A2752;font-weight:400;line-height:1.15}}
.head p{{font-size:9pt;color:#64748b;margin-top:3px}}
.br{{display:flex;align-items:center;gap:6px}} .br img{{width:30px;height:30px;border-radius:6px}}
.br span{{font-size:8pt;color:#64748b;line-height:1.3}} .br b{{display:block;font-size:9pt;color:#1A2752}}
h2{{font-family:'DM Serif Display',Georgia,serif;font-size:13pt;color:#1A2752;font-weight:400;margin:4px 0 6px}}
.tip{{font-size:8.5pt;color:#64748b;margin-bottom:8px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}}
.cell{{border:1px solid #e2e8f0;border-radius:6px;padding:4px 8px 2px;display:flex;justify-content:space-between;align-items:center;break-inside:avoid}}
.cell .p{{font-size:10pt;color:#94a3b8;font-weight:700}}
.cell .c{{font-family:'Playwrite US Trad',cursive;font-size:26pt;color:#1A2752;line-height:1.5}}
.pair{{break-inside:avoid;margin-bottom:6px}}
.trace{{font-family:'Playwrite US Trad Guides',cursive;font-size:{FS}px;line-height:1;color:#b8c2d1;
  white-space:nowrap;overflow:hidden;height:{1.5*FS + 4}px;padding-top:{0.05*FS:.1f}px}}
.tr{{position:relative}} .tr .bg{{position:absolute;left:0;right:0;top:0;margin:0}}
.trace{{position:relative}}
.blank{{position:relative;height:{1.5*FS + 4}px;margin-top:10px}}
.blank i{{position:absolute;left:0;right:0;border-top:1px solid #c7d0dc}}
.blank i.m{{border-top-style:dashed}}
.lbl{{font-size:8pt;color:#94a3b8;margin-bottom:1px}}
.page{{break-before:page}}
.foot{{position:fixed;bottom:0;left:0;right:0;font-size:7pt;color:#94a3b8;display:flex;justify-content:space-between}}
"""

def blank():
    # the Guides font's lines sit at 0, .5, 1 and 1.5 em below the ascender line
    y0 = 0.05 * FS - 0.045 * FS
    cls = ["", ' class="m"', "", ""]
    return ('<div class="blank">' + "".join(
        f'<i{cls[k]} style="top:{y0 + k * 0.5 * FS:.1f}px"></i>' for k in range(4)) + "</div>")

def trace(text, reps):
    sep = "\u2003"      # em space between repetitions
    return (f'<div class="tr">{blank().replace("blank", "blank bg", 1)}'
            f'<div class="trace">{sep.join([html.escape(text)] * reps)}</div></div>')

def build():
    letters = [(chr(65 + i), chr(97 + i)) for i in range(26)]
    lp = os.path.join(SITE, "assets/img/american-english-banqiao-logo.jpg")
    logo = "data:image/jpeg;base64," + base64.b64encode(open(lp, "rb").read()).decode()
    head = (f'<div class="head"><div><h1>{TITLE}</h1><p>{SUB}</p></div>'
            f'<div class="br"><img src="{logo}" alt=""><span><b>埃森美語</b>americanenglish.com.tw</span></div></div>')
    chart = '<div class="grid">' + "".join(
        f'<div class="cell"><span class="p">{u} {l}</span><span class="c">{u}{l}</span></div>' for u, l in letters) + "</div>"
    rows = "".join(
        f'<div class="pair"><div class="lbl">{u} {l}</div>{trace(u + l, 5)}{blank()}</div>' for u, l in letters)
    w = words()
    wrows = "".join(f'<div class="pair">{trace(x, 2 if len(x) < 9 else 1)}{blank()}</div>' for x in w)
    doc = f"""<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=DM+Serif+Display&family=Playwrite+US+Trad&family=Playwrite+US+Trad+Guides&display=swap" rel="stylesheet">
<title>{TITLE}｜埃森美語</title><style>{CSS}</style></head><body>
{head}
<h2>草寫字母表（大寫＋小寫）</h2>
<p class="tip">先看整張表，再往下練：灰色字照著描，下一行自己寫。每天 10 分鐘，一次練 3–4 個字母就好。</p>
{chart}
<h2 style="margin-top:14px">字母描寫練習</h2>
<p class="tip">描寫灰色字母，筆畫一筆到底不要停；下一行空白線自己寫一次。</p>
{rows}
{('<div class="page"></div><h2>常用單字草寫練習</h2><p class="tip">字母都會寫了，就練整個字：字母之間要連起來，大寫字母後面通常不連。</p>' + wrows) if w else ''}
<div class="foot"><span>埃森美語 American English・板橋</span>
<span>歡迎影印給學生使用，請保留此頁出處 americanenglish.com.tw/chart-license/</span></div>
</body></html>"""
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, FNAME)
    old = open(path, "rb").read() if os.path.exists(path) else None
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page()
        pg.set_content(doc, wait_until="networkidle"); pg.wait_for_timeout(1200)
        pg.pdf(path=path, format="A4", print_background=True)
        b.close()
    import importlib.util
    spec = importlib.util.spec_from_file_location("bcp", os.path.join(SITE, "tools/build_chart_pdfs.py"))
    bcp = importlib.util.module_from_spec(spec); spec.loader.exec_module(bcp)
    bcp.stamp_meta(path, TITLE, SUB)
    if old is not None:     # same content → keep the old bytes (Chromium stamps the time in)
        stamp = lambda x: re.sub(rb"/(CreationDate|ModDate) ?\(D:[^)]*\)", b"", x)
        if stamp(open(path, "rb").read()) == stamp(old):
            open(path, "wb").write(old)
    print(f"  {FNAME}  {os.path.getsize(path) / 1024:.0f}KB  ({len(w)} words)")
    print(f"     -> /english-cursive/ {bcp.offer('english-cursive', TITLE, SUB, FNAME, 'english-cursive-chart')}")
    return path

if __name__ == "__main__":
    build()
