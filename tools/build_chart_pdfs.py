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
 "english-numbers-guide":  ("english-numbers-chart",  "ae-numbers-1-100-a4.pdf",  "0 到 100 完整拼法對照"),
 "months-english":         ("months-english-chart", "ae-months-english-a4.pdf", "1-12 月英文、縮寫與天數"),
 "days-of-week-english":   ("days-week-english-chart","ae-days-of-week-a4.pdf", "星期英文、縮寫與口語說法"),
 "countries-english":      ("countries-english-chart","ae-countries-english-a4.pdf","80 國國名與國籍形容詞"),
 "jobs-english":           ("jobs-english-chart",   "ae-jobs-english-a4.pdf",   "108 種職業英文對照"),
 "body-parts-english":     ("body-parts-english-chart","ae-body-parts-a4.pdf",   "43 個身體部位英文對照"),
 "english-abbreviations-guide":  ("english-abbreviations-chart","ae-english-abbreviations-a4.pdf","74 個常用英文縮寫與全名"),
 "thank-you-english":      ("thank-you-english-chart","ae-thank-you-english-a4.pdf","30 種道謝說法與適用場合"),
 "cheer-up-english":       ("cheer-up-english-chart","ae-cheer-up-english-a4.pdf","21 種鼓勵說法依場合分組"),
 "english-pronunciation":  ("english-vowels-chart", "ae-english-vowels-a4.pdf", "17 個母音・例字與嘴型提示"),
 "english-pronunciation#consonants": ("english-consonants-chart", "ae-english-consonants-a4.pdf", "24 個子音・有聲無聲配對與發音位置"),
 "english-vowels-consonants": ("english-vowels-consonants-chart", "ae-vowels-consonants-a4.pdf", "母音、子音、長短母音與雙母音對照"),
 # 2026-09-21: the pages carrying the most impressions at the worst CTR on the site —
 # each already ranked 6–7, each with a chart and no download. GSC says the shapes that
 # convert here are "get a file" (8.99% CTR) and "look up" (7.45%), against 0.77% for
 # anything Google answers inside the SERP. Names got both genders: 女生英文名 sits at 9.1
 # while the boys page holds 4.5, and the girls table is all but the same size.
 "english-alphabet-guide":  ("english-alphabet-chart",    "ae-english-alphabet-a4.pdf",    "26 個字母大小寫與發音對照"),
 "ordinal-numbers-english": ("ordinal-numbers-chart",     "ae-ordinal-numbers-a4.pdf",     "序數拼法、縮寫與唸法"),
 "happy-birthday-english":  ("happy-birthday-chart",      "ae-happy-birthday-a4.pdf",      "生日祝福說法與適用對象"),
 "mid-autumn-festival-english": ("mid-autumn-chart",      "ae-mid-autumn-english-a4.pdf",  "中秋節英文說法與節慶單字"),
 "halloween-english":       ("halloween-chart",           "ae-halloween-english-a4.pdf",   "萬聖節英文祝福與單字表"),
 "christmas-english":       ("christmas-chart",           "ae-christmas-english-a4.pdf",   "聖誕節英文祝福與單字表"),
 "valentines-day-english":  ("valentines-day-chart",      "ae-valentines-day-english-a4.pdf", "情人節英文祝福與單字表"),
 "weather-english":         ("weather-english-chart",     "ae-weather-english-a4.pdf",     "天氣英文單字表與學習單"),
 "sports-english":          ("sports-english-chart",      "ae-sports-english-a4.pdf",      "運動英文單字表與學習單"),
 "feelings-english":        ("feelings-english-chart",    "ae-feelings-english-a4.pdf",    "72 個情緒與感覺形容詞・附 KK 音標"),
 "junior-high-english-grammar": ("junior-high-english-grammar-chart", "ae-junior-high-grammar-a4.pdf", "國一到國三 36 個文法重點・句型與例句"),
 "english-plural-nouns":    ("english-plural-nouns-all",  "ae-english-plurals-a4.pdf",     "142 個單複數對照・加 s、es、ies、ves 與不規則複數"),
 "school-grades-english":   ("school-grades-english-chart","ae-school-grades-english-a4.pdf","台灣、美國、英國年級與年齡對照"),
 "english-wishes":          ("english-wishes-all",        "ae-english-wishes-a4.pdf",      "13 種場合 180 句英文祝福語・附適合對象與語氣"),
 "english-card-writing":    ("english-card-writing-chart","ae-english-card-writing-a4.pdf","41 個卡片開頭、結尾、署名寫法與適合對象"),
 "time-english":            ("time-english-chart",        "ae-time-english-a4.pdf",        "時間英文幾點幾分說法對照表"),
 "thanksgiving-english":      ("thanksgiving-english-all", "ae-thanksgiving-english-a4.pdf", "感恩節英文 60 句・附對象與語氣"),
 "mothers-day-english":       ("mothers-day-english-all", "ae-mothers-day-english-a4.pdf", "母親節快樂英文 60 句・附誰寫的與語氣"),
 "dragon-boat-festival-english": ("dragon-boat-festival-english-all", "ae-dragon-boat-festival-english-a4.pdf", "端午節英文名稱、祝福語與基本句"),
 "lantern-festival-english":  ("lantern-festival-english-all", "ae-lantern-festival-english-a4.pdf", "元宵節英文 60 句・祝福語、活動、湯圓與燈會"),
 "red-envelope-english":      ("red-envelope-english-all", "ae-red-envelope-english-a4.pdf", "紅包英文 60 句・給紅包、收紅包、恭喜發財"),
 "chinese-zodiac-english":    ("chinese-zodiac-english-all", "ae-chinese-zodiac-english-a4.pdf", "十二生肖英文、年份與個性形容詞"),
 "earthquake-english":        ("earthquake-english-all", "ae-earthquake-english-a4.pdf", "地震英文 58 個單字・餘震、震央、規模與震度"),
 "good-morning-english":      ("good-morning-english-all", "ae-good-morning-english-a4.pdf", "早安英文 50 句・附對象與語氣"),
 "good-night-english":        ("good-night-english-all", "ae-good-night-english-a4.pdf", "晚安英文 50 句・附對象與語氣"),
 "zodiac-signs-english":      ("zodiac-signs-english-all", "ae-zodiac-signs-english-a4.pdf", "12 星座英文、日期、個性形容詞與 24 句"),
 "bubble-tea-english":        ("bubble-tea-english-all", "ae-bubble-tea-english-a4.pdf", "手搖飲英文菜單 50 種・甜度冰塊配料怎麼點"),
 "typhoon-english":           ("typhoon-english-all", "ae-typhoon-english-a4.pdf", "颱風英文・颱風假、停班停課、警報與防颱單字"),
 "basketball-english":        ("basketball-english-all", "ae-basketball-english-a4.pdf", "位置・動作與術語・球場・裝備・球季與比賽・共 81 項"),
 "soccer-english":            ("soccer-english-all", "ae-soccer-english-a4.pdf", "位置與人物・動作與進攻・規則與判罰・球場・裝備・共 78 項"),
 "tennis-english":            ("tennis-english-all", "ae-tennis-english-a4.pdf", "計分・擊球・球場・裝備・共 65 項"),
 "swimming-english":          ("swimming-english-all", "ae-swimming-english-a4.pdf", "四種泳式・基本動作・泳池與用品・游泳課、程度與檢定・泳池安全・共 80 項"),
 "school-subjects-english":   ("school-subjects-english-all", "ae-school-subjects-english-a4.pdf", "國小・國中・高中・美國學校才有的名稱・共 55 項"),
 "math-english":              ("math-english-all", "ae-math-english-a4.pdf", "運算與符號・分數、小數、平方・圖形與幾何・測量與單位・數學概念・共 77 項"),
 "science-english":           ("science-english-all", "ae-science-english-a4.pdf", "生物・物質三態・力與能量・地球與太空・太陽系八大行星・共 90 項"),
 "social-studies-english":    ("social-studies-english-all", "ae-social-studies-english-a4.pdf", "社區與家庭・地理・歷史・公民與政府・經濟・共 68 項"),
 "music-english":             ("music-english-all", "ae-music-english-a4.pdf", "樂器・看譜・演奏與演唱・音樂類型與聽音樂・共 77 項"),
 "airport-english":           ("airport-english-all", "ae-airport-english-a4.pdf", "出發前・報到櫃台・安檢・出境、入境・海關・共 74 項"),
 "travel-english":            ("travel-english-all", "ae-travel-english-a4.pdf", "飯店・交通與問路・餐廳・購物・景點・共 70 項"),
 "ordering-food-english":     ("ordering-food-english-all", "ae-ordering-food-english-a4.pdf", "菜單上的分區・點餐與結帳・內用、外帶、外送・怎麼做、加什麼、不要什麼・速食店・共 73 項"),
 "shopping-english":          ("shopping-english-all", "ae-shopping-english-a4.pdf", "店裡・商店種類・孩子會買的東西・網購・共 80 項"),
 "leave-note-english":        ("leave-note-english-all", "ae-leave-note-english-a4.pdf", "假別・請假的動詞・請假的原因・學校裡的字・上班用的字・共 63 項"),
 "chinglish-english":         ("chinglish-english-all", "ae-chinglish-english-a4.pdf", "美國老師最常聽到的兩句・逐字翻譯・文法照中文・單字混用・發音帶出來的・共 66 項"),
 "festivals-english":         ("festivals-english-all", "ae-festivals-english-a4.pdf", "國定假日・傳統節慶與紀念日・學校的假期・台灣孩子知道的西洋節日・共 44 項"),
 "fathers-day-english":       ("fathers-day-english-all", "ae-fathers-day-english-a4.pdf", "孩子寫給爸爸・國高中生、大人寫給爸爸・寫給爺爺、外公・太太寫給先生・全家人的卡片・共 50 項"),
 "teachers-day-english":      ("teachers-day-english-all", "ae-teachers-day-english-a4.pdf", "國小生寫給老師・國中生寫給老師・畢業生寫給老師・家長寫給老師・寫給外師・共 50 項"),
 "baseball-english":          ("baseball-english-all", "ae-baseball-english-a4.pdf", "守備位置與場上的人・打擊與跑壘・投球與球數・球場與裝備・共 87 項"),
 "icrt-english-radio":        ("icrt-english-radio-all", "ae-icrt-english-radio-a4.pdf", "電台用語・新聞用語・DJ・音樂用語・共 70 項"),
 "chinese-name-to-english":   ("chinese-name-to-english-all", "ae-chinese-name-to-english-a4.pdf", "兩種拼法相同的姓・台灣慣用威妥瑪式、和漢語拼音不同的姓・複姓・共 103 項"),
 "english-name-generator":    ("english-name-generator-all", "ae-english-name-generator-a4.pdf", "最常見的・其他名字常用字・共 68 項"),
 "learn-english-cartoons":    ("learn-english-cartoons-all", "ae-learn-english-cartoons-a4.pdf", "2–4・4–6・6–9・9–12・國中・共 66 項"),
 "afraid-to-speak-english":   ("afraid-to-speak-english-all", "ae-afraid-to-speak-english-a4.pdf", "跟老師打招呼・上課需要幫忙・聽不懂時・問英文怎麼說・買東西・共 72 項"),
 "how-to-learn-english":      ("how-to-learn-english-all", "ae-how-to-learn-english-a4.pdf", "聽力・口說・閱讀・寫作・單字・共 64 項"),
 "english-address":         ("english-address-all",       "ae-english-address-a4.pdf",     "地址單位縮寫・22 縣市・新北與臺北各區英譯"),
 "food-english":            ("food-english-chart",        "ae-food-english-a4.pdf",        "台灣小吃英文對照表（58 道）"),
 "new-year-english":        ("new-year-chart",            "ae-new-year-english-a4.pdf",    "新年快樂英文祝福與過年單字表"),
 "english-names-boys":      ("english-names-boys-chart",  "ae-english-names-boys-a4.pdf",  "男生英文名字、唸法與含意"),
 "english-names-girls":     ("english-names-girls-chart", "ae-english-names-girls-a4.pdf", "女生英文名字、唸法與含意"),
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

