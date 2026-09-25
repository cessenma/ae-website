#!/usr/bin/env python3
"""Product artwork for the exam-pack store (Lemon Squeezy Media, 4:3) and for the site.

Renders branded 1200×900 PNGs through the same headless Chromium the chart images use, so the
pictures are in the site's own fonts and palette. One generic cover for the single-level product
(the buyer picks the level inside the checkout), one per level for its gallery, one for the
KET+PET+FCE trio and one for all six. Colours are the site's accents, not the exam board's.

    python3 tools/build_product_images.py            # all nine
    python3 tools/build_product_images.py ket fce    # some
"""
import base64, os, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "assets", "img", "exams")
LOGO = os.path.join(SITE, "assets", "img", "american-english-banqiao-logo.jpg")
W, H = 1200, 900

# accent, dark accent, text colour on the accent
C = {"green": ("#06C755", "#04a046", "#fff"), "blue": ("#1CB0F6", "#1391cc", "#fff"),
     "purple": ("#CE82FF", "#a94fe0", "#fff"), "yellow": ("#FFC828", "#e0a800", "#1A2752"),
     "coral": ("#F0997B", "#d4795a", "#fff"), "navy": ("#1A2752", "#0f1a3a", "#fff")}

LEVELS = [  # slug, badge, sub-line, colour
    ("starters", "Starters", "Pre A1 · 劍橋兒童英檢", "green"),
    ("movers",   "Movers",   "A1 · 劍橋兒童英檢",     "blue"),
    ("flyers",   "Flyers",   "A2 · 劍橋兒童英檢",     "purple"),
    ("ket",      "KET",      "A2 Key · 劍橋英檢",     "yellow"),
    ("pet",      "PET",      "B1 Preliminary · 劍橋英檢", "coral"),
    ("fce",      "FCE",      "B2 First · 劍橋英檢",   "navy"),
]
CHIPS = ["題目卷", "中文逐題解析", "聽力音檔"]

def spec(slug):
    if slug == "single":
        return dict(kind="multi", badges=[l[1] for l in LEVELS], title="任選一級", count="9", colour="navy",
                    sub="Starters・Movers・Flyers・KET・PET・FCE")
    if slug == "kpf":
        return dict(kind="multi", badges=["KET", "PET", "FCE"], title="KET＋PET＋FCE 三級", count="27", colour="navy",
                    sub="A2 Key · B1 Preliminary · B2 First")
    if slug == "all":
        return dict(kind="multi", badges=[l[1] for l in LEVELS], title="全部六級", count="54", colour="navy",
                    sub="兒童英檢 Starters・Movers・Flyers ＋ KET・PET・FCE")
    for s, badge, sub, colour in LEVELS:
        if s == slug:
            return dict(kind="level", badge=badge, sub=sub, count="9", colour=colour)
    raise SystemExit(f"unknown slug {slug}")

