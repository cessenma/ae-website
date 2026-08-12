#!/usr/bin/env python3
"""Generate /banqiao-school-calendar/ from data/school-calendars.json.

Design rules, all driven by one risk: a wrong 段考 date on a cram school's website is worse
than no calendar at all.

  · every school links to its own official source, right next to its dates
  · the page states when it was last checked, from the actual run
  · the schools' own disclaimer is reproduced — their notice always wins
  · a school that publishes its calendar as an image is LINKED, never OCR'd
  · a school that has not yet published next semester shows "尚未公布", not stale dates
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "school-calendars.json")
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "exams", "banqiao-school-calendar", "index.html")
TPE = timezone(timedelta(hours=8))

KIND_COLOR = {"段考": "#d97a5c", "定期評量": "#d97a5c", "開學": "#06C755",
              "休業式": "#1CB0F6", "寒暑假": "#1CB0F6", "校慶": "#FFC828", "親師": "#1391cc"}


def rows(events):
    out = []
    for e in events:
        c = KIND_COLOR.get(e["kind"], "#94a3b8")
        d = f"{e['month']}/{e['day']}"
        out.append(
            f'<tr><td style="white-space:nowrap"><strong>{d}</strong></td>'
            f'<td><span style="display:inline-block;padding:1px 9px;border-radius:99px;'
            f'background:{c};color:#fff;font-size:12px">{e["kind"]}</span></td>'
            f'<td>{e["label"]}</td></tr>')
    return "".join(out)


def school_block(s):
    name, full = s["name"], s.get("full", s["name"])
    walk = s.get("walk", "")
    src = s.get("calendar_page") or s["home"]
    status = "✅ 連線正常" if s.get("link_ok") else f"⚠️ 連線異常（HTTP {s.get('http')}）"
    note = f'<p style="font-size:13px;color:#94a3b8">{s["note"]}</p>' if s.get("note") else ""
    body = ""
    if s.get("events"):
        body = ('<table class="compare"><thead><tr><th style="width:16%">日期</th>'
                '<th style="width:18%">類別</th><th>項目</th></tr></thead>'
                f'<tbody>{rows(s["events"])}</tbody></table>')
    return (f'<h2>{full}（{name}）</h2>'
            f'<p style="margin:0 0 6px"><strong>{walk}</strong>　·　'
            f'<a href="{src}" target="_blank" rel="noopener nofollow">前往學校官方行事曆 →</a></p>'
            f'{note}{body}'
            f'<p style="font-size:12px;color:#94a3b8;margin:0 0 18px">本週檢查：{status}</p>')


def main():
    if not os.path.exists(DATA):
        print("no data file — run school_calendars.py first")
        return 1
    d = json.load(open(DATA, encoding="utf-8"))
    checked = d.get("checked_at", "")
    blocks = "\n".join(school_block(s) for s in d["schools"])
    n_exam = sum(1 for s in d["schools"] for e in s.get("events", []) if e["kind"] == "段考")
    names = "、".join(s["name"] for s in d["schools"])

    html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>板橋學區行事曆總覽：{names}官方連結｜埃森美語</title>
<meta name="description" content="板橋 {names} 四校官方行事曆的所在位置，每週自動檢查連結是否有效。本頁不轉錄段考日期，直接連到學校官方公告，避免辨識錯誤。最後檢查：{checked}。">
<link rel="canonical" href="https://americanenglish.com.tw/exams/banqiao-school-calendar/">
<meta property="og:type" content="article">
<meta property="og:title" content="板橋學區行事曆總覽：四校官方連結">
<meta property="og:description" content="步行可達的四所學校，官方行事曆一頁找齊，每週自動檢查。">
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<main id="top">

<section class="page-hero">
  <div class="bg-deco"></div>
  <div class="wrap">
    <div class="breadcrumb reveal"><a href="/">首頁</a> ／ <a href="/blog/">部落格</a> ／ 板橋學區行事曆</div>
    <span class="eyebrow eyebrow-green reveal">在地資源 · 每週更新</span>
    <h1 class="reveal d1"><em>板橋學區行事曆</em><br>四校官方連結，一頁找齊</h1>
    <div class="divider reveal d1"></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="prose reveal">
      <p style="font-size:13px;line-height:1.7;color:#94a3b8;margin-bottom:14px">
        由埃森美語整理自各校官方行事曆　·　最後檢查：<strong>{checked}</strong>　·　每週自動檢查更新</p>

      <div style="background:#FFF9E6;border:1px solid #FFC828;border-radius:10px;padding:14px 18px;margin:0 0 22px">
        <p style="margin:0;font-size:14px"><strong>請以學校公告為準。</strong>
        各校行事曆均註明「如有調整，以校網及各處室通知或公告為主」，部分項目標示「暫訂」。
        本頁為方便家長快速查閱而整理，安排重要事項前請再確認學校最新公告。</p>
      </div>

      <h2>四所學校的官方行事曆在哪裡</h2>
      <p>板橋 {names} 各自把行事曆放在校網不同的位置，格式也不一樣——有的是 PDF，有的是圖片公告。
      埃森美語每週自動檢查這四個官方頁面是否還能連線、位置有沒有變動，讓家長不必每次重新找。</p>
      <p><strong>本頁不轉錄各校的段考日期。</strong>部分學校以圖片公告行事曆，辨識容易出錯，
      而一個錯的段考日期比沒有日期更糟。請點各校連結查看官方版本。</p>

      {blocks}

      <h2>為什麼段考日期值得先記下來？</h2>
      <p>段考前兩週是複習期，臨時抱佛腳的效果有限。埃森美語建議家長在學期一開始就把三次段考的日期標在行事曆上，
      往前推兩週安排複習，比考前一週才開始有效得多。國中英文的段考範圍通常涵蓋 2–3 個單元，
      不是靠考前衝刺能補回來的。</p>
      <p>想知道各校段考題型與歷屆考古題怎麼找，可以參考
      <a href="/banqiao-junior-high-english-past-papers/">板橋國中英文考古題哪裡下載</a>；
      國中英文常見的失分點整理在
      <a href="/banqiao-junior-high-english-blind-spots/">國中英文最容易失分的地方</a>。</p>
    </div>
  </div>
</section>

</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(html)
    print(f"  wrote {OUT}")
    print(f"  {len(d['schools'])} schools · {n_exam} 段考 entries · checked {checked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
