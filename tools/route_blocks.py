#!/usr/bin/env python3
"""AE:ROUTE blocks — the "what next" section on the site's traffic pages, pointing INTO
the practice pages and the exam pages that were slipping.

Why (GA4 2026-08-15→09-11): the four biggest organic landing pages (kk-phonetic-chart
1,219 sessions, moe-1200 734, phonics-rules-chart 716, irregular-verbs 352) sent ZERO
page views to any practice page — practice traffic came from Google (355), ket-prep-guide
(203), /exams/ (192) and the hub (153) only. The names page had no internal exit at all.
Every route below is a practice page or exam page chosen to match what the reader just
finished, plus one score/lookup page.

One block per page, inserted (or replaced) right before the page's closing bg-blue CTA
section. Re-runnable; this script owns every <!-- AE:ROUTE --> block from 2026-09-13.
Run tools/seo_build.py afterwards.
"""
import os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BTN = ('<a href="{href}" style="display:inline-block;font-family:\'Baloo 2\',sans-serif;font-weight:700;font-size:14.5px;'
       'color:var(--navy);background:#fff;border:2px solid var(--light-blue);border-radius:100px;padding:9px 18px;'
       'text-decoration:none;margin:0 8px 8px 0">{label}</a>')

# page → (eyebrow, h2 with <em>, body, [(label, href)])
ROUTES = {
 "kk-phonetic-chart": ("查完音標，下一步", "會看音標了，<em>聽得出來嗎？</em>",
   "音標表回答「這個字怎麼唸」；聽力考的是反過來——聽到聲音，認出是哪個字。KET 聽力 Part 1 是看圖三選一，五題、附音檔與逐字稿，做完就知道孩子的耳朵跟不跟得上。全部免費，不用註冊。",
   [("KET 聽力 Part 1 免費練習", "/ket-listening-practice-part1/"), ("Starters 聽力 看圖三選一", "/starters-listening-practice-part3/"),
    ("KET 題庫總覽（14 頁）", "/ket-practice-tests/"), ("KET 分數計算機", "/ket-score-calculator/")]),
 "phonics-rules-chart": ("規則會了，下一步", "自然發音學完，<em>拼得出來嗎？</em>",
   "自然發音的驗收方式不是背規則，是拼字：聽到 c-a-t 能寫出 cat。Starters 閱讀與寫作 Part 3 就是「排字母拼單字」，五題、每題有圖；KET 聽力 Part 1 則考聽音辨圖。兩份都免費，做完立刻對答案。",
   [("Starters 排字母拼單字", "/starters-rw-practice-part3/"), ("Starters 題庫總覽", "/starters-practice-tests/"),
    ("KET 聽力 Part 1", "/ket-listening-practice-part1/"), ("母音與子音怎麼分", "/english-vowels-consonants/")]),
 "moe-1200-words-guide": ("背完 1200 字之後", "這些字，<em>會用了嗎？</em>",
   "課綱 1200 字的難度大致落在 CEFR A2——也就是劍橋 KET 的範圍。背完不等於會用：KET 閱讀 Part 4「選字填空」考的正是把對的字放進句子裡。做一份免費練習題，再用計算機看換算成劍橋分數是幾分。",
   [("KET 閱讀 Part 4 選字填空", "/ket-rw-practice-part4/"), ("A2 單字情境練習（64 題）", "/a2-vocabulary-practice/"),
    ("KET 題庫總覽（14 頁）", "/ket-practice-tests/"), ("KET 分數計算機", "/ket-score-calculator/")]),
 "irregular-verbs-list": ("三態背完，下一步", "動詞三態，<em>放進句子裡試試</em>",
   "背表格是第一步，考試考的是「這個空格該填哪個時態」。KET 閱讀 Part 5 和 PET 閱讀 Part 6 都是開放式填空——沒有選項，自己寫一個字，動詞時態就是常見考點。免費，每題中文解析。",
   [("KET 閱讀 Part 5 開放填空", "/ket-rw-practice-part5/"), ("PET 閱讀 Part 6 開放式克漏字", "/pet-reading-practice-part6/"),
    ("英文時態總表", "/english-tenses-chart/"), ("PET 題庫總覽（14 頁）", "/pet-practice-tests/")]),
 "happy-birthday-english": ("祝福寫完，下一步", "寫短訊息，<em>其實是考題</em>",
   "生日卡、感謝卡、邀請訊息——這種 25 到 35 字的短訊息，正是劍橋 KET 寫作 Part 6 的題型：讀完情境、回三件事。免費練習題附範文逐句解析，孩子寫完可以直接對照。",
   [("KET 寫作 Part 6 短訊息", "/ket-rw-practice-part6/"), ("英文書信怎麼寫", "/english-letter-writing-guide/"),
    ("KET 題庫總覽（14 頁）", "/ket-practice-tests/"), ("小孩英文自我介紹", "/english-self-introduction-kids/")]),
 "gept-elementary-speaking-writing": ("複試之前", "先做一份<em>免費模擬題</em>",
   "初級複試的口說與寫作，和劍橋 KET 的口說、短訊息寫作程度相當（都是 CEFR A2）。官方歷屆試題怎麼拿、線上題庫怎麼用，整理在全民英檢題庫頁；想多練口說，KET 口說練習有整場對話逐字稿加中文對照。",
   [("全民英檢題庫／歷屆試題", "/gept-practice-tests/"), ("KET 口說練習（逐字稿）", "/ket-speaking-practice/"),
    ("KET vs 全民英檢初級", "/ket-vs-gept-comparison/"), ("成績查詢與放榜時間", "/gept-results-lookup/")]),
 "moe-2000-words-guide": ("2000 字之後", "國中 2000 字 ≈ <em>CEFR B1</em>",
   "課綱 2000 字的範圍，大致對到劍橋 PET（B1 Preliminary）。PET 閱讀 Part 5 是四選一克漏字，考的就是字義與搭配——做一份免費練習題，看孩子的單字是「認得」還是「會用」。",
   [("PET 閱讀 Part 5 克漏字", "/pet-reading-practice-part5/"), ("B1 單字情境練習（64 題）", "/b1-vocabulary-practice/"),
    ("PET 題庫總覽（14 頁）", "/pet-practice-tests/"), ("PET 分數計算機", "/pet-score-calculator/")]),
 "gept-elementary-guide": ("看完考什麼，下一步", "先做題，<em>再決定考不考</em>",
   "初級和劍橋 KET 同樣是 CEFR A2，題型互通：先用免費的線上題庫做一輪，就知道孩子離初試門檻還差多少。兩張證書怎麼選、放榜怎麼查，也一併整理好了。",
   [("全民英檢題庫／歷屆試題", "/gept-practice-tests/"), ("KET 題庫（同為 A2，14 頁免費）", "/ket-practice-tests/"),
    ("KET vs 全民英檢初級", "/ket-vs-gept-comparison/"), ("成績查詢與放榜時間", "/gept-results-lookup/")]),
 "english-alphabet-guide": ("字母會了，下一步", "26 個字母之後，<em>開始拼字</em>",
   "字母認得、唸得出來之後，下一步是把字母拼成字。Starters（劍橋兒童英檢第一級）閱讀與寫作 Part 3 就是「排字母拼單字」，每題有圖、五題一組；單字練習則按主題分組。都免費、不用註冊。",
   [("Starters 排字母拼單字", "/starters-rw-practice-part3/"), ("Starters 單字練習（36 題）", "/starters-vocabulary-practice/"),
    ("Starters 題庫總覽（11 頁）", "/starters-practice-tests/"), ("自然發音規則總表", "/phonics-rules-chart/")]),
 "cool-english-guide": ("酷英之外", "還有<em>80 頁免費模擬試題</em>",
   "酷英的題目是課綱進度；如果想知道孩子在國際標準（CEFR）上落在哪裡，我們依劍橋官方題型自己出了 Starters 到 FCE 六個級別、80 頁的線上練習題，每題中文解析，全部免費。全民英檢的官方題庫也整理好了。",
   [("劍橋英檢題庫總表（80 頁）", "/cambridge-practice-tests/"), ("全民英檢題庫／歷屆試題", "/gept-practice-tests/"),
    ("教育部 1200 字完整字表", "/moe-1200-words-guide/"), ("Starters 題庫（第一級）", "/starters-practice-tests/")]),
 "english-names-boys": ("名字選好了，下一步", "用新名字<em>開口說第一句</em>",
   "名字選好，下一件事就是讓孩子習慣用它介紹自己：「Hi, I'm Leo.」我們整理了小孩英文自我介紹的句型與範例；Starters 口說練習則是劍橋兒童英檢第一級的完整流程——考官第一個問題就是 What's your name?",
   [("小孩英文自我介紹", "/english-self-introduction-kids/"), ("女生英文名字完整清單", "/english-names-girls/"),
    ("取名原則與地雷", "/kids-english-names-guide/"), ("Starters 口說練習", "/starters-speaking-practice/")]),
 "english-names-girls": ("名字選好了，下一步", "用新名字<em>開口說第一句</em>",
   "名字選好，下一件事就是讓孩子習慣用它介紹自己：「Hi, I'm Lily.」我們整理了小孩英文自我介紹的句型與範例；Starters 口說練習則是劍橋兒童英檢第一級的完整流程——考官第一個問題就是 What's your name?",
   [("小孩英文自我介紹", "/english-self-introduction-kids/"), ("男生英文名字完整清單", "/english-names-boys/"),
    ("取名原則與地雷", "/kids-english-names-guide/"), ("Starters 口說練習", "/starters-speaking-practice/")]),
 "kids-english-names-guide": ("原則看完，選名字", "完整清單<em>在這裡</em>",
   "男生 300+、女生 300 個常用名字，每個附中文唸法、意思與來源，可以依開頭字母、音節、風格篩選，點名字聽美式發音。選好之後，用自我介紹的句型讓孩子開口。",
   [("男生英文名字完整清單", "/english-names-boys/"), ("女生英文名字完整清單", "/english-names-girls/"),
    ("小孩英文自我介紹", "/english-self-introduction-kids/"), ("Starters 口說練習", "/starters-speaking-practice/")]),
 "english-tenses-chart": ("時態表看完，下一步", "時態，<em>考題怎麼考？</em>",
   "時態在劍橋考試裡不會單獨出現，而是藏在填空裡：KET 閱讀 Part 5 開放填空（A2）、FCE 英語運用 Part 4 關鍵字轉換（B2）都是動詞形式的重災區。免費練習題，每題中文解析。",
   [("KET 閱讀 Part 5 開放填空", "/ket-rw-practice-part5/"), ("FCE 英語運用 Part 4 關鍵字轉換", "/fce-ruoe-practice-part4/"),
    ("不規則動詞三態表", "/irregular-verbs-list/"), ("PET 題庫總覽（14 頁）", "/pet-practice-tests/")]),
 "english-self-introduction-kids": ("自我介紹練完，下一步", "口說考試，<em>就是從自我介紹開始</em>",
   "劍橋兒童英檢與 KET 的口說第一部分，考官問的正是名字、年齡、學校、喜歡什麼——和這一頁練的一樣。整場對話的逐字稿加中文對照都在練習頁，可以照著模擬。",
   [("KET 口說練習（逐字稿）", "/ket-speaking-practice/"), ("Starters 口說練習", "/starters-speaking-practice/"),
    ("KET 題庫總覽（14 頁）", "/ket-practice-tests/"), ("英文名字怎麼取", "/kids-english-names-guide/")]),
 "english-dates-guide": ("日期會說了，下一步", "聽力考日期，<em>就是這一題</em>",
   "日期、時間、數字，在 KET 聽力 Part 2「筆記填空」裡幾乎每次都考——聽對話、把日期或數字填進表格。五題、附音檔與逐字稿，免費。另外，劍橋英檢每一級的考試日期也整理在報名頁。",
   [("KET 聽力 Part 2 筆記填空", "/ket-listening-practice-part2/"), ("KET 題庫總覽（14 頁）", "/ket-practice-tests/"),
    ("劍橋英檢 2026 考試日期", "/cambridge-exam-registration-taiwan/"), ("英文書信怎麼寫日期", "/english-letter-writing-guide/")]),
 "kk-phonetics-vs-phonics": ("選完方法，下一步", "不管學哪一種，<em>用聽力驗收</em>",
   "KK 或自然發音，最後都要能「聽到就認得、看到就唸得出」。KET 聽力 Part 1 看圖三選一是最直接的驗收；兩張總表也在這裡。",
   [("KET 聽力 Part 1 免費練習", "/ket-listening-practice-part1/"), ("KK 音標表", "/kk-phonetic-chart/"),
    ("自然發音規則總表", "/phonics-rules-chart/"), ("KET 題庫總覽（14 頁）", "/ket-practice-tests/")]),
 "gept-results-lookup": ("查完成績，下一步", "下一次，<em>準備得更有方向</em>",
   "成績出來之後，最有用的一件事是弄清楚差在哪一項。官方歷屆試題與線上題庫的用法在題庫頁；如果在考慮換考劍橋 KET（同為 A2、四項一次考完），比較與換算也整理好了。",
   [("全民英檢題庫／歷屆試題", "/gept-practice-tests/"), ("初級複試口說與寫作", "/gept-elementary-speaking-writing/"),
    ("KET vs 全民英檢初級", "/ket-vs-gept-comparison/"), ("劍橋英檢成績查詢", "/cambridge-results-lookup/")]),
 "cambridge-exam-registration-taiwan": ("報名前，先做題", "報名之前，<em>先確認程度對不對</em>",
   "報錯級別是最常見的浪費：太簡單拿不到高盾、太難直接挫折。每一級都有免費的線上模擬試題，做一份、輸入計算機，就知道該報哪一級。",
   [("劍橋英檢題庫總表（80 頁）", "/cambridge-practice-tests/"), ("KET 題庫", "/ket-practice-tests/"),
    ("PET 題庫", "/pet-practice-tests/"), ("劍橋英檢等級對照表", "/cambridge-english-levels/")]),
 "ket-vs-gept-comparison": ("比較完，做題看看", "兩張證書，<em>先用免費題目試一下</em>",
   "光看對照表很難感覺差別；兩邊的免費題目各做一份，孩子自己就會告訴你哪一種題型比較順。KET 的 14 頁線上題庫與全民英檢的官方題庫都免費。",
   [("KET 題庫（14 頁免費）", "/ket-practice-tests/"), ("全民英檢題庫／歷屆試題", "/gept-practice-tests/"),
    ("KET 分數計算機", "/ket-score-calculator/"), ("劍橋英檢等級對照表", "/cambridge-english-levels/")]),
 "cambridge-english-levels": ("對照表看完，下一步", "哪一級適合？<em>做題就知道</em>",
   "等級對照表是地圖，不是答案。六個級別各有免費的線上模擬試題：從孩子目前上課的程度做起，穩定拿到七成以上再往上試一級。",
   [("Starters 題庫（第一級）", "/starters-practice-tests/"), ("KET 題庫（A2）", "/ket-practice-tests/"),
    ("PET 題庫（B1）", "/pet-practice-tests/"), ("劍橋英檢值不值得考", "/cambridge-exam-worth-it/")]),
}


