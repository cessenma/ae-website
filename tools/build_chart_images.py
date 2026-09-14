#!/usr/bin/env python3
"""
Render the site's reference tables as branded PNG/WebP charts for Google Images.

Why: GSC Image search shows americanenglish.com.tw taking impressions for chart-shaped
queries (1200單字表 pos 14.3, 1-31日期英文 pos 14, 12時態) while the pages carry only
decorative stock photos. People searching Images for 「KK音標表」 want the table itself.
The one image click the site has ever had came from 國小1200單字分類 at position 2.8 —
i.e. when a relevant image exists, it ranks.

Tables are pulled live from each page so a chart can never drift from the page it came from.
Text is rendered by a real browser, never by an image model, so every phonetic symbol is exact.

Usage:  python3 tools/build_chart_images.py [slug ...]
"""
import os, re, sys, json, html
from bs4 import BeautifulSoup

SITE = os.path.expanduser("~/Documents/GitHub/ae-website")
OUT  = os.path.join(SITE, "assets/img/charts")
ORIGIN = "https://americanenglish.com.tw"

# slug -> page, which tables, chart title/subtitle, and the alt text (written as the
# query a person actually types into Images).
SPECS = {
 "english-vowels-chart": dict(
    page="english-pronunciation", only={1}, anchor_nth=1,
    title="英文母音發音表",
    sub="17 個母音 ・ 短音、長音與雙母音，附例字與嘴型提示",
    alt="英文母音發音表：17個母音的音標、例字與嘴型提示，含短母音長母音與雙母音",
    foot="免費 A4 列印版下載"),
 "english-consonants-chart": dict(
    page="english-pronunciation", only={2}, anchor_nth=2,
    title="英文子音發音表",
    sub="24 個子音 ・ 有聲無聲配對與發音位置",
    alt="英文子音發音表：24個子音的有聲無聲配對、例字與發音位置對照",
    foot="免費 A4 列印版下載"),
 "english-ending-sounds-chart": dict(
    page="english-pronunciation", only={3}, anchor_nth=3,
    title="字尾 -s 與 -ed 發音規則",
    sub="各三種唸法 ・ 由前一個音決定",
    alt="英文字尾-s與-ed發音規則表：三種唸法與判斷方式，附例字",
    foot="免費 A4 列印版下載"),
 "kk-phonetic-chart-full": dict(
    page="kk-phonetic-chart", tables="all",
    title="KK 音標表 完整對照",
    sub="母音 17 個 ・ 子音 24 個 ・ 共 41 個音標符號，附例字",
    alt="KK音標表完整對照：母音17個與子音24個共41個符號，附例字與有聲無聲配對",
    foot="免費 A4 列印版下載"),
 "phonics-rules-chart-full": dict(
    page="phonics-rules-chart", tables="all",
    title="自然發音規則總表",
    sub="字母音 ・ 短母音 ・ 長母音 ・ 母音組合 ・ 子音組合",
    alt="自然發音規則總表：字母音、短母音、長母音與母音組合的完整對照表",
    foot="免費 A4 列印版下載"),
 "moe-1200-words-categories": dict(
    page="moe-1200-words-guide", tables="all", max_rows=121, cols=3,
    title="教育部國小 1200 單字 分類表",
    sub="108 課綱附錄五・基本 1,200 字（節錄前 120 字，完整字表見網站）",
    alt="教育部國小英文1200單字分類表，依主題整理的必備單字對照",
    foot="完整字表與 Excel／PDF 下載"),
 "animals-english-table": dict(
    page="animals-english-vocabulary", tables="all", cols=2,
    title="動物英文 對照表",
    sub="哺乳類 ・ 鳥類 ・ 水生 ・ 昆蟲 ・ 爬蟲兩棲",
    alt="動物英文對照表：常見動物的英文名稱與中文對照，附KK音標",
    foot="americanenglish.com.tw"),
}

