#!/usr/bin/env python3
"""Three GEPT exam-prep pages for the December–January exams (2026-11-22, Chris: "build pages for the december GEPT exams").

  gept-elementary-exam-prep/              初級聽讀 2027/1/9 — registration to 11/26, 7-week plan, exam day
  gept-intermediate-exam-prep/            中級聽讀＋一日考 2027/1/30 — registration to 11/30 (一日考 11/23), plan, exam day
  gept-high-intermediate-speaking-writing/  中高級說寫 2026/12/19 — what is scored, pass marks, 4-week plan

Facts (dates, fees, formats, pass marks, test-room rules) come only from LTTC: gepttestdate.aspx (read 2026-11-22),
the level pages t01/t02/t03_introduction.asp, and the 2026 registration guide pp.40–41 as transcribed in
~/Downloads/AE-gept-research/01-official-truth-set.md. Study plans are labelled as Christopher's advice.
The page shell is copied from gept-elementary-speaking-writing; run tools/seo_build.py afterwards (chrome, SEO blocks,
dates box, TOC) and ae-question-bank/tools/swap_pack_offer.py (the pack strip).
Writes ~/Downloads/GLOSS-2026-11-22-GEPT-EXAM-PREP.md (every Chinese line with its English, for Chris).
"""
import html, json, os, re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://americanenglish.com.tw"
LTTC_DATES = "https://www.gept.org.tw/GEPT1/gepttestdate.aspx"
GUIDE_PDF = "https://www.gept.org.tw/info/registration_guide.pdf"
GLOSS_OUT = os.path.expanduser("~/Downloads/GLOSS-2026-11-22-GEPT-EXAM-PREP.md")
TEMPLATE = os.path.join(SITE, "gept-elementary-speaking-writing", "index.html")
TODAY = "2026-11-22"
esc = html.escape
GLOSS, _cur = {}, [""]


def Z(zh, en):
    GLOSS.setdefault(_cur[0], []).append((zh, en))
    return zh


def sec(eyebrow, color, hid, title, body, soft=False):
    return f"""<section class="section{' bg-soft' if soft else ''}">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-{color}">{eyebrow}</span><h2 id="{hid}">{title}</h2></div>
    <div class="prose reveal" style="max-width:800px;margin:0 auto">
{body}
    </div>
  </div>
</section>
"""


def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div style="overflow-x:auto"><table class="wtable"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def faq(items):
    out = []
    for q, a in items:
        qid = re.sub(r"[^\w一-鿿-]+", "", q.replace(" ", "-"))
        out.append(f'<div class="faq-item"><h3 id="{qid}" class="faq-h"><button class="faq-q" aria-expanded="false">{q}<span class="pm"></span></button></h3>'
                   f'<div class="faq-a"><p>{a}</p></div></div>')
    return '<div class="faq">\n      ' + "\n      ".join(out) + "\n    </div>"


def exam_day(pen_kind):
    """LTTC test-room rules (2026 registration guide pp.40–41)."""
    pen = (Z("2B 黑色鉛筆和橡皮擦（聽力、閱讀用電腦讀卡）", "a 2B black pencil and an eraser (listening and reading are machine-marked)") if pen_kind == "pencil"
           else Z("黑色原子筆和修正帶（寫作用）", "a black ballpoint pen and correction tape (for writing)"))
    items = [Z("<b>身分證件正本</b>：國民身分證、駕照或有效護照；<b>國中生（含）以下可以用健保卡正本</b>代替。影本不行。",
               "<b>An original ID</b>: national ID card, driving licence or valid passport; <b>junior-high pupils and below may use the original NHI card</b> instead. No copies."),
             pen,
             Z("手機、手錶、手環等所有電子用品<b>關機</b>，和書包一起放在教室前面的地上。考試中發出任何聲音（包括震動），<b>每一科扣 5 分</b>；被發現開機，每一科扣 2 分。",
               "Phones, watches, bands and every other device <b>switched off</b> and left on the floor at the front of the room with your bag. Any sound during the test (including vibration) costs <b>5 marks per component</b>; a device found switched on costs 2."),
             Z("<b>遲到超過 10 分鐘不能進場</b>，也不退費。坐錯位子每一科扣 5 分。",
               "<b>More than 10 minutes late and you cannot enter</b>, with no refund. Sitting in the wrong seat costs 5 marks per component."),
             Z("考場不保管貴重物品。身體不舒服或上廁所的時間不會補回來。",
               "The venue does not look after valuables. Time lost to feeling unwell or using the toilet is not made up.")]
    li = "".join(f"<li>{x}</li>" for x in items)
    src = Z(f'以上依 LTTC <a href="{GUIDE_PDF}" target="_blank" rel="noopener">報名須知</a>的試場規則整理；考前請再看一次考試通知上的規定。',
            "From the test-room rules in LTTC's registration guide (link); check your exam notice again before the day.")
    return f"<ul>{li}</ul>\n<p style=\"font-size:14px;color:#64748b\">{src}</p>"


