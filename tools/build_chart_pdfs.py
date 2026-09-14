#!/usr/bin/env python3
"""
A4 print versions of the reference tables.

Why: of the ten pages currently holding the top spots across these pools, exactly
zero offer a single downloadable file. Downloads are the one asset class this site
is alone in — and a table taped above a desk gets seen every day, which a web page
does not. Every chart should therefore have a print twin.

Shares the extraction, reflow and column-dropping logic of build_chart_images.py so
a PDF can never disagree with the chart or the page it came from.

Usage:  python3 tools/build_chart_pdfs.py [slug ...]
"""
import os, re, sys, json, html, base64, importlib.util

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(SITE, "assets/downloads")

spec = importlib.util.spec_from_file_location(
    "bci", os.path.join(SITE, "tools/build_chart_images.py"))
bci = importlib.util.module_from_spec(spec); spec.loader.exec_module(bci)

# slug -> (chart spec key, output filename, printed subtitle)
PDFS = {
 "numbers-1-100-english":  ("numbers-1-100-chart",  "ae-numbers-1-100-a4.pdf",  "0 到 100 完整拼法對照"),
 "months-english":         ("months-english-chart", "ae-months-english-a4.pdf", "1-12 月英文、縮寫與天數"),
 "days-of-week-english":   ("days-week-english-chart","ae-days-of-week-a4.pdf", "星期英文、縮寫與口語說法"),
 "countries-english":      ("countries-english-chart","ae-countries-english-a4.pdf","80 國國名與國籍形容詞"),
 "jobs-english":           ("jobs-english-chart",   "ae-jobs-english-a4.pdf",   "83 種職業英文對照"),
 "body-parts-english":     ("body-parts-english-chart","ae-body-parts-a4.pdf",   "43 個身體部位英文對照"),
 "english-abbreviations-guide":  ("english-abbreviations-chart","ae-english-abbreviations-a4.pdf","74 個常用英文縮寫與全名"),
 "thank-you-english":      ("thank-you-english-chart","ae-thank-you-english-a4.pdf","30 種道謝說法與適用場合"),
 "cheer-up-english":       ("cheer-up-english-chart","ae-cheer-up-english-a4.pdf","21 種鼓勵說法依場合分組"),
 "english-pronunciation":  ("english-vowels-chart", "ae-english-vowels-a4.pdf", "17 個母音・例字與嘴型提示"),
}

CSS = """
@page{size:A4 portrait;margin:11mm 10mm 13mm}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans','PingFang TC','Noto Sans TC','Microsoft JhengHei',sans-serif;color:#26324d}
.head{border-bottom:3px solid #1CB0F6;padding-bottom:7px;margin-bottom:11px;
  display:flex;align-items:flex-end;justify-content:space-between;gap:12px}
.head h1{font-family:'DM Serif Display',Georgia,serif;font-size:20pt;color:#1A2752;font-weight:400;line-height:1.15}
.head p{font-size:9pt;color:#64748b;margin-top:3px}
.head .br{display:flex;align-items:center;gap:6px;white-space:nowrap}
.head .br img{width:26px;height:26px;border-radius:50%}
.head .br span{font-size:8pt;color:#64748b;line-height:1.3}
.head .br b{display:block;font-size:9pt;color:#1A2752}
h2{font-family:'DM Serif Display',Georgia,serif;font-size:12pt;color:#1A2752;font-weight:400;
  margin:9px 0 5px;padding-left:7px;border-left:3px solid #1CB0F6;break-after:avoid}
table{border-collapse:collapse;width:100%;font-size:8.6pt;margin-bottom:7px}
th{background:#DDF4FF;color:#1A2752;text-align:left;padding:4px 6px;font-size:7.8pt;
  border-bottom:1.4px solid #1CB0F6}
td{padding:3.4px 6px;border-bottom:.6px solid #e8eef7;vertical-align:middle}
td:first-child{font-weight:700;color:#1A2752}
tr:nth-child(even) td{background:#fafcff}
tr{break-inside:avoid}
.foot{position:fixed;bottom:0;left:0;right:0;font-size:7pt;color:#94a3b8;
  border-top:.6px solid #e8eef7;padding-top:3px;display:flex;justify-content:space-between}
"""