def stamp_meta(path, title, sub):
    """Title/Author/Subject in the PDF itself: 23 of the A4 downloads had none (Chromium names a PDF
    after <title>, and the template had no <title>), and an untitled PDF shows in Google as its file
    name. Metadata only — the page content stream is copied as is."""
    from pypdf import PdfReader, PdfWriter
    r = PdfReader(path)
    w = PdfWriter(clone_from=r)
    meta = {k: v for k, v in (r.metadata or {}).items()}
    meta.update({"/Title": f"{title}｜埃森美語", "/Author": "埃森美語 American English",
                 "/Subject": sub, "/Creator": "americanenglish.com.tw"})
    w.add_metadata(meta)
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        w.write(fh)
    os.replace(tmp, path)


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
<title>{html.escape(cs['title'])}｜埃森美語</title>
<style>{CSS}{cs.get("css", "")}</style></head><body>
<div class="head"><div><h1>{html.escape(cs['title'])}</h1><p>{html.escape(sub)}</p></div>
<div class="br"><img src="{logo}" alt=""><span><b>埃森美語</b>americanenglish.com.tw</span></div></div>
{body}
<div class="foot"><span>埃森美語 American English・板橋</span>
<span>歡迎影印給學生使用，請保留此頁出處 americanenglish.com.tw/chart-license/</span></div>
</body></html>"""
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, fname)
    old = open(path, "rb").read() if os.path.exists(path) else None
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page()
        pg.set_content(doc, wait_until="networkidle"); pg.wait_for_timeout(600)
        pg.pdf(path=path, format="A4", print_background=True)
        b.close()
    stamp_meta(path, cs["title"], sub)
    # Chromium stamps the time into every PDF (/CreationDate, /ModDate): when nothing else changed,
    # keep the old file, so a rerun does not rewrite 23 PDFs (and backfill_lastmod does not re-date them)
    if old is not None:
        stamp = lambda x: re.sub(rb"/(CreationDate|ModDate) ?\(D:[^)]*\)", b"", x)
        if stamp(open(path, "rb").read()) == stamp(old):
            open(path, "wb").write(old)
    kb = os.path.getsize(path) / 1024
    print(f"  {fname}  {kb:.0f}KB")
    return fname

MAGNET = """<div class="magnet-box reveal">
  <p><strong>📄 免費下載：{title}（A4 列印版）</strong><br>{sub}——直接下載，印出來貼在書桌前，每天看一眼比坐下來背一次有用。</p>
  <a class="btn btn-primary" download href="/assets/downloads/{fname}" onclick="window.gtag&amp;&amp;gtag('event','pdf_download',{{file:'{fname}',page_path:location.pathname}})">免費下載 PDF</a>