def cta(title_zh, title_en, links):
    t = Z(title_zh, title_en)
    lk = "".join(f'<a href="{u}" class="btn {"btn-primary" if i == 0 else "btn-outline"}">{Z(a, b)}</a>' for i, (u, a, b) in enumerate(links))
    return f"""<section class="section bg-blue">
  <div class="wrap">
    <div class="cta-box reveal">
      <span class="eyebrow eyebrow-green">{Z("免費練習", "free practice")}</span>
      <h2 id="{re.sub(r'<[^>]+>|[^\w一-鿿]', '', t)}" style="margin-top:14px">{t}</h2>
      <p class="body" style="max-width:560px;margin:16px auto 0">{Z("每一部分都可以直接在網頁上作答、對答案、看中文解析，不用註冊。",
          "Every part can be answered on the page, checked and explained in Chinese, with no sign-up.")}</p>
      <div class="cta-row">{lk}</div>
    </div>
  </div>
</section>
"""


PACK = "<!-- AE:PACKOFFER -->\n<!-- /AE:PACKOFFER -->\n"

# ------------------------------------------------------------------ pages


def elementary():
    _cur[0] = "gept-elementary-exam-prep"
    P = "/gept-elementary-"
    dates = table([Z("項目", "item"), Z("日期", "date")], [
        [Z("網路報名截止", "online registration closes"), Z("<b>2026/11/26（四）下午 5 點</b>", "<b>Thu 26 Nov 2026, 5 pm</b>")],
        [Z("考試通知（email）", "exam notice (email)"), Z("2026/12/30（三）", "Wed 30 Dec 2026")],
        [Z("<b>考試</b>", "<b>exam</b>"), Z("<b>2027/1/9（六）</b>聽力＋閱讀", "<b>Sat 9 Jan 2027</b> listening + reading")],
        [Z("成績公布", "results"), Z("2027/1/21（四）", "Thu 21 Jan 2027")],
        [Z("報名費", "fee"), Z("聽讀 630 元", "listening + reading NT$630")]])
    fmt = table([Z("科目", "paper"), Z("題型", "parts"), Z("題數", "items"), Z("時間", "time")], [
        [Z("聽力", "listening"), Z(f'<a href="{P}listening-practice-part1/">看圖辨義</a>・<a href="{P}listening-practice-part2/">問答</a>・<a href="{P}listening-practice-part3/">簡短對話</a>・<a href="{P}listening-practice-part4/">短文聽解</a>',
                                    "picture identification, question & response, short conversations, short talks (each links to our free practice)"), "30", Z("約 20 分鐘", "about 20 min")],
        [Z("閱讀", "reading"), Z(f'<a href="{P}reading-practice-part1/">詞彙</a>・<a href="{P}reading-practice-part2/">段落填空</a>・<a href="{P}reading-practice-part3/">閱讀理解</a>',
                                  "vocabulary, cloze, reading comprehension"), "30", Z("35 分鐘", "35 min")]])
    plan = table([Z("週", "week"), Z("做什麼", "what to do")], [
        [Z("11/23 那週", "week of 23 Nov"), Z(f'還沒報名的，<b>11/26 下午 5 點前</b>報名。做一份<a href="{P}practice/">免費模擬題</a>，看聽力和閱讀哪一科比較弱。',
                                              "Register before 5 pm on 26 Nov if you have not. Do one free practice test to see which paper is weaker.")],
        [Z("11/30", "30 Nov"), Z(f'聽力 <a href="{P}listening-practice-part1/">Part 1</a>、<a href="{P}listening-practice-part2/">Part 2</a>：每天 15 分鐘。每題只播一次，練習聽完立刻選。',
                                  "Listening Parts 1–2, 15 minutes a day. Each item plays once: practise choosing straight away.")],
        [Z("12/7", "7 Dec"), Z(f'聽力 <a href="{P}listening-practice-part3/">Part 3</a>、<a href="{P}listening-practice-part4/">Part 4</a>，錯的題目看逐字稿再聽一次。',
                                "Listening Parts 3–4; for each mistake read the transcript and listen again.")],
        [Z("12/14", "14 Dec"), Z(f'閱讀 <a href="{P}reading-practice-part1/">詞彙</a>、<a href="{P}reading-practice-part2/">段落填空</a>；把錯的單字記在一張紙上，每天看一次。',
                                  "Reading: vocabulary and cloze; keep the missed words on one sheet and look at it daily.")],
        [Z("12/21", "21 Dec"), Z(f'<a href="{P}reading-practice-part3/">閱讀理解</a>，開始計時：閱讀整份 35 分鐘。',
                                  "Reading comprehension, now timed: the whole reading paper in 35 minutes.")],
        [Z("12/28", "28 Dec"), Z("12/30 收到考試通知，確認考場和時間。週末做一次完整模擬：聽力接著閱讀，中間不休息。",
                                  "The exam notice arrives on 30 Dec: check the venue and time. At the weekend do one full mock, listening then reading with no break.")],
        [Z("1/4 那週", "week of 4 Jan"), Z("只複習錯過的題目，不要再加新東西。準備證件、2B 鉛筆、橡皮擦，早點睡。",
                                        "Only review past mistakes; add nothing new. Get the ID, 2B pencil and eraser ready, and sleep early.")]])
    body = [
        sec(Z("日期", "dates"), "yellow", "2027-年-1-月-9-日初級聽讀的日期", Z("1/9 初級聽讀，<em>這幾個日期</em>先記下來", "the dates for the 9 January exam"),
            f"<p>{Z('LTTC 公布的 2027 年第一場初級聽讀（聽力＋閱讀）：', 'LTTC’s first 2027 Elementary listening and reading exam:')}</p>\n{dates}\n"
            f"<p style=\"font-size:14px;color:#64748b\">{Z(f'資料來源：<a href=\"{LTTC_DATES}\" target=\"_blank\" rel=\"noopener\">LTTC 全民英檢測驗日程表</a>（2026/11/22 查）。', 'Source: LTTC GEPT schedule (checked 22 Nov 2026).')}</p>"),
        PACK,
        sec(Z("考什麼", "what is tested"), "green", "初級聽讀考什麼", Z("聽讀考什麼、<em>幾分過</em>", "what the test is and the pass mark"),
            f"{fmt}\n<p>{Z('聽力每題<b>只播一次</b>。聽力和閱讀連著考，<b>中間不休息</b>，含說明大約 1.5 小時。', 'Each listening item <b>plays once</b>. Listening and reading run back to back <b>with no break</b>, about 1.5 hours with instructions.')}</p>\n"
            f"<p>{Z('<b>通過標準</b>：聽力、閱讀各 120 分，兩科加起來至少 160 分，<b>而且每一科都不能低於 72 分</b>。總分夠、但閱讀只有 70，一樣不通過。', '<b>Pass mark</b>: listening and reading are 120 each; together at least 160, <b>and neither below 72</b>. A high total with reading at 70 still fails.')}</p>", soft=True),
        sec(Z("我的建議", "my advice"), "yellow", "考前-7-週讀書計畫", Z("考前 7 週，<em>每週一件事</em>", "seven weeks, one thing a week"),
            f"<p>{Z('下面是我會給學生的安排（Christopher 的建議，不是官方規定）。每一格都連到可以直接作答的免費練習。', 'This is the plan I give students (Christopher’s advice, not an official rule). Each row links to free practice you can do on the page.')}</p>\n{plan}"),
        sec(Z("考試當天", "exam day"), "green", "1-9-考試當天要帶什麼", Z("考試當天，<em>這些別忘了</em>", "exam day: don’t forget"), exam_day("pencil"), soft=True),
        sec(Z("常見問題", "FAQ"), "yellow", "初級聽讀考前常見問題", Z("考前，<em>家長常問的</em>", "what parents ask before the exam"), faq([
            (Z("1/9 的初級還能報名嗎？", "Can we still register for 9 January?"),
             Z(f"可以，網路報名到 <b>2026/11/26（四）下午 5 點</b>。在 <a href='{LTTC_DATES}' target='_blank' rel='noopener'>LTTC 網站</a>報名，聽讀報名費 630 元。",
               "Yes, online registration runs to 5 pm on Thu 26 Nov 2026, on the LTTC site; the fee is NT$630.")),
            (Z("考試通知什麼時候寄？", "When does the exam notice come?"),
             Z("2026/12/30（三）用 email 寄出，上面有考場、教室和時間。", "By email on Wed 30 Dec 2026, with the venue, room and time.")),
            (Z("什麼時候可以查成績？", "When are the results out?"),
             Z("2027/1/21（四）。查詢方法看<a href='/gept-results-lookup/'>全民英檢成績查詢</a>。", "Thu 21 Jan 2027; how to look them up is on our results page.")),
            (Z("國中生沒有身分證怎麼辦？", "What if a junior-high pupil has no ID card?"),
             Z("國中生（含）以下可以帶<b>健保卡正本</b>代替，有沒有照片都可以。影本不行。", "Junior-high pupils and below may bring the <b>original NHI card</b> instead, with or without a photo. No copies.")),
        ])),
        cta("離 1/9 還有幾週，<br>先做<em>一份免費模擬題</em>", "a few weeks before 9 January: start with one free practice test",
            [(f"{P}practice/", "做初級免費模擬題", "do the free Elementary practice"), ("/gept-elementary-guide/", "初級完整指南", "the full Elementary guide")]),
    ]
    return dict(slug="gept-elementary-exam-prep", crumb="初級考前衝刺",
                eyebrow=Z("全民英檢 · 2027/1/9", "GEPT · 9 Jan 2027"),
                h1=Z('<span class="h1s"><em>全民英檢初級</em>考前衝刺：</span><br><span class="h1s">1/9 聽讀，7 週準備計畫</span>',
                     "GEPT Elementary: a 7-week plan for the 9 January listening and reading exam"),
                lead=Z("報名到 11/26、考試通知 12/30、1/21 放榜。這一頁整理官方日期、考試內容、通過標準、每週該練什麼，還有考試當天要帶的東西。",
                       "Registration to 26 Nov, notice 30 Dec, results 21 Jan. This page has the official dates, what is tested, the pass mark, what to practise each week, and what to bring on the day."),
                img="gept-exam-day-whiteboard-notice", alt=Z("考場白板上的考試注意事項", "exam-day notes on a classroom whiteboard"),
                title=Z("全民英檢初級考前衝刺：2027/1/9 聽讀考試日期、7 週讀書計畫", "GEPT Elementary 9 Jan 2027: dates and 7-week plan"),
                desc=Z("全民英檢初級 2027/1/9 聽讀：報名到 11/26 下午 5 點、12/30 寄通知、1/21 放榜。考什麼、通過標準、考前 7 週計畫與考試當天要帶什麼。",
                       "GEPT Elementary 9 Jan 2027: registration to 26 Nov 5 pm, notice 30 Dec, results 21 Jan; what is tested, the 160/72 pass mark, a 7-week plan and what to bring."),
                body=body)


