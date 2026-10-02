#!/usr/bin/env python3
"""AE:REGION blocks — the closing box on the busiest free reference pages, split by where
the reader lives.

Why (GA4 2026-08-01→10-02): 237 of 18,543 visitors tapped a LINE button. /courses/ turns
10.4% of its visitors into a tap; the reference pages turn 0.4–1.2% on ~10,000 visitors.
About 70% of the reference pages' readers, and half of everyone who taps LINE, are outside
Taipei / New Taipei — and every closing box offered them an assessment in a Banqiao classroom.
So the box now asks one question and gives each answer something it can use:
  住雙北   → the free assessment over LINE, and the course overview (/courses/)
  不在雙北 → the full mock papers, Cambridge or GEPT (bought online, sent by email)

One block per page. On the pages that carried the hand-written "這些教材，就是我每天上課用的"
box, the block replaces it; elsewhere it goes right before the byline / </main>. Re-runnable;
this script owns every <!-- AE:REGION --> block. Run tools/seo_build.py afterwards.

Clicks are counted in assets/app.js: the LINE button as line_tap with cta_position
"region_local", the other three links as region_cta_click with a `choice`
(local_courses / remote_pack / remote_gept).
(No prices or paper counts in the copy: build_exam_pack.py owns those.)
"""
import os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINE = "https://lin.ee/W9J8TuQ"
START, END = "<!-- AE:REGION -->", "<!-- /AE:REGION -->"

FOUNDER = ("來自板橋的真實教室", "這些教材，就是我<em>每天上課用的</em>",
           "我是 Christopher——密西根大學畢業、美國持證教師，在板橋教英文。這頁的內容不是編輯整理的，"
           "是我教室裡每天在用的教材。接下來怎麼用，看你住哪裡：")
# page → (eyebrow, h2 with <em>, intro)
PAGES = {
    "kk-phonetic-chart": FOUNDER,
    "phonics-rules-chart": FOUNDER,
    "moe-1200-words-guide": FOUNDER,
    "irregular-verbs-list": FOUNDER,
    "english-names-boys": ("名字選好之後", "想讓孩子<em>真的開口說</em>？",
                           "我是 Christopher——密西根大學畢業、美國持證教師，在板橋教英文。"
                           "名字只是第一步，接下來怎麼學，看你住哪裡："),
}
PACK, GEPT, COURSES = "/cambridge-practice-exam-pack/", "/gept/", "/courses/"

CARD = 'style="text-align:left;display:flex;flex-direction:column"'
ROW = 'style="justify-content:flex-start;margin-top:auto;padding-top:22px"'


def block(eyebrow, h2, intro):
    return f"""{START}
<section class="section bg-soft region-cta">
  <div class="wrap">
    <div class="center" style="max-width:720px;margin:0 auto 32px">
      <span class="eyebrow eyebrow-green">{eyebrow}</span>
      <h2 style="margin-top:14px">{h2}</h2>
      <p class="body" style="margin-top:16px">{intro}</p>
    </div>
    <div class="cards two" style="max-width:920px;margin:0 auto">
      <div class="card" {CARD}>
        <span class="eyebrow eyebrow-green" style="align-self:flex-start">住雙北</span>
        <h3 style="margin-top:14px">來教室做一次免費程度評估</h3>
        <p class="body" style="margin-top:8px">教室在板橋中正路。加 LINE 約個時間，我會告訴你孩子的程度落在哪個階段、下一步該練什麼——不推銷，就是告訴你孩子的真實落點。</p>
        <div class="cta-row" {ROW}>
          <a class="btn btn-primary" href="{LINE}" target="_blank" rel="noopener"><span class="btn-line" data-line-icon></span>加 LINE 預約免費評估</a>
          <a class="btn btn-outline" href="{COURSES}" data-region-choice="local_courses">看課程總覽</a>
        </div>
      </div>
      <div class="card" {CARD}>
        <span class="eyebrow eyebrow-yellow" style="align-self:flex-start">不在雙北</span>
        <h3 style="margin-top:14px">在家做一份完整模擬試題</h3>
        <p class="body" style="margin-top:8px">來不了教室也沒關係。網站上的線上練習全部免費、不用註冊；想讓孩子從第一題計時做到最後一題，我們自己出了劍橋英檢和全民英檢的完整模擬試題，每一份都含題目卷、中文逐題解析與聽力音檔，線上付款後立刻寄到信箱。</p>
        <div class="cta-row" {ROW}>
          <a class="btn btn-blue" href="{PACK}" data-region-choice="remote_pack">劍橋英檢模擬試題</a>
          <a class="btn btn-outline" href="{GEPT}" data-region-choice="remote_gept">全民英檢模擬試題</a>
        </div>
      </div>
    </div>
  </div>
</section>
{END}
"""


# the hand-written box this block replaces (same wording on every page that had it)
OLD_BOX = re.compile(r'<section class="section bg-soft">\s*<div class="wrap">\s*<div class="cta-box reveal">\s*'
                     r'<span class="eyebrow eyebrow-green">來自板橋的真實教室</span>.*?</section>\n?', re.S)
# the names page closed on a lone LINE button under its reading links: the block below it
# now carries the booking, so the button would be the same offer twice in a row
OLD_BTN = re.compile(r'\s*<a class="btn btn-primary" href="' + re.escape(LINE) +
                     r'" target="_blank" rel="noopener">LINE 免費諮詢＋預約試聽</a>')


def main():
    for target in (PACK, GEPT, COURSES):
        if not os.path.isfile(os.path.join(SITE, target.strip("/"), "index.html")):
            sys.exit(f"BROKEN region target: {target}")
    for page, (eyebrow, h2, intro) in PAGES.items():
        p = os.path.join(SITE, page, "index.html")
        if not os.path.isfile(p):
            print(f"  no page: {page}"); continue
        s = open(p, encoding="utf-8").read()
        blk = block(eyebrow, h2, intro)
        if START in s:
            s2 = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", lambda m: blk, s, count=1, flags=re.S)
            how = "replaced"
        elif OLD_BOX.search(s):
            s2 = OLD_BOX.sub(lambda m: blk, s, count=1)
            how = "swapped"
        else:
            i = s.find("<!-- AE:BYL start -->")
            if i < 0:
                i = s.rfind("</main>")
            if i < 0:
                print(f"  no anchor: {page}"); continue
            s2 = OLD_BTN.sub("", s[:i]).rstrip() + "\n\n" + blk + "\n" + s[i:]
            how = "inserted"
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
        print(f"  {how:8s} /{page}/")


if __name__ == "__main__":
    main()