def html(sp):
    acc, dk, fg = C[sp["colour"]]
    if sp["kind"] == "multi":          # light panel: every level chip reads, including the navy FCE one
        acc, fg = "#DDF4FF", "#1A2752"
    logo = "data:image/jpeg;base64," + base64.b64encode(open(LOGO, "rb").read()).decode()
    if sp["kind"] == "level":
        size = 190 if len(sp["badge"]) <= 3 else 120
        panel = (f'<div class="badge" style="font-size:{size}px">{sp["badge"]}</div>'
                 f'<div class="sub">{sp["sub"]}</div>')
        headline = "完整模擬試題"
    else:
        cols = 3 if len(sp["badges"]) == 6 else len(sp["badges"])
        fs = 30 if len(sp["badges"]) == 6 else 44
        mini = "".join(f'<span class="mini" style="background:{C[c][0]};color:{C[c][2]}">{b}</span>'
                       for b, c in zip(sp["badges"], [l[3] for l in LEVELS if l[1] in sp["badges"]]))
        panel = (f'<div class="minis" style="grid-template-columns:repeat({cols},1fr);font-size:{fs}px">{mini}</div>'
                 f'<div class="sub" style="margin-top:22px">{sp["sub"]}</div>')
        headline = sp["title"]
    chips = "".join(f'<li>{c}</li>' for c in CHIPS)
    return f"""<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@700;800&family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{font-family:'DM Sans',system-ui,sans-serif;color:#1A2752;background:linear-gradient(160deg,#fff 0%,#fef8f3 100%);position:relative}}
.dot{{position:absolute;border-radius:50%;opacity:.55}}
.card{{position:absolute;inset:44px;background:#fff;border-radius:36px;box-shadow:0 18px 60px rgba(26,39,82,.12);display:grid;grid-template-columns:470px 1fr;overflow:hidden;border:2px solid rgba(26,39,82,.06)}}
.panel{{background:{acc};color:{fg};display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 28px;text-align:center;position:relative}}
.panel::after{{content:"";position:absolute;right:-1px;top:0;bottom:0;width:2px;background:{dk};opacity:.35}}
.badge{{font-family:'Baloo 2',sans-serif;font-weight:800;letter-spacing:-.02em;line-height:.95}}
.sub{{font-family:'DM Sans',sans-serif;font-weight:700;font-size:26px;margin-top:18px;opacity:.92}}
.minis{{display:grid;gap:10px;width:100%}}
.mini{{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:inherit;padding:14px 4px;border-radius:16px;text-align:center;line-height:1;letter-spacing:-.01em;overflow:hidden;box-shadow:0 4px 0 rgba(0,0,0,.12)}}
.main{{padding:56px 56px 48px 60px;display:flex;flex-direction:column;justify-content:center;position:relative}}
.eyebrow{{font-weight:700;font-size:22px;letter-spacing:.14em;text-transform:uppercase;color:{dk if sp["colour"]!="navy" else "#1391cc"}}}
h1{{font-family:'DM Serif Display',serif;font-size:66px;line-height:1.05;margin:14px 0 6px;letter-spacing:-.01em}}
.count{{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:150px;line-height:.9;color:#1A2752;margin:6px 0 4px}}
.count small{{font-family:'DM Serif Display',serif;font-size:60px;margin-left:8px;color:#1A2752}}
ul{{list-style:none;padding:0;display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}}
li{{background:#DDF4FF;color:#1A2752;font-weight:700;font-size:26px;padding:12px 22px;border-radius:999px}}
.foot{{position:absolute;left:60px;right:56px;bottom:40px;display:flex;align-items:center;justify-content:space-between;font-size:19px;color:#4b5563}}
.foot img{{height:54px;width:54px;border-radius:14px;object-fit:cover;margin-right:14px;vertical-align:middle}}
.foot b{{color:#1A2752;font-size:21px}}
.disc{{white-space:nowrap;font-size:17px}}
</style></head><body>
<div class="dot" style="width:120px;height:120px;background:{acc};left:-30px;top:-30px"></div>
<div class="dot" style="width:70px;height:70px;background:#FFC828;right:60px;top:10px"></div>
<div class="dot" style="width:90px;height:90px;background:#CE82FF;right:-20px;bottom:-25px"></div>
<div class="card">
  <div class="panel">{panel}</div>
  <div class="main">
    <div class="eyebrow">American English · 埃森美語</div>
    <h1>{headline}</h1>
    <div class="count">{sp["count"]}<small>回</small></div>
    <ul>{chips}</ul>
    <div class="foot"><span><img src="{logo}" alt=""><b>americanenglish.com.tw</b></span><span class="disc">非官方試題・依官方題型格式自編</span></div>
  </div>
</div>
</body></html>"""

def main(which):
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for slug in which:
            pg.set_content(html(spec(slug)), wait_until="networkidle")
            pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            out = os.path.join(OUT, f"product-{slug}.png"); pg.screenshot(path=out)
            print(f"  product-{slug}.png  {os.path.getsize(out)//1024} KB")
        b.close()

if __name__ == "__main__":
    main(sys.argv[1:] or ["single"] + [l[0] for l in LEVELS] + ["kpf", "all"])