def intermediate():
    _cur[0] = "gept-intermediate-exam-prep"
    P = "/gept-intermediate-"
    dates = table([Z("項目", "item"), Z("聽讀", "listening + reading"), Z("一日考", "one-day exam")], [
        [Z("網路報名截止", "registration closes"), Z("<b>2026/11/30（一）下午 5 點</b>", "<b>Mon 30 Nov 2026, 5 pm</b>"), Z("<b>2026/11/23（一）下午 5 點</b>", "<b>Mon 23 Nov 2026, 5 pm</b>")],
        [Z("考試通知（email）", "exam notice (email)"), Z("2027/1/20（三）", "Wed 20 Jan 2027"), Z("2027/1/20（三）", "Wed 20 Jan 2027")],
        [Z("<b>考試</b>", "<b>exam</b>"), Z("<b>2027/1/30（六）</b>", "<b>Sat 30 Jan 2027</b>"), Z("<b>2027/1/30（六）</b>", "<b>Sat 30 Jan 2027</b>")],
        [Z("成績公布", "results"), Z("2027/2/26（五）", "Fri 26 Feb 2027"), Z("2027/3/5（五）", "Fri 5 Mar 2027")],
        [Z("報名費", "fee"), Z("900 元", "NT$900"), Z("2,530 元", "NT$2,530")]])
    fmt = table([Z("科目", "paper"), Z("題型", "parts"), Z("題數", "items"), Z("時間", "time")], [
        [Z("聽力", "listening"), Z(f'<a href="{P}listening-practice-part1/">看圖辨義</a>・<a href="{P}listening-practice-part2/">問答</a>・<a href="{P}listening-practice-part3/">簡短對話</a>・<a href="{P}listening-practice-part4/">簡短談話</a>',
                                    "picture identification, question & response, short conversations, short talks"), "35", Z("約 30 分鐘", "about 30 min")],
        [Z("閱讀", "reading"), Z(f'<a href="{P}reading-practice-part1/">詞彙</a>・<a href="{P}reading-practice-part2/">段落填空</a>・<a href="{P}reading-practice-part3/">閱讀理解</a>',
                                  "vocabulary, cloze, reading comprehension"), "35", Z("45 分鐘", "45 min")]])
    plan = table([Z("時間", "when"), Z("做什麼", "what to do")], [
        [Z("11 月底", "end of November"), Z(f'報名（聽讀到 11/30、一日考到 11/23）。做一份<a href="{P}practice/">免費模擬題</a>，找出比較弱的一科。',
                                           "Register (listening + reading to 30 Nov, one-day exam to 23 Nov). Do one free practice test to find the weaker paper.")],
        [Z("12 月第 1–2 週", "early December"), Z(f'聽力四個部分輪流練，每天 20 分鐘；中級每題四個選項，練習邊聽邊刪掉不可能的答案。',
                                                 "Rotate the four listening parts, 20 minutes a day; Intermediate items have four options, so practise ruling out the impossible ones while listening.")],
        [Z("12 月第 3–4 週", "late December"), Z(f'閱讀<a href="{P}reading-practice-part3/">閱讀理解</a>每天一篇，計時；錯的單字和片語集中在一張紙上。',
                                                "One reading-comprehension set a day, timed; collect missed words and phrases on one sheet.")],
        [Z("1 月第 1–2 週", "early January"), Z("每週一次完整模擬：聽力接著閱讀，大約 2 小時，中間不休息。", "One full mock a week: listening then reading, about 2 hours, no break.")],
        [Z("1/20 之後", "after 20 Jan"), Z("考試通知寄出，確認考場。最後一週只複習錯題，準備證件和 2B 鉛筆。",
                                         "The exam notice arrives: check the venue. In the last week only review mistakes; get the ID and 2B pencil ready.")]])
    body = [
        sec(Z("日期", "dates"), "yellow", "2027-年-1-月-30-日中級的日期", Z("1/30 中級，<em>這幾個日期</em>先記下來", "the dates for the 30 January exam"),
            f"<p>{Z('1/30 同一天有兩種考法：只考聽讀，或「一日考」（同一天考完初試和複試）。兩者的報名截止日不一樣：', 'On 30 January there are two options: listening and reading only, or the one-day exam (both stages on one day). They close on different days:')}</p>\n{dates}\n"
            f"<p style=\"font-size:14px;color:#64748b\">{Z(f'資料來源：<a href=\"{LTTC_DATES}\" target=\"_blank\" rel=\"noopener\">LTTC 全民英檢測驗日程表</a>（2026/11/22 查）。', 'Source: LTTC GEPT schedule (checked 22 Nov 2026).')}</p>"),
        PACK,
        sec(Z("考什麼", "what is tested"), "green", "中級聽讀考什麼", Z("聽讀考什麼、<em>幾分過</em>", "what the test is and the pass mark"),
            f"{fmt}\n<p>{Z('聽力和閱讀連著考，含說明大約 2 小時。', 'Listening and reading run back to back, about 2 hours with instructions.')}</p>\n"
            f"<p>{Z('<b>通過標準</b>：聽力、閱讀各 120 分，兩科加起來至少 160 分，<b>而且每一科都不能低於 72 分</b>。複試（寫作、口說）各 80 分通過。', '<b>Pass mark</b>: 120 each; together at least 160, <b>and neither below 72</b>. The second stage (writing, speaking) needs 80 in each.')}</p>"
            f"<p>{Z('更多中級的程度與計分，看<a href=\"/gept-intermediate-guide/\">全民英檢中級指南</a>。', 'More on the level and scoring in our Intermediate guide.')}</p>", soft=True),
        sec(Z("我的建議", "my advice"), "yellow", "考前-10-週讀書計畫", Z("考前 10 週，<em>怎麼排</em>", "how to use the ten weeks"),
            f"<p>{Z('下面是我會給學生的安排（Christopher 的建議，不是官方規定）。', 'This is the plan I give students (Christopher’s advice, not an official rule).')}</p>\n{plan}"),
        sec(Z("考試當天", "exam day"), "green", "1-30-考試當天要帶什麼", Z("考試當天，<em>這些別忘了</em>", "exam day: don’t forget"), exam_day("pencil"), soft=True),
        sec(Z("常見問題", "FAQ"), "yellow", "中級考前常見問題", Z("考前，<em>常被問的</em>", "common questions before the exam"), faq([
            (Z("聽讀和一日考差在哪？", "What is the difference between listening + reading and the one-day exam?"),
             Z("聽讀只考初試（聽力、閱讀）；一日考是同一天考完初試和複試（寫作、口說），報名費 2,530 元、報名到 11/23 下午 5 點，成績 3/5 公布。",
               "Listening + reading is the first stage only; the one-day exam does both stages on one day, costs NT$2,530, closes at 5 pm on 23 Nov, with results on 5 Mar.")),
            (Z("總分夠了為什麼沒過？", "Why fail with a high enough total?"),
             Z("因為每一科都不能低於 72 分。例如聽力 94、閱讀 70，總分 164 也不通過。", "Because neither paper may be below 72: listening 94 + reading 70 = 164 still fails.")),
            (Z("什麼時候可以查成績？", "When are the results out?"),
             Z("聽讀 2027/2/26（五），一日考 2027/3/5（五）。查詢方法看<a href='/gept-results-lookup/'>全民英檢成績查詢</a>。", "Listening + reading on Fri 26 Feb 2027, the one-day exam on Fri 5 Mar 2027.")),
        ])),
        cta("考前先做<em>一份免費中級模擬題</em>", "before the exam, do one free Intermediate practice test",
            [(f"{P}practice/", "做中級免費模擬題", "do the free Intermediate practice"), ("/gept-intermediate-guide/", "中級指南", "the Intermediate guide")]),
    ]
    return dict(slug="gept-intermediate-exam-prep", crumb="中級考前衝刺",
                eyebrow=Z("全民英檢 · 2027/1/30", "GEPT · 30 Jan 2027"),
                h1=Z('<span class="h1s"><em>全民英檢中級</em>考前衝刺：</span><br><span class="h1s">1/30 聽讀＋一日考</span>',
                     "GEPT Intermediate: preparing for the 30 January exam"),
                lead=Z("聽讀報名到 11/30、一日考報名到 11/23；1/20 寄考試通知，2/26 放榜。這一頁整理官方日期、考試內容、通過標準和考前 10 週的安排。",
                       "Listening + reading registration to 30 Nov, the one-day exam to 23 Nov; notice 20 Jan, results 26 Feb. The official dates, what is tested, the pass mark and a 10-week plan."),
                img="exam-dates-calendar-marking", alt=Z("在月曆上圈出考試日期", "marking the exam date on a calendar"),
                title=Z("全民英檢中級考前衝刺：2027/1/30 聽讀與一日考日期、讀書計畫", "GEPT Intermediate 30 Jan 2027: dates and plan"),
                desc=Z("全民英檢中級 2027/1/30：聽讀報名到 11/30、一日考到 11/23，1/20 寄通知、2/26 放榜。考什麼、通過標準、考前讀書計畫與當天要帶什麼。",
                       "GEPT Intermediate 30 Jan 2027: registration deadlines, notice, results, what is tested, the pass mark, a study plan and what to bring."),
                body=body)