def block(eyebrow, h2, body, links):
    btns = "".join(BTN.format(href=h, label=l) for l, h in links)
    return f"""<!-- AE:ROUTE -->
<section class="section bg-soft">
  <div class="wrap">
    <span class="eyebrow eyebrow-yellow">{eyebrow}</span>
    <h2 style="margin-top:14px">{h2}</h2>
    <div class="divider" style="margin:18px 0 22px"></div>
    <p class="body" style="max-width:720px">{body}</p>
    <div style="margin-top:20px">{btns}</div>
  </div>
</section>
<!-- /AE:ROUTE -->
"""


def main():
    missing = []
    for page, (eyebrow, h2, body, links) in ROUTES.items():
        p = os.path.join(SITE, page, "index.html")
        if not os.path.isfile(p):
            print(f"  no page: {page}"); continue
        for _, h in links:
            if not os.path.isfile(os.path.join(SITE, h.strip("/"), "index.html")):
                missing.append((page, h))
        s = open(p, encoding="utf-8").read()
        blk = block(eyebrow, h2, body, links)
        if "<!-- AE:ROUTE -->" in s:
            s2 = re.sub(r"<!-- AE:ROUTE -->.*?<!-- /AE:ROUTE -->\n?", lambda m: blk, s, count=1, flags=re.S)
            how = "replaced"
        else:
            i = s.rfind('<section class="section bg-blue">')
            if i < 0:
                print(f"  no bg-blue anchor: {page}"); continue
            s2 = s[:i] + blk + s[i:]
            how = "inserted"
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
        print(f"  {how:8s} /{page}/  → {', '.join(h for _, h in links)}")
    if missing:
        sys.exit("BROKEN route targets: " + ", ".join(f"{p}→{h}" for p, h in missing))


if __name__ == "__main__":
    main()