def build(page, chart_key, fname, sub):
    cs = bci.SPECS.get(chart_key)
    if not cs:
        print(f"  ?? no chart spec {chart_key}"); return None
    groups = bci.extract(cs["page"], cs.get("tables", "all"),
                         cs.get("max_rows"), cs.get("only"))
    if not groups:
        print(f"  !! {page}: no tables"); return None
    cols = cs.get("cols", 1)
    # a single-group PDF already says what it is in the header — don't repeat it
    one = len(groups) == 1
    body = "\n".join(
        f'{"" if one else (f"<h2>{html.escape(c)}</h2>" if c else "")}{bci.reflow(t, cols)}'
        for c, t in groups)
    lp = os.path.join(SITE, "assets/img/american-english-banqiao-logo.jpg")
    logo = "data:image/jpeg;base64," + base64.b64encode(open(lp, "rb").read()).decode()
    doc = f"""<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=DM+Serif+Display&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="head"><div><h1>{html.escape(cs['title'])}</h1><p>{html.escape(sub)}</p></div>
<div class="br"><img src="{logo}" alt=""><span><b>埃森美語</b>americanenglish.com.tw</span></div></div>
{body}
<div class="foot"><span>埃森美語 American English・板橋</span>
<span>歡迎影印給學生使用，請保留此頁出處 americanenglish.com.tw/chart-license/</span></div>
</body></html>"""
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, fname)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page()
        pg.set_content(doc, wait_until="networkidle"); pg.wait_for_timeout(600)
        pg.pdf(path=path, format="A4", print_background=True)
        b.close()
    kb = os.path.getsize(path) / 1024
    print(f"  {fname}  {kb:.0f}KB")
    return fname

MAGNET = ('<div class="magnet-box reveal">\n'
 '  <p><strong>📄 免費下載：{title}（A4 列印版）</strong><br>{sub}'
 '——直接下載，印出來貼在書桌前，每天看一眼比坐下來背一次有用。</p>\n'
 '  <a class="btn btn-primary" download href="/assets/downloads/{fname}">免費下載 PDF</a>\n'
 '</div>')

def offer(page, title, sub, fname):
    fp = os.path.join(SITE, page, "index.html")
    s = open(fp, encoding="utf-8").read()
    if fname in s:
        return "already linked"
    blk = MAGNET.format(title=title, sub=sub, fname=fname)
    m = re.search(r'([ \t]*)<figure class="chart-fig">', s)
    if not m:
        return "no chart anchor"
    ind = m.group(1)
    s = s[:m.start()] + "".join(ind + l + "\n" for l in blk.split("\n")) + s[m.start():]
    open(fp, "w", encoding="utf-8").write(s)
    return "offer added"

# Topics that already have a printable from the earlier workbook set — link, don't rebuild.
EXISTING = {
 "colors-english-vocabulary": ("顏色英文閃卡", "62 個顏色的中英對照與閃卡", "ae-colors-flashcards-a4.pdf"),
 "fruits-english": ("水果英文閃卡", "常見水果的中英對照與閃卡", "ae-fruits-flashcards-a4.pdf"),
 "animals-english-vocabulary": ("動物英文閃卡", "常見動物的中英對照與閃卡", "ae-animals-flashcards-a4.pdf"),
}

if __name__ == "__main__":
    want = sys.argv[1:] or list(PDFS)
    for page in want:
        if page not in PDFS:
            print(f"  ?? unknown {page}"); continue
        ck, fn, sub = PDFS[page]
        f = build(page, ck, fn, sub)
        if f:
            print(f"     -> /{page}/ {offer(page, bci.SPECS[ck]['title'], sub, fn)}")
    for page, (title, sub, fn) in EXISTING.items():
        if not os.path.exists(os.path.join(OUT, fn)):
            print(f"  !! missing {fn}"); continue
        print(f"  link  /{page}/ -> {fn}: {offer(page, title, sub, fn)}")