def high_intermediate():
    _cur[0] = "gept-high-intermediate-speaking-writing"
    P = "/gept-high-intermediate-"
    dates = table([Z("項目", "item"), Z("日期", "date")], [
        [Z("考試通知（email）", "exam notice (email)"), Z("2026/12/9（三）", "Wed 9 Dec 2026")],
        [Z("<b>說寫測驗</b>", "<b>speaking + writing exam</b>"), Z("<b>2026/12/19（六）</b>", "<b>Sat 19 Dec 2026</b>")],
        [Z("成績公布", "results"), Z("2027/2/3（三）", "Wed 3 Feb 2027")]])
    write = table([Z("部分", "part"), Z("內容", "task"), Z("比重", "weight")], [
        [Z(f'<a href="{P}writing-practice-part1/">第一部分</a>', "Part 1"), Z("中譯英：把一段中文翻成英文", "Chinese-to-English translation of a passage"), "40%"],
        [Z(f'<a href="{P}writing-practice-part2/">第二部分</a>', "Part 2"), Z("引導寫作：依題目寫一篇 150–180 字的文章", "guided writing: a 150–180-word essay on the prompt"), "60%"]])
    speak = table([Z("部分", "part"), Z("內容", "task"), Z("時間", "time")], [
        [Z("第一部分", "Part 1"), Z("回答問題 8 題", "answer 8 questions"), Z("前 4 題每題 15 秒，後 4 題每題 30 秒", "Q1–4: 15 s each; Q5–8: 30 s each")],
        [Z("第二部分", "Part 2"), Z("看圖敘述", "describe a picture"), Z("想 30 秒，說 1.5 分鐘", "30 s to think, 1.5 min to speak")],
        [Z("第三部分", "Part 3"), Z("申述：針對題目表達看法", "a short talk giving your view on a topic"), Z("想（可做筆記）1.5 分鐘，說 1.5 分鐘", "1.5 min to think and make notes, 1.5 min to speak")]])
    plan = table([Z("週", "week"), Z("寫作", "writing"), Z("口說", "speaking")], [
        [Z("11/23", "23 Nov"), Z(f'做一次<a href="{P}writing-practice-part1/">中譯英</a>，計時，找出最常錯的地方（時態、介系詞、搭配）。', "One timed translation; find your most common errors (tense, prepositions, collocations)."),
         Z(f'錄下<a href="{P}speaking-practice/">回答問題</a> 8 題，自己聽一次。', "Record the 8 answer-the-question items and listen back.")],
        [Z("11/30", "30 Nov"), Z(f'<a href="{P}writing-practice-part2/">引導寫作</a>每週兩篇，控制在 150–180 字，先列大綱再寫。', "Two guided essays a week, 150–180 words, outline first."),
         Z("看圖敘述：先說看到什麼，再推測發生什麼事。", "Picture description: say what you see, then what is probably happening.")],
        [Z("12/7", "7 Dec"), Z("中譯英和寫作輪流練；寫完檢查拼字、標點、大小寫。", "Alternate translation and essays; check spelling, punctuation and capitals."),
         Z("申述：1.5 分鐘想、1.5 分鐘說，練到說得滿時間。", "The short talk: 1.5 min to think, 1.5 to speak, until you can fill the time.")],
        [Z("12/14 那週", "week of 14 Dec"), Z("12/9 收到考試通知、確認考場。最後一週計時寫一份完整的（50 分鐘）。", "The notice comes on 9 Dec: check the venue. In the last week write one full timed paper (50 min)."),
         Z("錄一次完整口說（約 15 分鐘），只修正最常犯的一兩個錯。", "Record one full speaking test (about 15 min) and fix only the one or two most common errors.")]])
    body = [
        sec(Z("日期", "dates"), "yellow", "12-19-中高級說寫的日期", Z("12/19 中高級說寫，<em>這幾個日期</em>", "the dates for 19 December"),
            f"{dates}\n<p style=\"font-size:14px;color:#64748b\">{Z(f'資料來源：LTTC 2026 年<a href=\"{GUIDE_PDF}\" target=\"_blank\" rel=\"noopener\">報名須知</a>測驗日程。報名已在 11/16 截止。', 'Source: the 2026 schedule in LTTC’s registration guide. Registration closed on 16 Nov.')}</p>"),
        PACK,
        sec(Z("寫作", "writing"), "green", "中高級寫作考什麼", Z("寫作 50 分鐘，<em>兩個部分</em>", "writing: 50 minutes, two parts"),
            f"{write}\n<p>{Z('兩位評分老師各自給 0–5 級分，平均後換算成百分制。翻譯太短（少於 25 字）、文章太短（少於 40 字）或完全離題，<b>視同沒有作答</b>。', 'Two raters each give 0–5; the average is converted to 100. A translation under 25 words, an essay under 40 words, or one completely off topic <b>counts as no answer</b>.')}</p>", soft=True),
        sec(Z("口說", "speaking"), "yellow", "中高級口說考什麼", Z(f'口說約 15 分鐘，<em>三個部分</em>', "speaking: about 15 minutes, three parts"),
            f"{speak}\n<p>{Z(f'每一部分都可以在<a href=\"{P}speaking-practice/\">中高級口說練習</a>直接錄音練習。', 'Every part can be practised with recording on our High-Intermediate speaking page.')}</p>"),
        sec(Z("通過標準", "pass mark"), "green", "中高級說寫幾分過", Z("寫作、口說<em>各 80 分</em>", "80 in writing and 80 in speaking"),
            f"<p>{Z('寫作、口說各 100 分，<b>各自達到 80 分</b>才算通過（不是兩科平均）。5 級分制裡，80 分就是 4 級分。', 'Writing and speaking are each out of 100 and <b>each must reach 80</b> (not an average). On the 0–5 scale, 80 is band 4.')}</p>"
            f"<p>{Z('4 級分的寫作，LTTC 的描述是：內容符合題目要求、組織良好、大致連貫，能正確使用字彙與句型，仍偶有錯誤。', 'LTTC describes band-4 writing as on task, well organised, generally coherent, with correct vocabulary and structures and occasional errors.')}</p>", soft=True),
        sec(Z("我的建議", "my advice"), "yellow", "考前-4-週說寫計畫", Z("考前 4 週，<em>寫作和口說一起練</em>", "four weeks: practise writing and speaking together"),
            f"<p>{Z('下面是我會給學生的安排（Christopher 的建議，不是官方規定）。', 'This is the plan I give students (Christopher’s advice, not an official rule).')}</p>\n{plan}"),
        sec(Z("考試當天", "exam day"), "green", "12-19-考試當天要帶什麼", Z("考試當天，<em>這些別忘了</em>", "exam day: don’t forget"), exam_day("pen"), soft=True),
        sec(Z("常見問題", "FAQ"), "yellow", "中高級說寫常見問題", Z("考前，<em>常被問的</em>", "common questions"), faq([
            (Z("中高級說寫什麼時候放榜？", "When are the 19 December results out?"),
             Z("2027/2/3（三）。查詢方法看<a href='/gept-results-lookup/'>全民英檢成績查詢</a>。", "Wed 3 Feb 2027; see our results page.")),
            (Z("寫作和口說可以互相補分嗎？", "Can one skill make up for the other?"),
             Z("不行。寫作、口說各自要到 80 分，口說 90、寫作 76 一樣不通過寫作。", "No: each must reach 80; speaking 90 with writing 76 still fails writing.")),
            (Z("文章寫太短會怎樣？", "What if the essay is too short?"),
             Z("少於 40 字視同沒有作答；題目要求 150–180 字，寫不到會影響內容和組織的分數。", "Under 40 words counts as no answer; the task asks for 150–180 words, and falling short costs content and organisation marks.")),
        ])),
        cta("考前先把<em>三部分口說</em>錄一次", "before the exam, record all three speaking parts once",
            [(f"{P}speaking-practice/", "中高級口說練習（可錄音）", "High-Intermediate speaking practice (with recording)"), (f"{P}writing-practice-part2/", "中高級寫作練習", "High-Intermediate writing practice")]),
    ]
    return dict(slug="gept-high-intermediate-speaking-writing", crumb="中高級說寫",
                eyebrow=Z("全民英檢 · 12/19 說寫", "GEPT · 19 Dec speaking + writing"),
                h1=Z('<span class="h1s"><em>全民英檢中高級</em>說寫：</span><br><span class="h1s">12/19 寫作與口說怎麼準備</span>',
                     "GEPT High-Intermediate speaking and writing: preparing for 19 December"),
                lead=Z("寫作考中譯英＋150–180 字引導寫作，口說考回答問題、看圖敘述、申述；兩科各 80 分通過。12/9 寄考試通知，2027/2/3 放榜。",
                       "Writing: translation plus a 150–180-word essay; speaking: answering questions, describing a picture, a short talk; 80 in each to pass. Notice 9 Dec, results 3 Feb 2027."),
                img="gept-speaking-test-interview-practice", alt=Z("兩人面對面坐著進行口說練習", "two people practising a speaking test face to face"),
                title=Z("全民英檢中高級說寫 12/19：寫作口說考什麼、幾分過", "GEPT High-Intermediate speaking + writing 19 Dec"),
                desc=Z("全民英檢中高級說寫 12/19：寫作考中譯英與 150–180 字引導寫作，口說考回答問題、看圖敘述、申述，兩科各 80 分通過；附考前 4 週計畫。",
                       "GEPT High-Intermediate second stage on 19 Dec: what writing and speaking test, the 80/80 pass mark, notice and results dates, and a 4-week plan."),
                body=body)