SPECS.update({
 "numbers-1-100-chart": dict(page="numbers-1-100-english", cols=4, max_rows=101,
   title="英文數字 1-100 對照表", sub="0 到 100 ・ 英文拼法與中文對照",
   alt="英文數字1到100完整對照表，每個數字的英文拼法與中文對照",
   foot="可儲存列印｜americanenglish.com.tw"),
 "months-english-chart": dict(page="months-english",
   title="1-12 月份英文對照表", sub="英文 ・ 中文 ・ 縮寫 ・ 天數",
   alt="1到12月份英文對照表，含月份英文、中文、縮寫與每月天數",
   foot="可儲存列印｜americanenglish.com.tw"),
 "days-week-english-chart": dict(page="days-of-week-english",
   title="星期英文對照表", sub="星期一到星期日 ・ 英文、縮寫與口語說法",
   alt="星期英文對照表：星期一到星期日的英文、中文、縮寫與口語說法",
   foot="可儲存列印｜americanenglish.com.tw"),
 "colors-english-chart": dict(page="colors-english", cols=3, width=1500,
   title="顏色英文對照表", sub="62 個常用顏色 ・ 依色系分組",
   alt="顏色英文對照表：62個常用顏色的英文與中文對照，依色系分組",
   foot="可儲存列印｜americanenglish.com.tw"),
 "fruits-english-chart": dict(page="fruits-english", cols=2,
   title="水果英文對照表", sub="47 種水果 ・ 含芭樂、蓮霧、釋迦等台灣水果",
   alt="水果英文對照表：47種水果的英文與中文，含芭樂蓮霧釋迦等台灣水果說法",
   foot="可儲存列印｜americanenglish.com.tw"),
 "body-parts-english-chart": dict(page="body-parts-english", cols=2,
   title="身體部位英文對照表", sub="43 個部位 ・ 頭臉、上半身、下半身與體內",
   alt="身體部位英文對照表：43個身體部位的英文與中文，分頭臉上半身下半身與體內",
   foot="可儲存列印｜americanenglish.com.tw"),

 "countries-english-chart": dict(page="countries-english", cols=2, width=1560,
   title="國家英文對照表", sub="80 國 ・ 國名、中文與國籍形容詞",
   alt="國家英文對照表：80個國家的英文名稱、中文與國籍形容詞對照",
   foot="可儲存列印｜americanenglish.com.tw"),
 "jobs-english-chart": dict(page="jobs-english", cols=3, width=1560,
   title="職業英文對照表", sub="83 種工作 ・ 依領域分組",
   alt="職業英文對照表：83種常見工作的英文與中文對照，依領域分組",
   foot="可儲存列印｜americanenglish.com.tw"),
})

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans','PingFang TC','Noto Sans TC','Microsoft JhengHei',sans-serif;
  background:#fff;width:__W__px}