</div>"""

def offer(page, title, sub, fname, chart_key=None):
    fp = os.path.join(SITE, page, "index.html")
    s = open(fp, encoding="utf-8").read()
    if fname in s:
        return "already linked"
    blk = MAGNET.format(title=title, sub=sub, fname=fname)
    # a page with two charts (pronunciation: vowels + consonants) gets each box at its own chart
    at = s.find(f"<!-- AE:CHART {chart_key} start -->") if chart_key else -1
    m = re.compile(r'([ \t]*)<figure class="chart-fig">').search(s, max(at, 0))
    if not m:
        return "no chart anchor"
    ind = m.group(1)
    s = s[:m.start()] + "".join(ind + l + "\n" for l in blk.split("\n")) + s[m.start():]
    open(fp, "w", encoding="utf-8").write(s)
    return "offer added"

# Topics that already have a printable from the earlier workbook set — link, don't rebuild.
EXISTING = {
 "colors-english-vocabulary": ("顏色英文閃卡", "62 個顏色的中英對照與閃卡", "ae-colors-flashcards-a4.pdf"),
 "fruits-english-vocabulary": ("水果英文閃卡", "常見水果的中英對照與閃卡", "ae-fruits-flashcards-a4.pdf"),
 "animals-english-vocabulary": ("動物英文閃卡", "常見動物的中英對照與閃卡", "ae-animals-flashcards-a4.pdf"),
}

if __name__ == "__main__":
    if "--meta-only" in sys.argv:          # title/author/subject into the existing files, no re-render
        for page, (ck, fn, sub) in PDFS.items():
            p = os.path.join(OUT, fn)
            if os.path.exists(p) and ck in bci.SPECS:
                stamp_meta(p, bci.SPECS[ck]["title"], sub)
                print(f"  meta  {fn}")
        sys.exit(0)
    want = sys.argv[1:] or list(PDFS)
    for page in want:
        if page not in PDFS:
            print(f"  ?? unknown {page}"); continue
        ck, fn, sub = PDFS[page]
        f = build(page, ck, fn, sub)
        if f:      # "page#suffix" keys: a second PDF on the same page
            print(f"     -> /{page}/ {offer(page.split('#')[0], bci.SPECS[ck]['title'], sub, fn, ck)}")
    for page, (title, sub, fn) in EXISTING.items():
        if not os.path.exists(os.path.join(OUT, fn)):
            print(f"  !! missing {fn}"); continue
        print(f"  link  /{page}/ -> {fn}: {offer(page, title, sub, fn)}")