# ------------------------------------------------------------------ shell


def build(p):
    t = open(TEMPLATE, encoding="utf-8").read()
    slug, url = p["slug"], f"{ORIGIN}/{p['slug']}/"
    title_tag = p["title"] + "｜埃森美語"
    t = re.sub(r"<title>.*?</title>", f"<title>{esc(title_tag)}</title>", t, count=1, flags=re.S)
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(p["desc"])}">', t, count=1)
    t = t.replace(f"{ORIGIN}/gept-elementary-speaking-writing/", url)
    t = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(p["title"])}">', t, count=1)
    t = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(p["desc"])}">', t, count=1)
    t = t.replace("/assets/img/blog/gept-speaking-test-interview-practice", f"/assets/img/blog/{p['img']}")
    t = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{esc(p["alt"])}">', t, count=1)
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": re.sub(r"<[^>]+>", "", p["h1"]),
          "description": p["desc"], "url": url, "mainEntityOfPage": url, "inLanguage": "zh-Hant-TW",
          "datePublished": TODAY, "dateModified": TODAY, "image": f"{ORIGIN}/assets/img/blog/{p['img']}.webp",
          "author": {"@type": "Person", "name": "Christopher", "url": f"{ORIGIN}/certified-american-teacher-banqiao/"},
          "publisher": {"@id": f"{ORIGIN}/#organization"}}
    t = re.sub(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"BlogPosting".*?</script>',
               lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + "</script>", t, count=1, flags=re.S)
    t = t.replace('data-page="gept-elementary-speaking-writing"', f'data-page="{slug}"')
    hero = f"""<section class="page-hero">
  <div class="bg-deco"></div>
  <div class="wrap">
    <div class="breadcrumb reveal"><a href="/">首頁</a> ／ <a href="/gept/">全民英檢</a> ／ {p['crumb']}</div>
    <span class="eyebrow eyebrow-green reveal">{p['eyebrow']}</span>
    <h1 class="reveal d1">{p['h1']}</h1>
    <div class="divider reveal d1"></div>
    <p class="body reveal d2">{p['lead']}</p>
    <p class="body reveal d2" style="font-size:14px">作者：Christopher｜埃森美語創辦人｜美國密西根大學畢業、美國正式教師執照<!-- AE:PAGEMETA start --><!-- AE:PAGEMETA end --></p>
    <figure class="post-hero pf-cream reveal d2">
      <img src="/assets/img/blog/{p['img']}.webp" srcset="/assets/img/blog/{p['img']}-800.webp 800w, /assets/img/blog/{p['img']}.webp 1600w" sizes="(max-width:828px) 100vw, 732px" alt="{esc(p['alt'])}" width="1600" height="900" fetchpriority="high" decoding="async">
    </figure>
  </div>
</section>
"""
    main = "\n<main id=\"top\">\n\n" + hero + "\n" + "\n".join(p["body"]) + "\n"
    a, b = t.index("\n<main id=\"top\">"), t.index("<!-- AE:BYL start -->")
    t = t[:a] + main + t[b:]
    d = os.path.join(SITE, slug)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(t)
    print("  wrote", slug)
    return slug, p["title"], p["desc"]