.card{background:#fff}
.head{background:linear-gradient(135deg,#1A2752 0%,#26407e 100%);color:#fff;padding:38px 46px 34px;position:relative;overflow:hidden}
.head::after{content:'';position:absolute;right:-60px;top:-60px;width:260px;height:260px;border-radius:50%;
  background:rgba(28,176,246,.22)}
.head h1{font-family:'DM Serif Display',Georgia,serif;font-size:52px;line-height:1.1;font-weight:400;
  letter-spacing:-1px;position:relative;z-index:2}
.head p{font-size:21px;color:#9fc6ef;margin-top:12px;position:relative;z-index:2;font-weight:500}
.bar{height:7px;background:linear-gradient(90deg,#1CB0F6,#CE82FF,#FFC828)}
.body{padding:30px 40px 26px}
.grp{margin-bottom:26px}
.grp:last-child{margin-bottom:0}
.grp h2{font-family:'DM Serif Display',Georgia,serif;font-size:27px;color:#1A2752;margin-bottom:12px;
  padding-left:13px;border-left:6px solid #1CB0F6;line-height:1.25;font-weight:400}
table{border-collapse:collapse;width:100%;font-size:21px;table-layout:fixed}
.c3 table{font-size:17px}
.c3 td,.c3 th{padding:7px 9px}
.c3 td:first-child{white-space:nowrap}
th{background:#DDF4FF;color:#1A2752;font-weight:700;text-align:left;padding:11px 14px;
  font-size:18px;border-bottom:2px solid #1CB0F6}
td{padding:10px 14px;border-bottom:1px solid #e8eef7;color:#26324d;vertical-align:middle}
tr:nth-child(even) td{background:#fafcff}
td:first-child{font-weight:700;color:#1A2752}
.foot{display:flex;align-items:center;justify-content:space-between;gap:20px;
  padding:20px 46px 24px;border-top:2px solid #eef3fa;background:#fff}
.brand{display:flex;align-items:center;gap:13px}
.brand img{width:52px;height:52px;border-radius:50%;object-fit:cover}
.brand .n{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:25px;color:#1A2752;line-height:1.15}
.brand .u{font-size:17px;color:#7b8aa6;font-weight:500}
.tag{background:#06C755;color:#fff;font-family:'Baloo 2',sans-serif;font-weight:800;font-size:19px;
  padding:11px 22px;border-radius:12px;white-space:nowrap}
"""

def reflow(table_html, cols):
    """Re-lay a long narrow table into `cols` side-by-side copies of its columns."""
    t = BeautifulSoup(table_html, "html.parser").find("table")
    rows = t.find_all("tr")
    head = rows[0] if rows[0].find("th") else None
    body = rows[1:] if head else rows
    if cols < 2 or len(body) < cols * 2:
        return table_html
    per = -(-len(body) // cols)                      # ceil
    chunks = [body[i * per:(i + 1) * per] for i in range(cols)]
    ncell = max(len(r.find_all(["td", "th"])) for r in body)
    out = ['<table>']
    if head:
        hcells = "".join(str(c) for c in head.find_all(["th", "td"]))
        out.append("<tr>" + hcells * cols + "</tr>")
    for i in range(per):
        cells = []
        for ch in chunks:
            if i < len(ch):
                cs = ch[i].find_all(["td", "th"])
                cells.append("".join(str(c) for c in cs))
                cells.append("<td></td>" * (ncell - len(cs)))
            else:
                cells.append("<td></td>" * ncell)
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</table>")
    return "".join(out)

def extract(page, which="all", max_rows=None, only=None):
    p = os.path.join(SITE, page, "index.html")
    soup = BeautifulSoup(open(p, encoding="utf-8").read(), "html.parser")
    out, used = [], 0
    cand = [t for t in soup.find_all("table") if len(t.find_all("tr")) >= 3]
    if only is not None:
        cand = [t for i, t in enumerate(cand) if i in only]
    for tb in cand:
        rows = tb.find_all("tr")
        if len(rows) < 3:
            continue
        # nearest preceding heading gives the group its name
        h = tb.find_previous(["h2", "h3"])
        cap = h.get_text(" ", strip=True) if h else ""
        cap = re.sub(r"\s+", " ", cap)[:44]
        if max_rows and used >= max_rows:
            break
        keep = rows if not max_rows else rows[: max(3, max_rows - used)]
        used += len(keep) - 1
        tb2 = BeautifulSoup(str(tb), "html.parser").find("table")
        allr = tb2.find_all("tr")
        for extra in allr[len(keep):]:
            extra.decompose()
        for a in tb2.find_all("a"):
            a.replace_with(a.get_text())
        for bad in tb2.find_all(["button", "audio", "svg", "script"]):
            bad.decompose()
        # Drop on-page interactive columns (the 「會了」 tick boxes). They mean nothing
        # in a static chart and cost a third of the width on a reflowed list.
        allrows = tb2.find_all("tr")
        if allrows:
            drop = set()
            for r in allrows:
                for i, c in enumerate(r.find_all(["td", "th"])):
                    txt = c.get_text(" ", strip=True)
                    if c.find("input") or txt in ("會了", "☐", ""):
                        if any(rr.find_all(["td", "th"]) and
                               (rr.find_all(["td", "th"])[i].find("input") if
                                i < len(rr.find_all(["td", "th"])) else False)
                               for rr in allrows[1:3] or allrows):
                            drop.add(i)
            for r in allrows:
                cs = r.find_all(["td", "th"])
                for i in sorted(drop, reverse=True):
                    if i < len(cs):
                        cs[i].decompose()
        out.append((cap, str(tb2)))
    return out

def build(slug, spec):
    groups = extract(spec["page"], spec.get("tables", "all"),
                     spec.get("max_rows"), spec.get("only"))
    if not groups:
        print(f"  !! {slug}: no tables found on /{spec['page']}/")
        return None
    cols = spec.get("cols", 1)
    W = spec.get("width", 1200)
    body = "\n".join(
        f'<div class="grp">{f"<h2>{html.escape(c)}</h2>" if c else ""}{reflow(t, cols)}</div>'
        for c, t in groups)
    import base64
    lp = os.path.join(SITE, "assets/img/american-english-banqiao-logo.jpg")
    logo = "data:image/jpeg;base64," + base64.b64encode(open(lp, "rb").read()).decode()
    doc = f"""<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@700;800&family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&display=swap" rel="stylesheet">
<style>{CSS.replace("__W__", str(W))}</style></head><body><div class="card">
<div class="head"><h1>{html.escape(spec['title'])}</h1><p>{html.escape(spec['sub'])}</p></div>
<div class="bar"></div>
<div class="body {'c3' if cols>=3 else ''}">{body}</div>
<div class="foot">
  <div class="brand"><img src="{logo}" alt="">
    <div><div class="n">埃森美語 American English</div>
    <div class="u">americanenglish.com.tw</div></div></div>
  <div class="tag">{html.escape(spec['foot'])}</div>
</div></div></body></html>"""
    os.makedirs(OUT, exist_ok=True)
    png = os.path.join(OUT, slug + ".png")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": 1000}, device_scale_factor=1)
        pg.set_content(doc, wait_until="networkidle")
        pg.wait_for_timeout(700)          # webfonts
        pg.locator(".card").screenshot(path=png)
        b.close()
    h = 0
    try:
        from PIL import Image
        with Image.open(png) as im: w, h = im.size
    except Exception: w = W
    print(f"  {slug}.png  {w}x{h}  ({len(groups)} tables)")
    return dict(slug=slug, png=f"/assets/img/charts/{slug}.png", w=w, h=h,
                alt=spec["alt"], title=spec["title"], page=spec["page"])

FIG_CSS_HOOK = "chart-fig"

def inject(rec):
    """Put the chart on its page inside an AE:CHART block, before the first table,
    with ImageObject JSON-LD. Re-running replaces the block rather than stacking."""
    fp = os.path.join(SITE, rec["page"], "index.html")
    src = open(fp, encoding="utf-8").read()
    tag = rec["slug"]
    startm, endm = f"<!-- AE:CHART {tag} start -->", f"<!-- AE:CHART {tag} end -->"
    cap = f'{rec["title"]}——可儲存或列印｜埃森美語 americanenglish.com.tw'
    ld = {"@context": "https://schema.org", "@type": "ImageObject",
          "contentUrl": ORIGIN + rec["png"], "url": ORIGIN + rec["png"],
          "width": rec["w"], "height": rec["h"],
          "caption": rec["alt"], "name": rec["title"],
          "creditText": "American English 埃森美語",
          "creator": {"@type": "Organization", "name": "American English 埃森美語"},
          "license": ORIGIN + "/", "acquireLicensePage": ORIGIN + f'/{rec["page"]}/'}
    block = (f'{startm}\n'
             f'<figure class="{FIG_CSS_HOOK}">\n'
             f'  <img src="{rec["png"]}" width="{rec["w"]}" height="{rec["h"]}"\n'
             f'       alt="{html.escape(rec["alt"], quote=True)}" loading="lazy" decoding="async">\n'
             f'  <figcaption>{html.escape(cap)}</figcaption>\n'
             f'</figure>\n'
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>\n'
             f'{endm}\n')
    if startm in src:
        new = re.sub(re.escape(startm) + r".*?" + re.escape(endm) + r"\n?", block, src, flags=re.S)
        act = "replaced"
    else:
        nth = rec.get("anchor_nth", 0)
        ms = list(re.finditer(r"([ \t]*)<table", src))
        m = ms[nth] if nth < len(ms) else (ms[0] if ms else None)
        if not m:
            print(f"  !! {rec['page']}: no <table> to anchor to"); return False
        indent = m.group(1)
        new = src[:m.start()] + "".join(indent + l + "\n" for l in block.rstrip().split("\n")) + src[m.start():]
        act = "inserted"
    if new != src:
        open(fp, "w", encoding="utf-8").write(new)
    print(f"     -> /{rec['page']}/ chart block {act}")
    return True

if __name__ == "__main__":
    want = sys.argv[1:] or list(SPECS)
    man = {}
    mf = os.path.join(OUT, "manifest.json")
    if os.path.exists(mf):
        man = json.load(open(mf, encoding="utf-8"))
    for s in want:
        if s not in SPECS:
            print(f"  ?? unknown slug {s}"); continue
        r = build(s, SPECS[s])
        if r:
            man[s] = r
            inject(r)
    os.makedirs(OUT, exist_ok=True)
    json.dump(man, open(mf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"manifest: {len(man)} charts -> assets/img/charts/manifest.json")