def main():
    pages = [elementary(), intermediate(), high_intermediate()]
    snip_p = os.path.join(SITE, "data", "snippets.json")
    snip = json.load(open(snip_p, encoding="utf-8"))
    for p in pages:
        slug, title, desc = build(p)
        snip[slug] = {"description": desc, "title": title + "｜埃森美語"}
    sm = os.path.join(SITE, "sitemap.xml")      # seo_build fills <lastmod> only for URLs already listed; add ours once
    xml = open(sm, encoding="utf-8").read()
    add = [f"{ORIGIN}/{p['slug']}/" for p in pages if f"<loc>{ORIGIN}/{p['slug']}/</loc>" not in xml]
    if add:
        open(sm, "w", encoding="utf-8").write(xml.replace("</urlset>", "".join(f"  <url><loc>{u}</loc></url>\n" for u in add) + "</urlset>"))
    print("  sitemap:", len(add), "added")
    json.dump(snip, open(snip_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(snip_p, "a", encoding="utf-8").write("\n")
    L = ["# GEPT exam-prep pages — every Chinese line with its English (2026-11-22)", ""]
    for page, rows in GLOSS.items():
        L += [f"## /{page}/", ""]
        for zh, en in rows:
            L += [f"- {re.sub(r'<[^>]+>', '', zh)}", f"  - *{re.sub(r'<[^>]+>', '', en)}*"]
        L.append("")
    open(GLOSS_OUT, "w", encoding="utf-8").write("\n".join(L))
    print("  gloss:", GLOSS_OUT)


if __name__ == "__main__":
    main()
