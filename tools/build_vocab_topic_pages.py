#!/usr/bin/env python3
"""
Topic-vocabulary pages — Wave 2 of the capture portfolio.

Eight small pools (英文月份 3.74, 國家英文 3.21, 英文數字 5.04, 顏色英文 1.28,
職業英文 1.23, 星期英文 1.21, 水果英文 1.19, 身體部位英文 0.49) share one page
shape, so they share one template. Combined they are the largest reachable block
on the demand map — bigger than any single pool except TOEIC.

Running order follows the page that actually holds #1 for 英文月份: the lookup table
comes FIRST (it is what the reader came for), then the confusions people really type,
then depth, an adjacent topic, usage rules, FAQ, offer. Pages are generated, so the
word lists live in tools/data/vocab_topics.json — never hand-edit the HTML.

Usage:  python3 tools/build_vocab_topic_pages.py [slug ...]
        then tools/build_chart_images.py and tools/build_word_audio.py
"""
import os, re, json, html, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(SITE, "tools/data/vocab_topics.json"), encoding="utf-8"))
SHELL = os.path.join(SITE, "kk-phonetic-chart/index.html")
ORIGIN = "https://americanenglish.com.tw"

def tbl(rows, heads):
    h = "".join(f"<th>{x}</th>" for x in heads)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>"
                   for r in rows)
    return f'<div class="compare reveal"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'

def grouped(groups, heads):
    out = []
    for name, rows in groups:
        out.append(f'<h3>{html.escape(name)}</h3>')
        out.append(tbl([list(r) for r in rows], heads))
    return "\n".join(out)

def sec(title, inner, soft=False):
    return (f'<section class="section{" bg-soft" if soft else ""}"><div class="wrap">'
            f'<div class="center stack reveal"><h2>{title}</h2></div>{inner}</div></section>')

def prose(*ps):
    return '<div class="prose reveal">' + "".join(f"<p>{p}</p>" for p in ps) + "</div>"

def faq(items):
    # The site's FAQ shape is h3.faq-h > button.faq-q, and .faq-a wraps its text in <p>.
    # seo_build.py's faq_ld() selects .faq-q, so a bare <h3> yields no FAQPage schema and
    # no accordion — this markup is not cosmetic.
    inner = "".join(
        f'<div class="faq-item"><h3 class="faq-h">'
        f'<button class="faq-q" aria-expanded="false">{q}<span class="pm"></span></button>'
        f'</h3><div class="faq-a"><p>{a}</p></div></div>' for q, a in items)
    return f'<div class="faq">{inner}</div>'

def cta(line):
    # bg-blue is the site's closing-CTA convention and the anchor route_blocks.py
    # inserts its "what next" section before — without it the page gets no route block.
    return ('<section class="section bg-blue"><div class="wrap"><div class="center stack reveal">'
            f'<h2>單字背起來了，用得出來嗎？</h2><p class="body">{line}</p>'
            '<a class="btn btn-primary" href="/line/">預約免費試上一堂</a></div></div></section>')

N  = DATA["numbers"]; M = DATA["months"]; D = DATA["days"]

PAGES = {
"english-numbers-guide": dict(
  target="英文數字", index=5.04,
  h1="英文數字 1-100 完整對照表：唸法、拼法與 13／30 的分辨方法",
  title="英文數字1-100對照表：唸法、拼法與13／30怎麼分｜埃森美語",
  desc="英文數字 0 到 100 完整對照表，每個數字附英文拼法與中文。另有 -teen 與 -ty 的重音分辨法（13 還是 30）、序數與基數的差別、連字號規則與唸電話號碼的方式——美籍持證教師整理，可點聽發音。",
  hero="英文數字看起來簡單，真正會卡住的只有三個地方：13 和 30 分不出來、超過 20 忘記加連字號、序數和基數搞混。下面先給完整的 0–100 對照表，再逐一拆這三個問題。",
  body=lambda: (
    sec("0-100 完整對照表",
      prose("每個數字都附中文與阿拉伯數字，可以直接點喇叭聽發音。20 以後的規則是固定的：<strong>幾十 + 連字號 + 個位數</strong>，例如 21 是 twenty-one、47 是 forty-seven。")
      + tbl([[r["extra"], r["en"], r["zh"]] for r in N], ["數字", "英文", "中文"]))
    + sec("13 還是 30？台灣學生最常聽錯的一組",
      prose("這組是聽力考試的固定考點，也是點餐、報價、聽門牌號碼時最容易出錯的地方。差別<strong>不在字母，在重音</strong>：",
        "<strong>-teen 結尾（13–19）重音在後面</strong>：thir<em>TEEN</em>、four<em>TEEN</em>、fif<em>TEEN</em>，最後一個音節唸得又長又響。<br>"
        "<strong>-ty 結尾（20–90）重音在前面</strong>：<em>THIR</em>-ty、<em>FOR</em>-ty、<em>FIF</em>-ty，尾巴輕輕帶過。",
        "還有一個輔助線索：-teen 的尾音是清楚的 /n/，-ty 的尾音在美式英語裡常被唸成輕彈音，聽起來接近 /d/——thirty 聽起來像「thir-dee」。兩個線索一起用，幾乎不會錯。"), soft=True)
    + sec("拼字規則：連字號、不規則拼法與 hundred",
      prose("<strong>連字號只用在 21–99 之間的兩位數</strong>：twenty-one、fifty-six、ninety-nine。整十（twenty、thirty）和一百（one hundred）都不加。",
        "<strong>四個不規則拼法要單獨記</strong>：four 有 u，但 forty <em>沒有</em> u（不是 fourty）；five 變 fifteen 和 fifty；nine 變 ninety（去掉 e）；eight 加 h 變 eighteen、eighty。",
        "<strong>hundred 不加 s</strong>：two hundred 不是 two hundreds。只有在表示「數百個」這種模糊數量時才用複數：hundreds of people（好幾百人）。"))
    + sec("序數：first、second、third 怎麼用",
      prose("基數（cardinal）回答「幾個」，序數（ordinal）回答「第幾」。日期、樓層、名次、生日都用序數：<strong>May 5th</strong>、the <strong>3rd</strong> floor、he came <strong>2nd</strong>。",
        "前三個不規則：one→first、two→second、three→third。之後大多加 -th：fourth、fifth（注意拼法）、sixth、seventh、eighth（只加 h）、ninth（去 e）、twelfth（ve→f）。"
        "幾十的序數把 y 換成 ie 再加 th：twenty→twentieth、forty→fortieth。完整用法整理在 <a href=\"/ordinal-numbers-english/\">英文序數</a>。"), soft=True)
    + sec("數字的實際唸法：電話、年份與小數",
      prose("<strong>電話號碼</strong>一個數字一個數字唸，0 唸成 “oh” 或 “zero”；連續兩個相同數字可以用 double：0932 唸 “oh nine three two”。",
        "<strong>年份</strong>通常拆成兩半：1998 唸 nineteen ninety-eight；2026 唸 twenty twenty-six 或 two thousand twenty-six。",
        "<strong>小數</strong>的點唸 point，後面一位一位唸：3.14 是 three point one four。<strong>金額</strong>則把單位放中間：$5.50 唸 five fifty 或 five dollars and fifty cents。"))
    + sec("英文數字常見問題", faq([
      ("13 和 30 到底怎麼分？", "聽重音。13 是 thir<em>TEEN</em>，重音在後；30 是 <em>THIR</em>-ty，重音在前。美式英語裡 thirty 的 t 還會弱化成接近 /d/ 的輕彈音，聽起來像「thir-dee」。念不確定時，可以改說 “one three” 或 “three zero” 確認。"),
      ("為什麼是 forty 不是 fourty？", "這是英文拼字史上的一個例外，沒有規則可循，只能記。four、fourteen 都有 u，唯獨 forty 沒有。同類要單獨記的還有 five→fifteen／fifty、nine→ninety。"),
      ("100 要說 one hundred 還是 a hundred？", "兩個都對。a hundred 比較口語，one hundred 比較正式、也用在需要強調數量的時候。但前面有其他數字時只能用 one：one hundred and twenty（120）。"),
      ("英文數字要加連字號嗎？", "21 到 99 之間的兩位數要：twenty-one、ninety-nine。整十和一百以上不用。寫作文時這個細節常被扣分。"),
      ("幾歲開始教英文數字比較好？", "學齡前就可以從 1–10 的口語開始，重點是聽和說，不是拼。國小低年級加到 20 並開始認字形，中年級再處理 -teen／-ty 的重音差別與序數——那時候孩子的聽辨能力才跟得上。"),
      ("零要唸 zero 還是 oh？", "報電話號碼、房號、年份時唸 “oh”；數學、運動比分、溫度唸 zero。球類比賽的 0 分在英式英語還會唸成 nil，網球則是 love。"),
    ]), soft=True)
    + cta("數字是最早學、也最早忘記怎麼「用」的一課。我們的課堂用點餐、報時間、比價這些真實情境練，孩子講出來的不是背過的表，是能用的句子。")),
  faq_n=6),

"months-english": dict(
  target="英文月份", index=3.74,
  h1="1-12 月份英文對照表：縮寫、唸法與 in／on 用法一次搞懂",
  title="月份英文1-12月：縮寫、唸法、日期寫法與介系詞用法｜埃森美語",
  desc="1 到 12 月的英文與縮寫完整對照，附天數與唸法；Feb.、Apr.、May、Jun. 常見縮寫一次查清楚，並說明月份前面用 in 還是 on、美式與英式日期寫法的差別——美籍持證教師整理，可點聽發音。",
  hero="月份英文最常被問的其實不是「三月怎麼說」，而是「Jun. 是六月還是七月」「日期前面要用 in 還是 on」。下面先給完整對照表，再把這幾個實際會用到的問題講清楚。",
  body=lambda: (
    sec("1-12 月英文對照表",
      prose("縮寫規則很一致：<strong>取前三個字母加句點</strong>。唯一的例外是 May——它只有三個字母，所以不縮寫、也不加點。September 兩種縮寫都通行（Sep. 與 Sept.）。")
      + tbl([[f"{i+1} 月", m[0], m[1], m[2], m[3]] for i, m in enumerate(M)],
            ["月份", "英文", "中文", "縮寫", "天數"]))
    + sec("Feb.、Apr.、May、Jun. 各是幾月？",
      prose("這四個是查詢量最高的，因為它們彼此看起來很像：<br>"
        "<strong>Jan.</strong> 一月　<strong>Feb.</strong> 二月　<strong>Mar.</strong> 三月　<strong>Apr.</strong> 四月<br>"
        "<strong>May</strong> 五月（不縮寫）　<strong>Jun.</strong> 六月　<strong>Jul.</strong> 七月　<strong>Aug.</strong> 八月<br>"
        "<strong>Sep./Sept.</strong> 九月　<strong>Oct.</strong> 十月　<strong>Nov.</strong> 十一月　<strong>Dec.</strong> 十二月",
        "最容易混的是 <strong>Jun. 和 Jul.</strong>（六月與七月）、<strong>Mar. 和 May</strong>（三月與五月）。記法：六月 June 和七月 July 都是 J 開頭，<em>Jun</em>e 的 n 在前、<em>Jul</em>y 的 l 在後，照字母順序排就對了。"), soft=True)
    + sec("月份前面用 in 還是 on？",
      prose("這是月份最常錯的地方，規則其實只有一條：<strong>範圍越大用 in，越精確用 on</strong>。",
        "<strong>in + 月份</strong>（只講月，不講日）：in May、in December。<br>"
        "<strong>on + 完整日期</strong>（有日）：on May 5、on December 25th。<br>"
        "<strong>from…to…</strong> 表示期間：from March to June。",
        "同一條規則也適用年份（in 2026）、季節（in summer）與星期（on Monday）。想一次看完，可以讀 <a href=\"/days-of-week-english/\">星期英文</a>。"))
    + sec("日期寫法：美式與英式差在哪",
      prose("<strong>美式</strong>是「月-日-年」：May 5, 2026，縮寫成 5/5/2026 時月份在前。<br>"
        "<strong>英式</strong>是「日-月-年」：5 May 2026，縮寫成 5/5/2026 時日在前。",
        "所以 <strong>03/04/2026</strong> 在美國是三月四日、在英國是四月三日——完全不同的兩天。寫給國外的信件或報名表，最安全的做法是<strong>把月份拼出來</strong>：4 March 2026，這樣沒有任何誤會空間。",
        "台灣的學校與官方文件多採英式或 ISO 格式（2026-03-04）。劍橋與全民英檢的報名表通常會標明格式，填之前先看一眼。"), soft=True)
    + sec("月份的由來：為什麼九月是 September",
      prose("英文月份幾乎都來自拉丁文與羅馬神話，知道由來會好記很多：<strong>January</strong> 來自雙面神 Janus（門與開始）、<strong>March</strong> 來自戰神 Mars、<strong>July</strong> 紀念凱撒 Julius Caesar、<strong>August</strong> 紀念奧古斯都 Augustus。",
        "最有趣的是 9 到 12 月：<strong>Sept-</strong>（七）、<strong>Oct-</strong>（八）、<strong>Nov-</strong>（九）、<strong>Dec-</strong>（十）。這些字根和月份數字差了兩位，因為古羅馬曆一年只有十個月、從三月開始算。"
        "同樣的字根今天還在用：octopus（八爪章魚）、decade（十年），記住字根就同時記住兩組字。"))
    + sec("月份英文常見問題", faq([
      ("月份的英文開頭要大寫嗎？", "要。英文的月份和星期都是專有名詞，句中也一定大寫：I was born in <em>May</em>。這是作文最常被扣分的小細節之一，季節（spring、summer）則<strong>不</strong>大寫。"),
      ("May 為什麼沒有縮寫？", "因為它本身只有三個字母，縮寫不會比較短。同樣道理，短的月份不縮寫；縮寫要加句點，代表後面還有字母被省略——May 沒有省略任何字母，所以也不加點。"),
      ("Sep. 和 Sept. 哪一個對？", "兩個都對。Sept. 在英式英語較常見，Sep. 在美式與資訊系統中較常見。同一份文件裡選一種用到底就好。"),
      ("in May 還是 on May？", "只講月份用 in（in May）；有指定到哪一天才用 on（on May 5）。判斷方式很簡單：句子裡有沒有日期數字。"),
      ("月份要怎麼幫孩子記？", "不要一次背十二個。先記和孩子有關的三個——生日的月份、開學的九月、過年的一二月——有情境就記得住。接著用字根補上 9 到 12 月，最後再處理縮寫。"),
      ("寫日期時 5 要寫成 5th 嗎？", "口說一定唸序數（May fifth），書寫則兩種都可以：May 5 和 May 5th 都正確，美式正式文件偏好不加 th。重點是同一份文件保持一致。"),
    ]), soft=True)
    + cta("月份、日期、時間這種「每天都會用到」的英文，最怕只認得字、講不出口。我們的小班課每堂都有真實情境的口說練習，講錯當場就被美籍老師接住。")),
  faq_n=6),

"days-of-week-english": dict(
  target="星期英文", index=1.21,
  h1="星期英文對照表：七天的唸法、縮寫與 on Monday 的用法",
  title="星期英文：一到日對照表、縮寫、唸法與介系詞用法｜埃森美語",
  desc="星期一到星期日的英文、縮寫與中文完整對照；說明為什麼星期要大寫、on Monday 與 on Mondays 的差別、weekday 與 weekend 怎麼用，以及七天名稱的北歐神話由來——美籍持證教師整理，可點聽發音。",
  hero="星期只有七個字，卻是國小英文最早考、也最常拼錯的一組。難點不在背，在三件事：大寫、縮寫，以及「星期一」和「每個星期一」在英文裡是兩個不同的說法。",
  body=lambda: (
    sec("星期英文完整對照表",
      prose("縮寫一樣是取前三個字母加句點。Tuesday 和 Thursday 因為都是 T 開頭，常見四個字母的縮寫（Tues.、Thurs.）以免混淆。")
      + tbl([[d[0], d[1], d[2], d[3]] for d in D], ["英文", "中文", "縮寫", "口語"]))
    + sec("星期一定要大寫",
      prose("英文的星期是<strong>專有名詞</strong>，不管出現在句子哪個位置都要大寫：See you on <em>Friday</em>。這一條和月份相同，也是台灣學生作文最常見的扣分點。",
        "對照組：季節（spring、summer、autumn、winter）和一天的時段（morning、afternoon、evening）都是普通名詞，<strong>不</strong>大寫。"), soft=True)
    + sec("on Monday 和 on Mondays 差在哪",
      prose("差一個 s，意思完全不同：",
        "<strong>on Monday</strong> = 這個星期一（特定的某一天）。<em>I have a test on Monday.</em><br>"
        "<strong>on Mondays</strong> = 每個星期一（習慣、規律）。<em>I have English class on Mondays.</em><br>"
        "也可以寫成 <strong>every Monday</strong>，意思一樣但更強調。",
        "另外三個常用說法：<strong>this Monday</strong>（本週一）、<strong>next Monday</strong>（下週一）、<strong>last Monday</strong>（上週一）——這三個前面<strong>不加</strong> on。月份的 in／on 規則整理在 <a href=\"/months-english/\">月份英文</a>。"))
    + sec("weekday、weekend 與一週從哪天開始",
      prose("<strong>weekday</strong> 指週一到週五的上班上課日；<strong>weekend</strong> 指週六與週日。注意介系詞：美式用 <em>on the weekend</em>，英式用 <em>at the weekend</em>，兩個都對。",
        "一週從哪天開始其實沒有標準答案：美國、加拿大、日本的月曆多從<strong>星期日</strong>開始；歐洲與 ISO 國際標準從<strong>星期一</strong>開始。台灣的月曆兩種都看得到。填國外表格遇到 “first day of week” 時，看它自己的月曆怎麼排最準。"), soft=True)
    + sec("七天的名字從哪來",
      prose("英文的星期名稱一半來自北歐神話、一半來自天體，記住由來就不容易拼錯：",
        "<strong>Sunday</strong> 太陽日、<strong>Monday</strong> 月亮日（Moon-day）、<strong>Tuesday</strong> 戰神 Tyr、"
        "<strong>Wednesday</strong> 主神 Odin（Woden's day，所以中間那個不發音的 d 一定要寫）、"
        "<strong>Thursday</strong> 雷神 Thor、<strong>Friday</strong> 愛神 Frigg、<strong>Saturday</strong> 土星 Saturn。",
        "Wednesday 是全班拼字考的頭號殺手。教孩子拆成 <strong>Wed-nes-day</strong> 三段唸出來（明明唸 /ˈwɛnzdeɪ/，但拼的時候刻意唸出中間的 d），一次就記住。"))
    + sec("星期英文常見問題", faq([
      ("星期的英文需要大寫嗎？", "需要，任何位置都要。星期和月份都是專有名詞。季節和早中晚則不用大寫，這組對比常出現在考題裡。"),
      ("Wednesday 為什麼有不發音的 d？", "它來自北歐主神 Odin 的古英文名 Woden——Woden's day。發音隨著時間簡化成 /ˈwɛnzdeɪ/，拼字卻保留了原本的 d。拼的時候刻意唸成「Wed-nes-day」就不會漏。"),
      ("on Monday 和 on Mondays 有什麼不同？", "on Monday 指特定的這個星期一；on Mondays（或 every Monday）指每週固定的星期一。講課表、社團、固定行程用複數。"),
      ("this Monday 前面要加 on 嗎？", "不用。this／next／last 開頭的時間片語本身就當副詞用：See you next Monday，不是 on next Monday。"),
      ("一週的第一天是星期日還是星期一？", "看標準。美式月曆和日本多從星期日起算，歐洲與 ISO 8601 國際標準從星期一起算。台灣兩種都有，填表時以該表自己的月曆為準。"),
      ("孩子怎麼記七天最快？", "配課表記，不要照順序背。把孩子每天實際在做的事接上去——Monday 有英文課、Wednesday 要游泳——七天兩三天就記熟，而且是能用的。"),
    ]), soft=True)
    + cta("星期、月份、時間這些字，真正的驗收是「聽到就反應得過來」。我們的課堂每天用英文問行程，孩子想的時間會越來越短。")),
  faq_n=6),
}

PAGES.update({
"colors-english-vocabulary": dict(
  target="顏色英文", index=1.28,
  h1="顏色英文對照表：62 個常用顏色、深淺說法與 color／colour 的差別",
  title="顏色英文62個對照表：深淺說法、拼法差異與形容詞順序｜埃森美語",
  desc="顏色英文完整對照表，收錄 62 個常用顏色與中文對照，分基本色、深淺、紅粉紫、黃橙棕與藍綠五組；並說明 color 與 colour 的拼法差別、light／dark 的用法，以及顏色在形容詞裡的正確位置。",
  hero="顏色是孩子最早學會的一批英文單字，但大多數人停在十個基本色就沒再往下走。下面這份表收了 62 個，分成五組——先給表，再講三個真正會用到的規則。",
  body=lambda: (
    sec("顏色英文對照表（62 個）",
      prose("按色系分組，找起來比按字母快。深淺的說法在第二組，實際寫作最常用到。")
      + grouped([(g[0], [[w, z] for w, z in g[1]]) for g in DATA["colors"]], ["英文", "中文"]))
    + sec("color 還是 colour？",
      prose("<strong>color 是美式，colour 是英式</strong>，兩個都正確。同一組差異還有 gray（美）／grey（英）。",
        "台灣的審定教科書（康軒、翰林、南一）採<strong>美式</strong>拼法，多益也是美式；劍橋與全民英檢兩種都接受。"
        "我們教的是美式英語，所以本頁一律以美式拼法為主。考試不會因為你用另一套而扣分，但<strong>同一篇文章裡必須一致</strong>——這才是真正會被扣分的地方。"), soft=True)
    + sec("深淺怎麼說：light、dark 與 -ish",
      prose("<strong>light + 顏色</strong> = 淺（light blue 淺藍）；<strong>dark + 顏色</strong> = 深（dark green 深綠）。",
        "<strong>pale</strong> 比 light 更淡、偏無血色；<strong>bright</strong> 是鮮豔；<strong>deep</strong> 比 dark 更濃郁。",
        "口語裡還有一個好用的字尾 <strong>-ish</strong>，表示「有點…色的」：reddish（偏紅）、greenish（帶點綠）。不確定是什麼顏色時特別好用。"))
    + sec("顏色放在形容詞的哪個位置",
      prose("英文形容詞有固定順序，顏色排在<strong>倒數第三</strong>：<em>數量 → 評價 → 大小 → 形狀 → 年齡 → 顏色 → 來源 → 材質 → 用途 → 名詞</em>。",
        "所以是 <strong>a big old red wooden box</strong>，不是 a red old big wooden box。母語者不會背這個順序，但講錯會立刻聽出來。",
        "實務上很少同時用到五個形容詞，記住「<strong>顏色永遠緊貼在材質前面</strong>」就夠應付大部分句子。"), soft=True)
    + sec("顏色英文常見問題", faq([
      ("color 和 colour 哪個對？", "都對。color 是美式、colour 是英式，gray／grey 同理。台灣審定教科書與多益用美式，劍橋和全民英檢兩種都收。我們教美式，重點是同一篇文章從頭到尾一致。"),
      ("淺藍色的英文是什麼？", "light blue。更淡可以說 pale blue，天空那種藍是 sky blue，很淺的嬰兒藍是 baby blue。深藍則是 dark blue 或 navy。"),
      ("顏色可以當名詞用嗎？", "可以。Red is my favorite color（紅色是我最喜歡的顏色）裡 red 就是名詞。當形容詞時放在名詞前：a red car。"),
      ("金色銀色算顏色嗎？", "算，gold 和 silver 既是金屬也是顏色。它們同時可以當名詞和形容詞：a gold medal、painted silver。"),
      ("孩子幾歲學顏色最好？", "學齡前就可以，顏色是最容易「指著實物說」的一類字。建議直接在生活裡教——穿衣服、吃水果、玩積木時順口問一句，比看字卡有效得多。"),
      ("為什麼有些顏色要加 -ish？", "-ish 表示「大約、有點」，用在不確定或介於兩色之間時：reddish 偏紅、yellowish 偏黃。這個字尾也能用在其他形容詞上，像 tallish（有點高）。"),
    ]), soft=True)
    + cta("顏色、水果、動物這些字，孩子背得起來卻用不出來，原因通常是從沒在句子裡講過。我們的課堂用實物和遊戲練，說出口的頻率比看字卡高得多。")),
  faq_n=6),

"fruits-english-vocabulary": dict(
  target="水果英文", index=1.19,
  h1="水果英文對照表：47 種水果，含芭樂、蓮霧、釋迦等台灣水果說法",
  title="水果英文47種對照表：台灣水果的英文怎麼說｜埃森美語",
  desc="水果英文完整對照表，收錄 47 種水果與中文對照，特別整理芭樂、蓮霧、釋迦、龍眼、楊桃等台灣常見水果的正確英文說法；並說明水果的可數與不可數、a 與 an 的選擇——美籍持證教師整理。",
  hero="市面上的水果英文表幾乎都是從國外教材直接翻過來的，所以查得到 apple、blueberry，卻查不到芭樂和蓮霧——偏偏那才是台灣孩子天天吃、最想講的。這份表把台灣水果放在第一組。",
  body=lambda: (
    sec("水果英文對照表（47 種）",
      prose("第一組是台灣市場買得到、國外教材通常沒有的水果。這些名稱在英語系國家也通用，點餐或跟外師介紹時直接說就懂。")
      + grouped([(g[0], [[w, z] for w, z in g[1]]) for g in DATA["fruits"]], ["英文", "中文"]))
    + sec("台灣水果的英文，為什麼常常查不到",
      prose("因為很多熱帶水果在英語系國家不常見，名稱沒有完全統一。幾個實用提醒：",
        "<strong>蓮霧</strong>最通行的說法是 wax apple，也有人說 rose apple 或 java apple。<br>"
        "<strong>釋迦</strong>是 sugar apple 或 custard apple（嚴格說是不同品種，但日常混用）。<br>"
        "<strong>芭樂</strong>是 guava，重音在第一音節：<em>GUA</em>-va。<br>"
        "<strong>楊桃</strong>是 star fruit，因為橫切面是星形——這個字孩子一聽就記住。",
        "遇到真的沒有對應字的水果，母語者的做法是<strong>描述它</strong>：It's a bit like a pear, but crunchier. 這比硬記一個沒人用的譯名實用得多。"), soft=True)
    + sec("水果是可數還是不可數",
      prose("<strong>一顆一顆算的水果是可數的</strong>：an apple、two bananas、three oranges。",
        "<strong>切開或當成食材時變不可數</strong>：Would you like some watermelon?（來點西瓜嗎）——這裡不會說 a watermelon，因為指的是切好的果肉。",
        "<strong>a 還是 an 看發音，不是看字母</strong>：an apple、an orange（母音開頭）；a banana、a pear（子音開頭）。注意 <strong>a</strong>n <strong>a</strong>vocado 是 an，但 <strong>a</strong> uniform 卻是 a——因為 uniform 的開頭唸 /j/，是子音。"))
    + sec("水果英文常見問題", faq([
      ("芭樂的英文怎麼說？", "guava，重音在第一音節。這個字在英語系國家通用，果汁和果醬上都看得到，直接說就懂。"),
      ("蓮霧的英文是什麼？", "最通行的是 wax apple（字面「蠟蘋果」，因為表皮光亮）。也有人說 rose apple 或 java apple，三種在英語系國家都有人用。"),
      ("釋迦的英文怎麼說？", "sugar apple 或 custard apple。嚴格說兩者是不同品種，但日常對話裡混用不會造成誤解。台東鳳梨釋迦則常譯為 atemoya。"),
      ("水果前面要加 a 還是 an？", "看開頭的發音：母音開頭用 an（an apple、an orange、an avocado），子音開頭用 a（a banana、a guava）。判斷依據是聲音不是字母。"),
      ("一串香蕉的英文怎麼說？", "a bunch of bananas。其他常用單位：a bunch of grapes（一串葡萄）、a slice of watermelon（一片西瓜）、a basket of strawberries（一籃草莓）。"),
      ("怎麼讓孩子記住水果英文？", "去一趟市場或超市，邊走邊說。水果是最適合實物教學的一類字——看得到、摸得到、吃得到，記憶點比字卡強太多。回家再用那幾個字造一句就夠了。"),
    ]), soft=True)
    + cta("水果、顏色、動物這些生活單字，最好的練法是真的拿來用。我們的小班課用實物和情境對話練，孩子講的是自己的生活，不是課本例句。")),
  faq_n=6),

"body-parts-english": dict(
  target="身體部位英文", index=0.49,
  h1="身體部位英文對照表：43 個部位，含 tooth／teeth 等不規則複數",
  title="身體部位英文對照表：43個部位、不規則複數與看醫生用語｜埃森美語",
  desc="身體部位英文完整對照表，收錄 43 個部位分頭臉、上半身、下半身與體內四組；說明 tooth／teeth、foot／feet 等不規則複數，以及身體部位前面用 my 還是 the——美籍持證教師整理，可點聽發音。",
  hero="身體部位是國小英文的必考單元，也是少數「背了馬上用得到」的字——孩子不舒服、受傷、看醫生時都要講。難點只有兩個：不規則複數，和前面該放 my 還是 the。",
  body=lambda: (
    sec("身體部位英文對照表（43 個）",
      prose("依位置分四組，從頭到腳。體內器官那一組雖然低年級用不到，但健康教育和自然課會出現。")
      + grouped([(g[0], [[w, z] for w, z in g[1]]) for g in DATA["body"]], ["英文", "中文"]))
    + sec("不規則複數：teeth、feet 不加 s",
      prose("身體部位集中了英文最常見的幾個不規則複數，因為它們都是最古老的字：",
        "<strong>tooth → teeth</strong>（牙齒）、<strong>foot → feet</strong>（腳）。這兩個是母音變化，不加 s。",
        "成對的部位平常用複數：my <strong>eyes</strong>、my <strong>hands</strong>、my <strong>feet</strong>。只講其中一邊才用單數，而且通常會指明哪一邊：my <strong>left</strong> hand。",
        "還有一個容易錯的：<strong>hair</strong> 當「頭髮整體」時是不可數，沒有 s——My hair is long，不是 My hairs are long。加了 s 會變成「好幾根分開的毛髮」。"), soft=True)
    + sec("my 還是 the？",
      prose("這是台灣學生最常被糾正的一點。<strong>英文講身體部位時，前面幾乎一定要有所有格</strong>：",
        "<em>I washed <strong>my</strong> hands.</em>（不是 I washed hands）<br>"
        "<em>He broke <strong>his</strong> arm.</em>（不是 He broke arm）",
        "例外是在 <strong>介系詞片語</strong>裡，描述「打到／碰到某人的某部位」時用 the：<em>She hit me on <strong>the</strong> head.</em>、<em>He patted me on <strong>the</strong> back.</em> 這個結構固定，直接當片語記就好。"))
    + sec("身體不舒服怎麼說",
      prose("三個最常用的句型，看醫生和跟外師請假都用得上：",
        "<strong>My + 部位 + hurts.</strong> — My stomach hurts.（我肚子痛）<br>"
        "<strong>I have a + 部位 + ache.</strong> — I have a headache／toothache／stomachache.（注意這幾個是連寫）<br>"
        "<strong>I have a sore + 部位.</strong> — I have a sore throat.（喉嚨痛）",
        "痛的程度：<em>a little</em>（有點）→ <em>quite</em>（蠻）→ <em>really／very</em>（很）。孩子會講這三個級距，表達就夠用了。"), soft=True)
    + sec("身體部位英文常見問題", faq([
      ("牙齒的複數為什麼是 teeth？", "tooth／teeth 和 foot／feet 一樣，是古英文留下來的母音變化複數，不加 s。同類的還有 man／men、woman／women、child／children——都是最常用的老字。"),
      ("頭髮是 hair 還是 hairs？", "講整頭頭髮時不可數，用 hair：My hair is long。加 s 變成「好幾根分開的毛髮」，通常出現在「湯裡有根頭髮」這種語境。"),
      ("為什麼是 wash my hands 不是 wash hands？", "英文提到身體部位時前面要有所有格，說明是誰的。中文可以省略，英文不行——這是中文母語者最常見的漏字之一。"),
      ("hurt、ache、sore 有什麼不同？", "hurt 是動詞（My leg hurts）；ache 多半接在部位後面組成名詞（headache、toothache）；sore 是形容詞，指發炎紅腫的痛（a sore throat）。三個用法不同，但都表示痛。"),
      ("成對的部位要用複數嗎？", "平常講兩隻都算時用複數：my eyes、my feet。只講一邊時用單數並指明左右：my left foot。這一點和中文習慣不同，容易漏。"),
      ("孩子怎麼記身體部位最快？", "用動作記，不要用字卡。Simon Says 這類遊戲讓孩子聽到 touch your nose 就要做出動作——把字和動作綁在一起，比默背快得多，也更接近真實的使用情境。"),
    ]), soft=True)
    + cta("身體部位是孩子真的會用到的字——不舒服、受傷、上體育課都要講。我們的課堂用遊戲和情境練，讓孩子在需要的時候講得出來。")),
  faq_n=6),
})

PAGES.update({
"countries-english": dict(
  target="國家英文", index=3.21,
  h1="國家英文對照表：80 國名稱、國籍形容詞與 the 什麼時候要加",
  title="國家英文對照表：80國名稱、國籍說法與the的用法｜埃森美語",
  desc="國家英文完整對照表，收錄 80 個國家的英文名稱、中文與國籍形容詞，依亞洲、歐洲、美洲、非洲中東與大洋洲分組；並說明哪些國名前面要加 the、國家與國籍與語言的差別——美籍持證教師整理。",
  hero="國家英文最常錯的不是國名本身，是後面那一串：台灣是 Taiwan，台灣人卻不是 Taiwan people；英國前面要加 the，日本卻不用。下面先給對照表，再把這兩件事講清楚。",
  body=lambda: (
    sec("國家與國籍對照表（80 國）",
      prose("每一列都有三欄：<strong>國家</strong>、中文、以及<strong>國籍形容詞</strong>——後者同時用來說「哪裡人」和「哪一國的」。")
      + grouped([(g[0], [[a, b, c] for a, b, c in g[1]]) for g in DATA["countries"]],
                ["國家 Country", "中文", "國籍 Nationality"]))
    + sec("哪些國名前面要加 the",
      prose("規則其實很乾淨，只有三類國名要加 <strong>the</strong>：",
        "<strong>一、國名是複數</strong>：<em>the</em> Philippines、<em>the</em> Netherlands、<em>the</em> Marshall Islands。<br>"
        "<strong>二、國名裡有 States／Kingdom／Republic／Emirates 這類普通名詞</strong>："
        "<em>the</em> United States、<em>the</em> United Kingdom、<em>the</em> United Arab Emirates。<br>"
        "<strong>三、少數習慣用法</strong>：the Gambia、the Bahamas。",
        "其他單一名稱的國家一律<strong>不加</strong>：Japan、France、Taiwan、Brazil。"
        "一個好記的檢查法：如果國名可以拆成「形容詞＋普通名詞」（united + states），就要 the。"), soft=True)
    + sec("國家、國籍、語言：三個不一樣的字",
      prose("中文說「他是日本人、他說日文」都用同一個「日」字，英文卻可能是三個形態：",
        "<strong>Japan</strong>（國家）→ <strong>Japanese</strong>（日本人／日本的）→ <strong>Japanese</strong>（日文）——這組剛好相同。<br>"
        "<strong>Spain</strong>（國家）→ <strong>Spanish</strong>（西班牙人／的）→ <strong>Spanish</strong>（西班牙文）。<br>"
        "但 <strong>the Netherlands</strong>（國家）→ <strong>Dutch</strong>（荷蘭人／的）→ <strong>Dutch</strong>（荷蘭文）——國名和形容詞完全不同字，這類要單獨記。",
        "還有一個常錯：<strong>國籍形容詞開頭一定大寫</strong>，因為它是專有形容詞——I'm <em>Taiwanese</em>，不是 taiwanese。"))
    + sec("國籍形容詞的字尾規律",
      prose("大部分國籍形容詞照四種字尾走，記住規律比一個一個背快：",
        "<strong>-an／-ian</strong>（最多）：American、Italian、Korean、Canadian、Brazilian、Russian。<br>"
        "<strong>-ese</strong>（多為亞洲與葡語系）：Taiwanese、Japanese、Chinese、Vietnamese、Portuguese。<br>"
        "<strong>-ish</strong>（多為歐洲）：British、Spanish、Polish、Turkish、Danish、Swedish。<br>"
        "<strong>-i</strong>（多為中東）：Israeli、Iraqi、Pakistani、Saudi、Emirati。",
        "少數完全不規則：France→<strong>French</strong>、the Netherlands→<strong>Dutch</strong>、"
        "Greece→<strong>Greek</strong>、Switzerland→<strong>Swiss</strong>、Thailand→<strong>Thai</strong>。"), soft=True)
    + sec("國家英文常見問題", faq([
      ("台灣人的英文怎麼說？", "Taiwanese。可以當形容詞（Taiwanese food）也可以當名詞（I'm Taiwanese／She is a Taiwanese）。注意不說 Taiwan people——國名不能直接當形容詞用。"),
      ("英國為什麼是 the United Kingdom？", "因為 Kingdom 是普通名詞，前面要有 the。同理 the United States、the Philippines。單一專有名稱的國家（Japan、France）則不加。"),
      ("England、Britain、the UK 差在哪？", "England 只是英格蘭一地；Great Britain 包含英格蘭、蘇格蘭、威爾斯；the United Kingdom 再加上北愛爾蘭，是正式國名。填表格時通常要填 the United Kingdom。"),
      ("國籍的英文要大寫嗎？", "要。國名、國籍形容詞和語言名稱都是專有名詞，句中也大寫：I speak Chinese and English。這和月份、星期的規則一樣。"),
      ("America 和 the United States 一樣嗎？", "口語裡常常互換，但嚴格說 America 指整個美洲大陸。正式文件用 the United States 或 the USA 比較精確。"),
      ("要怎麼幫孩子記國家英文？", "從孩子有連結的國家開始——去過的、喜歡的球隊或卡通來自哪裡。接著用字尾規律（-ese、-ish、-an）成組記，而不是照字母硬背。"),
    ]), soft=True)
    + cta("國家、國籍這些字，真正用到的場合是自我介紹和聊天。我們的課堂每週都有跟美籍老師的真實對話練習，孩子講的是自己的事。")),
  faq_n=6),

"jobs-english": dict(
  target="職業英文", index=1.23,
  h1="職業英文對照表：83 種工作的英文說法與 a／an 的選擇",
  title="職業英文83種對照表：工作英文怎麼說、a與an怎麼選｜埃森美語",
  desc="職業英文完整對照表，收錄 83 種常見工作的英文與中文，依學校醫療、公共服務、商業辦公、科技工程、餐飲服務、運輸農漁與藝術媒體七組分類；並說明職業前面 a／an 的選擇與問職業的三種問法。",
  hero="「你爸爸做什麼工作？」是國小英文最早出現的對話之一，也是每年都會考的題型。難的不是單字，是三件事：職業前面要不要加 a、怎麼問、以及有些字已經不分男女了。",
  body=lambda: (
    sec("職業英文對照表（83 種）",
      prose("依領域分七組。找不到完全對應的工作時，母語者的做法是說 <em>I work in…</em> 加上行業，例如 I work in finance。")
      + grouped([(g[0], [[w, z] for w, z in g[1]]) for g in DATA["jobs"]], ["英文", "中文"]))
    + sec("職業前面一定要加 a 或 an",
      prose("這是中文母語者最常漏的一個字。中文說「我是老師」，英文<strong>必須</strong>說 I'm <em>a</em> teacher。",
        "<strong>a 或 an 看發音</strong>：a teacher、a doctor（子音開頭）；<em>an</em> engineer、<em>an</em> artist、<em>an</em> actor（母音開頭）。"
        "注意 <strong>an hour</strong> 的 h 不發音所以用 an，但 <strong>a university</strong> 開頭唸 /j/ 是子音，所以用 a。",
        "只有在講<strong>複數</strong>或<strong>職位唯一</strong>時不加：They are teachers（複數）／She was elected president（唯一職位）。"), soft=True)
    + sec("問職業的三種說法",
      prose("<strong>What do you do?</strong> — 最自然、最常用的問法。字面是「你做什麼」，實際就是問職業。<br>"
        "<strong>What do you do for a living?</strong> — 同義但更明確，適合正式場合。<br>"
        "<strong>What's your job?</strong> — 文法沒錯，但聽起來偏生硬，母語者較少用。",
        "回答時不必只講單字，加一句情境會自然得多：<em>I'm a teacher. I teach English at an elementary school.</em>",
        "問孩子的父母時用 <strong>What does your father do?</strong>——注意這裡是 does，考卷上常在這裡設陷阱。"))
    + sec("不再分男女的職業說法",
      prose("英文近二十年有個明顯轉變：<strong>帶性別的職稱正在被中性說法取代</strong>。考試和正式寫作建議用中性的：",
        "<strong>policeman → police officer</strong>、<strong>fireman → firefighter</strong>、"
        "<strong>stewardess → flight attendant</strong>、<strong>chairman → chairperson／chair</strong>、"
        "<strong>businessman → businessperson</strong>、<strong>mailman → mail carrier</strong>。",
        "少數仍常見成對使用：actor／actress、waiter／waitress——但現在也有越來越多人一律用 actor 和 server。"
        "教孩子時直接教中性版本，不會錯也不會過時。"), soft=True)
    + sec("職業英文常見問題", faq([
      ("「我是老師」英文怎麼說？", "I'm a teacher。a 不能省略——中文可以說「我是老師」，英文的單數可數名詞前面一定要有冠詞。這是最常見的漏字之一。"),
      ("a 還是 an 怎麼決定？", "看後面那個字的開頭發音，不是字母。母音音開頭用 an：an engineer、an artist、an hour（h 不發音）。子音音開頭用 a：a teacher、a university（唸 /j/）。"),
      ("What do you do 是什麼意思？", "就是問「你做什麼工作」，不是問「你在做什麼」。問當下在做什麼要用 What are you doing?——差在時態，考試常考這組對比。"),
      ("policeman 還可以用嗎？", "還看得懂，但正式寫作和考試建議用 police officer。英文近年普遍改用中性職稱：firefighter、flight attendant、chairperson 都是同樣的轉變。"),
      ("老闆和經理的英文怎麼分？", "boss 是口語的「上司」，指直屬管你的人；manager 是正式職稱，指管理某個部門或團隊。履歷和正式場合用 manager。"),
      ("孩子怎麼學職業英文最有效？", "從身邊的人開始——爸媽、老師、醫生、店員。接著玩猜謎：用英文描述一個職業做什麼，讓孩子猜。這同時練到職業單字和動詞，比單背名詞有用得多。"),
    ]), soft=True)
    + cta("職業、自我介紹這類單元，考試考的是句子不是單字。我們的課堂讓孩子真的用英文介紹自己和家人，講到不用想。")),
  faq_n=6),
})

HUB_CARDS = [
 ("/english-numbers-guide/", "英文數字 1-100", "0 到 100 完整拼法，附 13／30 的分辨方法", "101"),
 ("/months-english/", "月份英文 1-12", "月份、縮寫與天數，in／on 用法一次說清", "12"),
 ("/days-of-week-english/", "星期英文", "七天的縮寫、口語說法與 on Monday 的差別", "7"),
 ("/colors-english-vocabulary/", "顏色英文", "62 個顏色分五組，含深淺說法與拼法差異", "62"),
 ("/fruits-english-vocabulary/", "水果英文", "47 種水果，含芭樂、蓮霧、釋迦等台灣水果", "47"),
 ("/body-parts-english/", "身體部位英文", "43 個部位，含 teeth／feet 不規則複數", "43"),
 ("/countries-english/", "國家英文", "80 國名稱與國籍形容詞，the 什麼時候加", "80"),
 ("/jobs-english/", "職業英文", "83 種工作，a／an 的選擇與問職業的說法", "83"),
 ("/animals-english-vocabulary/", "動物英文", "常見動物中英對照，依類別分組", "41"),
 ("/moe-1200-words-guide/", "教育部 1200 單字", "108 課綱附錄五完整字表，可線上核對", "1211"),
 ("/moe-2000-words-guide/", "國中 2000 單字", "國中必備字表，程度約 CEFR B1", "2000"),
 ("/kk-phonetic-chart/", "KK 音標表", "41 個音標符號，每個字可點聽發音", "41"),
]

def hub_page():
    cards = "".join(
      f'<a class="hubcard" href="{h}"><span class="hc-n">{n}</span>'
      f'<strong>{t}</strong><span class="hc-d">{d}</span></a>' for h, t, d, n in HUB_CARDS)
    return (
      sec("依主題挑一份字表",
        prose("每一頁都是完整對照表，不是節錄；主題字表的每個英文字旁邊都有喇叭可以點開聽發音，"
              "表格也都有可以直接存下來或列印的圖片版。")
        + f'<div class="hubgrid reveal">{cards}</div>')
      + sec("背單字為什麼常常沒用",
        prose("台灣孩子的單字量通常不差，問題出在<strong>只記得中文意思，不知道怎麼用</strong>。"
              "「背過」和「會用」中間差了三件事：發音、詞性、搭配。",
              "<strong>發音</strong>——念不出來的字，聽力考試聽到也認不出來。這也是這裡每個字都配音檔的原因。<br>"
              "<strong>詞性</strong>——知道 beautiful 是「美麗的」不夠，要知道它是形容詞，所以不能說 She beautiful。<br>"
              "<strong>搭配</strong>——make a decision 不是 do a decision。母語者記的是整組詞，不是單字。",
              "所以這些字表的用法不是「從頭背到尾」，而是<strong>挑一組主題，用它造五個句子</strong>。"
              "五個句子花的時間比背五十個字少，效果卻大得多。"), soft=True)
      + sec("一份字表怎麼用才有效",
        prose("<strong>一、先聽再看。</strong>點喇叭聽過一遍再看拼法，順序反過來會讓孩子用中文的發音習慣去猜英文。",
              "<strong>二、分組不分量。</strong>一次處理一個主題（顏色、水果），不要一次十個主題。"
              "同一類的字在腦中會互相牽連，記得比較牢。",
              "<strong>三、印出來貼起來。</strong>每一頁都有圖片版的對照表，貼在書桌前或冰箱上，"
              "每天經過看一眼的效果，勝過一週坐下來背一次。",
              "<strong>四、用它造句。</strong>這是唯一真正把字從「認得」推到「會用」的一步。"))
      + sec("背單字常見問題", faq([
        ("孩子一天該背幾個單字？", "比起數量，更重要的是重複的次數。國小中年級一天 5 到 8 個、並且隔天再看一次，"
          "遠比一天 30 個、之後再也不看有效。單字是靠反覆遇到記住的，不是靠一次背完。"),
        ("要先背教育部的字表還是主題字表？", "兩個一起。教育部 1200／2000 字表是考試範圍，主題字表是生活會用到的。"
          "先從主題字表建立成就感和語感，再用教育部字表確認範圍有沒有漏。"),
        ("單字書和線上字表哪個好？", "差別不在載體，在有沒有發音和能不能反覆。線上字表的優勢是可以點聽、可以搜尋；"
          "紙本的優勢是可以貼起來天天看。最好的做法是線上學、印出來複習。"),
        ("背了就忘怎麼辦？", "這是正常的。記憶需要在快忘記的時候被提取一次才會變長期記憶。"
          "實務做法是「隔天、隔三天、隔一週」各看一次，三次之後大多數字就穩定了。"),
        ("要不要用 App 背單字？", "可以，但 App 最擅長的是「提醒你複習」，不是「教你用」。"
          "用 App 維持每天接觸，用造句和對話把字變成能用的——兩件事要分開做。"),
        ("孩子只記中文意思算會了嗎？", "不算。真正的檢查方式是反過來：給中文，孩子能不能說出英文並唸對；"
          "以及能不能用這個字講一個句子。只認得中文，考試遇到閱讀和寫作還是用不出來。"),
      ]), soft=True)
      + cta("字表給的是範圍，真正的差別在有沒有人聽孩子把這些字用出來。我們的小班課每堂都要開口，美籍老師當場糾正。"))

PAGES["english-vocabulary-by-topic"] = dict(
  target="英文單字", index=8.09,
  h1="英文單字主題字表總整理：12 份完整對照表，每個字都能點聽發音",
  title="英文單字主題總整理：12份完整字表，可聽發音與列印｜埃森美語",
  desc="英文單字主題字表總整理：數字、月份、星期、顏色、水果、身體部位、國家、職業、動物，加上教育部 1200／2000 字表與 KK 音標表，共 12 份完整對照表。每個英文字可點聽發音，每份都有可列印的圖片版——美籍持證教師整理。",
  hero="市面上的單字表大多是節錄，而且沒有發音。這裡的 12 份都是完整表，每個英文字旁邊都能點開聽，也都能直接存成圖片印出來。下面先挑主題，後面講怎麼用才不會背了就忘。",
  body=hub_page,
  faq_n=6)

PAGES["english-abbreviations-guide"] = dict(
  target="英文縮寫", index=11.99,
  h1="英文縮寫大全：74 個常用縮寫的意思、全名與正確用法",
  title="英文縮寫大全：74個常用縮寫意思查詢、全名與用法｜埃森美語",
  desc="英文縮寫完整對照表，收錄 74 個常用縮寫的中文意思與英文全名，分日常書寫、網路訊息、學校考試、商業職場與單位五組；並說明 e.g. 與 i.e. 的差別、縮寫要不要加句點，以及月份與星期縮寫的完整規則。",
  hero="英文縮寫最惱人的地方是：看得到卻查不到。e.g. 和 i.e. 差在哪、etc. 前面要不要加 and、LOL 到底能不能對長輩用——下面這份表把 74 個常見縮寫的意思和<strong>英文全名</strong>都列出來，知道全名就不會再用錯。",
  body=lambda: (
    sec("英文縮寫對照表（74 個）",
      prose("第三欄是<strong>英文全名</strong>——這一欄才是關鍵。知道 e.g. 來自 exempli gratia（for example）、"
            "i.e. 來自 id est（that is），就不會再混用。")
      + grouped([(g[0], [[a, b, c] for a, b, c in g[1]]) for g in DATA["abbrev"]],
                ["縮寫", "中文意思", "英文全名／說明"]))
    + sec("e.g. 和 i.e. 到底差在哪",
      prose("這是英文縮寫裡最常用錯的一組，連母語者都會錯。",
        "<strong>e.g. = for example（舉例）</strong>，後面接的是<em>其中幾個例子</em>，不是全部。<br>"
        "<em>I like citrus fruits, e.g. oranges and lemons.</em>（還有其他柑橘類，只是舉兩個）",
        "<strong>i.e. = that is（也就是說）</strong>，後面接的是<em>把前面說完整</em>，等於重講一次。<br>"
        "<em>I like citrus fruits, i.e. oranges and lemons.</em>（我喜歡的柑橘類就只有這兩種）",
        "記法：<strong>e</strong>.g. 的 e 想成 <strong>e</strong>xample，<strong>i</strong>.e. 的 i 想成 <strong>i</strong>n other words。"
        "兩者在正式英文中後面都要加逗號，而且都保留句點。"), soft=True)
    + sec("縮寫要不要加句點？",
      prose("規則不複雜，但美式與英式不同：",
        "<strong>截去字尾的縮寫要加句點</strong>：Prof.（Professor）、etc.（et cetera）、approx.（approximately）、Jan.（January）。"
        "因為後面還有字母被省略。<br>"
        "<strong>頭尾都保留的縮寫，英式不加、美式加</strong>：Mr／Mr.、Dr／Dr.、St／St.。台灣教科書多從英式，多益等美系考試用美式。<br>"
        "<strong>首字母縮寫（每個字母唸出來或當成字唸）不加句點</strong>：NASA、UNESCO、ASAP、FYI、CEO。",
        "一個常見錯誤：<strong>etc. 前面不加 and</strong>。et cetera 的 et 本身就是 and，寫 and etc. 等於講了兩次。"))
    + sec("月份、星期與單位的縮寫",
      prose("這三組有自己的固定規則，也是查詢量最高的幾個：",
        "<strong>月份</strong>取前三個字母加句點，只有 May 不縮寫；September 兩種都通行（Sep./Sept.）。完整表在 "
        "<a href=\"/months-english/\">月份英文</a>。<br>"
        "<strong>星期</strong>同樣取前三字母：Mon.、Tue.（或 Tues.）、Wed.、Thu.（或 Thurs.）、Fri.、Sat.、Sun.。"
        "完整表在 <a href=\"/days-of-week-english/\">星期英文</a>。<br>"
        "<strong>單位</strong>一律不加句點也不加複數 s：5 kg（不是 5 kgs.）、10 cm、3 L。這是國際單位制的規定。",
        "名字縮寫（initials）則是取每個名字的第一個字母大寫加句點：John Ronald Reuel Tolkien → <strong>J. R. R. Tolkien</strong>。"), soft=True)
    + sec("NASA 唸成單字、FBI 唸字母——怎麼判斷",
      prose("首字母縮寫有兩種唸法，分界不是規則而是<strong>能不能唸得出來</strong>：",
        "<strong>拼得出音節的唸成一個字</strong>（acronym）：NASA /ˈnæsə/、NATO /ˈneɪtoʊ/、"
        "UNESCO、ASAP（也有人逐字母唸）、SCUBA、laser——這些字母組合剛好構成可發音的音節。<br>"
        "<strong>拼不出音節的逐字母唸</strong>（initialism）：FBI /ˌɛf biː ˈaɪ/、CEO、DIY、ATM、USB、"
        "FAQ——連續子音沒辦法成音節，只能一個一個唸。",
        "判斷法很簡單：<strong>試著把它當成一個字唸唸看</strong>。唸得順就是 acronym，卡住就逐字母唸。"
        "少數兩種都可以：ASAP、FAQ 在不同地區習慣不同，都不算錯。"), soft=True)
    + sec("網路縮寫什麼場合能用",
      prose("這是家長最常問的一題。簡單的分界線：<strong>看對象，不看場合的正式程度</strong>。",
        "<strong>朋友之間的訊息</strong>：LOL、BTW、TBH、JK 都沒問題。<br>"
        "<strong>寫給老師、主管或客戶</strong>：FYI、ASAP、ETA 可以（這些在職場是標準用語）；"
        "LOL、OMG、JK 不要。<br>"
        "<strong>作文與正式書信</strong>：網路縮寫一律不要，連 e.g. 和 etc. 在很正式的文章裡也建議寫全。",
        "考試更嚴格：<strong>英檢與學測作文用網路縮寫會被視為錯誤</strong>。教孩子時把這條線講清楚比禁止有效——"
        "他知道什麼時候能用，才不會在該正式的時候用錯。"))
    + sec("英文縮寫常見問題", faq([
      ("e.g. 和 i.e. 差在哪？", "e.g. 是 for example，後面接其中幾個例子；i.e. 是 that is，後面把前面那句說完整。"
        "記法：e 想成 example，i 想成 in other words。兩個後面在正式英文裡都加逗號。"),
      ("etc. 前面要加 and 嗎？", "不要。etc. 是 et cetera，et 本身就是 and，寫 and etc. 等於說了兩次 and。"
        "另外 etc. 只用在列舉事物，列舉「人」時用 et al.。"),
      ("縮寫要不要加句點？", "截掉字尾的要加（Prof.、approx.、Jan.）；首字母縮寫不加（ASAP、CEO、NASA）；"
        "Mr、Dr 這類頭尾都在的，英式不加、美式加。台灣教科書多從英式。"),
      ("ASAP 可以對主管用嗎？", "可以，ASAP、FYI、ETA 在職場是標準用語，不算不禮貌。要避開的是 LOL、OMG、JK 這類"
        "純社交用語。真正的分界是對象，不是縮寫本身。"),
      ("名字縮寫怎麼寫？", "取每個名字的第一個字母大寫加句點，中間空一格：J. R. R. Tolkien。"
        "台灣的護照英文姓名若要縮寫，一般保留姓氏全名、名字縮寫，例如 Wang, C. H."),
      ("作文可以用縮寫嗎？", "英檢與學測作文建議不要。e.g.、etc. 在一般文章可以，但在正式作文裡寫成 for example、and so on 更安全；"
        "網路縮寫一律會被視為錯誤。"),
    ]), soft=True)
    + cta("縮寫這種東西，查得到意思不代表用得對——用錯場合比不會用更尷尬。我們的課堂會教孩子分辨什麼時候能用、什麼時候不行。")),
  faq_n=6)

PAGES["thank-you-english"] = dict(
  target="謝謝英文", index=2.16,
  h1="謝謝的英文怎麼說？30 種說法、回應方式與 Thank you for 的用法",
  title="謝謝英文30種說法與回應方式｜埃森美語",
  desc="謝謝英文完整對照表：日常口語、正式書面、回應別人道謝的說法，共 30 種，每一句都標明適用場合；"
       "並說明 Thank you for 後面要接 -ing 還是名詞、You're welcome 之外還能怎麼回，以及 Thanks in advance 什麼時候別用。",
  hero="Thank you 大家都會，問題是<strong>只會這一句</strong>。英文裡道謝的輕重差別很細：對同學說 Thank you very much 會顯得客套，寫 email 只寫 Thanks 又太隨便。下面 30 種說法都標了適用場合，挑對比說多更重要。",
  body=lambda: (
    sec("謝謝英文對照表（30 種）",
      prose("第三欄是<strong>什麼時候用</strong>——這才是真正決定該說哪一句的依據。")
      + grouped([(g[0], [[a, b, c] for a, b, c in g[1]]) for g in DATA["thanks"]],
                ["英文", "中文", "什麼時候用"]))
    + sec("Thank you for 後面要接什麼",
      prose("這是最常錯的文法點。<strong>for 是介系詞，後面只能接名詞或動名詞（-ing）</strong>，不能接原形動詞：",
        "✅ Thank you for <strong>your help</strong>.（名詞）<br>"
        "✅ Thank you for <strong>helping</strong> me.（動名詞）<br>"
        "❌ Thank you for <s>help</s> me.（原形動詞——錯）",
        "另一個常見錯誤是把 thank 當名詞用：<strong>Thanks 一定有 s</strong>（它是 thanks 的縮略，本來就是複數），"
        "沒有 <s>Thank</s> 這種單獨用法。"), soft=True)
    + sec("別人謝你，除了 You're welcome 還能說什麼",
      prose("台灣學生幾乎只會 You're welcome，但母語者日常更常用短一點的：<strong>No problem</strong>、"
        "<strong>No worries</strong>、<strong>Sure</strong>、<strong>Anytime</strong>。",
        "服務場合（店員、櫃檯、服務生）最常用 <strong>My pleasure</strong>——它比 You're welcome 更禮貌，"
        "在飯店和餐廳幾乎是標準答案。",
        "⚠️ 一個小陷阱：<strong>Thanks in advance</strong>（先謝謝你）在英文裡有時會被讀成「我已經當你會答應了」，"
        "帶點壓力。寫信給不熟的人時，用 <em>Thank you for considering this</em> 或 <em>I'd really appreciate your help</em> 更安全。"))
    + sec("謝謝英文常見問題", faq([
      ("Thanks 和 Thank you 差在哪？", "Thanks 較輕鬆、口語，用於朋友同學；Thank you 通用，任何場合都不會出錯；"
        "Thank you very much 最正式。寫 email 給老師或主管，用 Thank you 起跳。"),
      ("Thank you for 後面可以接原形動詞嗎？", "不行。for 是介系詞，後面接名詞或動名詞：Thank you for your help／"
        "Thank you for helping me。接原形動詞是台灣學生最常見的錯誤之一。"),
      ("回「不客氣」只能說 You're welcome 嗎？", "不是，母語者日常更常用 No problem、No worries、Sure、Anytime。"
        "服務場合用 My pleasure 最得體。You're welcome 不算錯，只是聽起來比較正式。"),
      ("Cheers 是謝謝的意思嗎？", "在英式英語裡是。Cheers 同時能表示「謝了」「再見」和舉杯敬酒，看場合判斷。"
        "美式英語裡主要只有敬酒的意思，拿來道謝會讓人愣一下。"),
      ("寫 email 道謝該用哪一句？", "開頭用 Thank you for your email／Thanks for getting back to me；"
        "結尾用 Thank you for your help／Thank you for your time。想簡短一點，Many thanks 也很常見。"),
      ("孩子怎麼練這些說法？", "不要一次背三十句。先挑三句——一句對同學（Thanks）、一句對老師（Thank you）、"
        "一句回應（No problem）——用到變成反射動作，再加下一組。"),
    ]), soft=True)
    + cta("道謝、道歉、請求這種每天都會用到的句子，最怕只認得字、開口卡住。我們的課堂每堂都有真實情境的對話練習。")),
  faq_n=6)

PAGES["cheer-up-english"] = dict(
  target="加油英文", index=1.16,
  h1="「加油」的英文怎麼說？21 種說法，看場合挑對那一句",
  title="加油英文怎麼說？21種說法：考試前、比賽中、撐下去的差別｜埃森美語",
  desc="「加油」的英文沒有單一對應說法，要看場合：考試前用 Good luck、比賽場邊喊 Come on、"
       "過程中撐住用 Hang in there、對方已經很努力時用 Take your time。21 種說法分四組對照，"
       "並說明 Break a leg 為什麼不能用在考試前——美籍持證教師整理。",
  hero="這是中翻英最難的一個詞，因為<strong>英文裡沒有一個字等於「加油」</strong>。中文的加油可以是祝好運、可以是催快一點、也可以是叫人撐住——英文會依情境用完全不同的句子。挑錯了會很奇怪，下面按場合分好。",
  body=lambda: (
    sec("加油英文對照表（21 種）",
      prose("先看<strong>場合</strong>再挑句子。同一句「加油」，考試前和比賽中用的英文完全不同。")
      + grouped([(g[0], [[a, b, c] for a, b, c in g[1]]) for g in DATA["cheer"]],
                ["英文", "中文", "備註"]))
    + sec("為什麼沒有一個字等於「加油」",
      prose("中文的「加油」字面是往引擎裡加燃料，用來泛指一切鼓勵。英文把這件事拆成<strong>四種不同的意思</strong>，"
        "各有各的說法：",
        "<strong>事情還沒開始</strong> → 祝好運：Good luck!<br>"
        "<strong>正在進行、在場邊</strong> → 催促與助威：Come on! / Go!<br>"
        "<strong>進行中、很辛苦</strong> → 叫對方撐住：Hang in there! / Keep going!<br>"
        "<strong>對方已經很努力</strong> → 肯定而非催促：You're doing great. / Take your time.",
        "最後一種台灣學生最少用，卻最常是中文「加油」真正的意思。對一個已經很累的人喊 Come on，"
        "在英文裡聽起來像在嫌他慢。"), soft=True)
    + sec("Break a leg 千萬別用錯",
      prose("<strong>Break a leg</strong> 是「祝演出順利」，只用在<strong>上台表演之前</strong>——戲劇、音樂會、舞蹈。"
        "它來自劇場迷信：直接說 good luck 會帶來厄運，所以反著講。",
        "⚠️ <strong>不要用在考試、比賽或面試前</strong>。對要去考試的人說 Break a leg，"
        "母語者會覺得你用錯了場合，甚至像在開玩笑。考試前就用最單純的 <strong>Good luck!</strong>",
        "另一個容易誤用的是 <strong>Fight!</strong>——那是韓劇裡的用法（화이팅），不是英文。"
        "英語母語者聽到 Fight 只會想到打架。"))
    + sec("加油英文常見問題", faq([
      ("「加油」的英文到底是什麼？", "沒有單一答案，看場合。考試前 Good luck；比賽場邊 Come on／Go；"
        "過程中撐住 Hang in there／Keep going；對方已經很努力時 You're doing great。挑錯場合會很奇怪。"),
      ("可以說 Add oil 嗎？", "Add oil 已被牛津英語詞典收錄為源自香港的用法，英語圈也有人看得懂，"
        "但在台灣以外的日常對話裡仍然少見。想被聽懂，還是用 You've got this 或 Good luck 最安全。"),
      ("Fighting 是英文嗎？", "不是英文的用法。화이팅／Fighting 來自韓語，英語母語者聽到 Fight 只會想到打架。"
        "要表達同樣的意思，用 You can do it 或 Let's go。"),
      ("Break a leg 可以用在考試前嗎？", "不行。它專指上台表演之前——戲劇、音樂會、舞蹈。用在考試或面試前會顯得用錯場合。"
        "考試前說 Good luck 就好。"),
      ("Good luck 和 You've got this 差在哪？", "Good luck 把結果交給運氣；You've got this 是說「你有這個能力」，"
        "肯定的是對方本身。鼓勵準備充分的人，後者更有力量。"),
      ("怎麼教孩子挑對句子？", "給他三個場景就夠：考試前、比賽中、很累的時候。每個場景配一句，"
        "先會用再擴充。一次背二十一句，結果是每一句都不敢用。"),
    ]), soft=True)
    + cta("鼓勵、安慰、道賀這種話，說不出口不是因為單字不夠，是因為沒在真實對話裡練過。我們的小班課每堂都要開口。")),
  faq_n=6)

def practice_cards(rows):
    cards = "".join(
      f'<a class="hubcard" href="{h}"><span class="hc-n">{n}</span>'
      f'<strong>{t}</strong><span class="hc-d">{d}</span></a>' for h, t, d, n in rows)
    return f'<div class="hubgrid reveal">{cards}</div>'

SKILL_FAQ_TAIL = ("我們的小班課每堂都要開口，美籍老師當場糾正——"
                  "這是任何線上教材都補不上的一環。")

PAGES["english-listening-practice"] = dict(
  target="英文聽力", index=1.42,
  h1="英文聽力怎麼練？從聽不懂到跟得上的四個階段（附 27 頁免費練習）",
  title="英文聽力練習：四個階段方法＋27頁免費線上題庫與音檔｜埃森美語",
  desc="英文聽力練習完整方法：為什麼單字都會卻聽不懂、跟讀（shadowing）怎麼做才有效、"
       "連音與弱化如何拆解，以及依程度分級的 27 頁免費線上聽力練習，每一頁都附音檔與逐字稿。",
  hero="「每個字我都認得，連起來就聽不懂」——這是台灣學生最普遍的英文問題，而且它<strong>不是單字量的問題</strong>。"
       "聽不懂多半來自三件事：長短母音沒分開、字尾被吞掉、以及母語者會把字黏在一起。下面先講方法，後面有依程度分好的免費練習。",
  body=lambda: (
    sec("為什麼字都會，還是聽不懂",
      prose("閱讀和聽力用的是兩套不同的能力。閱讀時你可以停下來、回頭看；聽力是<strong>單向而且不等人</strong>的。"
            "三個真正的卡點：",
            "<strong>一、音沒有分開。</strong>ship 和 sheep 在腦中是同一個音，聽到時就得靠上下文猜——猜錯就整句崩掉。"
            "這一關屬於發音，不是聽力：<a href=\"/ship-or-sheep-english-vowels/\">母音辨識練習</a>。",
            "<strong>二、字尾聽不到。</strong>-s 和 -ed 在口語中很輕，但它們承載單複數與時態。聽不到就判斷不出「他做過」還是「他要做」："
            "<a href=\"/plural-s-past-ed-pronunciation/\">字尾 -s 與 -ed 練習</a>。",
            "<strong>三、字被黏在一起。</strong>母語者說 pick it up 聽起來像 pi-ki-tup。這不是說得快，是<strong>連音</strong>——"
            "規則整理在 <a href=\"/english-pronunciation/\">英文發音完整指南</a>。"))
    + sec("聽起來像什麼、其實是什麼：12 個最常聽錯的地方",
      prose("這些不是說話快，是母語者<strong>固定的省略與連音</strong>。認得它們之後，很多「聽不懂」會直接消失。")
      + tbl([["wanna","want to","想要","I wanna go."],["gonna","going to","將要","It's gonna rain."],
             ["gotta","got to / have got to","必須","I gotta go."],["lemme","let me","讓我","Lemme see."],
             ["dunno","don't know","不知道","I dunno."],["kinda","kind of","有點","It's kinda cold."],
             ["cuz / 'cause","because","因為","'Cause I'm tired."],["watcha","what are you / what do you","你在…","Watcha doing?"],
             ["thir-TEEN","thirteen（重音在後）","13","She's thirteen."],["THIR-ty","thirty（重音在前）","30","She's thirty."],
             ["can（弱讀 /kən/）","can","可以","I can /kən/ swim."],["CAN'T（重讀）","can't","不可以","I CAN'T swim."]],
            ["聽起來像", "其實是", "意思", "例句"]))
    + sec("跟讀：唯一真正有效的練法",
      prose("<strong>跟讀（shadowing）</strong>是聽力訓練裡少數有明確證據的方法，做法簡單但細節決定成敗：",
            "<strong>1. 挑對材料。</strong>選你能聽懂七、八成的音檔。全聽不懂等於在聽噪音，全聽得懂則沒有訓練效果。",
            "<strong>2. 先不看逐字稿聽一遍。</strong>記下聽不出來的地方。",
            "<strong>3. 看著逐字稿再聽一遍。</strong>這一步會出現最多「啊原來它是這樣唸」的瞬間——那正是連音在哪裡發生。",
            "<strong>4. 原速跟著唸。</strong>重點是模仿<em>節奏和語調</em>，不是把每個字咬清楚。唸不完整沒關係，跟上拍子最重要。",
            "<strong>5. 最後再裸聽一次。</strong>檢查剛才聽不出來的地方現在聽不聽得到。",
            "每天一段五分鐘，勝過週末一次半小時。聽力是靠接觸頻率長出來的。"), soft=True)
    + sec("依程度分級的免費聽力練習（27 頁）",
      prose("每一頁都有音檔、題目與<strong>完整逐字稿</strong>，做完可以立刻對答案。全部免費，不用註冊。")
      + practice_cards([
        ("/starters-listening-practice-part1/","Starters 聽力","劍橋第一級・國小低年級起步","4 頁"),
        ("/movers-listening-practice-part1/","Movers 聽力","劍橋第二級・國小中年級","5 頁"),
        ("/flyers-listening-practice-part1/","Flyers 聽力","劍橋第三級・國小高年級","5 頁"),
        ("/ket-listening-practice-part1/","KET 聽力","CEFR A2・國中程度","5 頁"),
        ("/pet-listening-practice-part1/","PET 聽力","CEFR B1・國中進階","4 頁"),
        ("/fce-listening-practice-part1/","FCE 聽力","CEFR B2・高中程度","4 頁"),
      ]))
    + sec("英文聽力常見問題", faq([
      ("聽力要從幾級開始練？", "從你能聽懂七到八成的那一級開始，不是從你的年級開始。做一頁 Starters 覺得太簡單就往上跳一級，"
        "連續兩頁低於六成就退一級。選對難度比練多久重要。"),
      ("一天要練多久？", "五到十分鐘，但要每天。聽力是接觸頻率的函數，不是總時數的函數——每天五分鐘連續三十天，"
        "效果遠勝於一個週末練三小時。"),
      ("可以用美劇或英文歌練嗎？", "可以當作接觸，但不能取代練習。影集的語速、俚語和背景音對還在建立基礎的孩子太難，"
        "而且看字幕時眼睛會接管耳朵的工作。先用有逐字稿的教材練，再用影集維持興趣。"),
      ("要開字幕嗎？", "分兩階段：第一次聽不要開，記下聽不懂的地方；第二次開著聽，找出「原來是這樣唸」的位置。"
        "全程開字幕等於在練閱讀。"),
      ("聽力進步要多久才看得出來？", "如果卡點在音的辨識，穩定練六到八週通常看得出差別；如果是單字量不足造成的，"
        "會更久。先確認是哪一種——聽不懂的是「沒聽清楚」還是「聽清楚了但不知道意思」。"),
      ("孩子說聽力很無聊怎麼辦？", "多半是難度選錯了。太難會挫折、太簡單會無趣。換一級試試，"
        "並把時間縮到五分鐘——短到他覺得「這很快就結束」，才撐得下去。"),
    ]), soft=True)
    + cta("聽力最難自己檢查的一點是：你不知道自己漏聽了什麼。" + SKILL_FAQ_TAIL)),
  faq_n=6)

PAGES["english-reading-practice"] = dict(
  target="英文閱讀", index=1.60,
  h1="英文閱讀怎麼練？從逐字翻譯到讀得順的方法（附 30 頁免費練習）",
  title="英文閱讀練習：擺脫逐字翻譯的方法＋30頁免費線上題庫｜埃森美語",
  desc="英文閱讀練習方法：為什麼逐字翻譯會讓閱讀卡住、猜字的三個線索、略讀與尋讀怎麼分，"
       "以及依程度分級的 30 頁免費線上閱讀練習，每題附中文解析。",
  hero="讀英文時在心裡默默翻成中文，是台灣學生最普遍的閱讀習慣——也是速度上不去的主因。"
       "<strong>閱讀的目標不是翻譯，是理解。</strong>下面講怎麼把這個習慣換掉，後面有依程度分好的免費練習。",
  body=lambda: (
    sec("逐字翻譯為什麼會卡住",
      prose("逐字翻譯有三個代價：<strong>慢</strong>（每個字都要轉一次）、<strong>容易錯</strong>"
            "（英文的語序和中文不同，逐字換過來常常意思跑掉）、以及<strong>撐不到句尾</strong>"
            "（翻到後面時前面已經忘了）。",
            "換掉它的方法不是「叫自己不要翻譯」，而是<strong>讓速度快到來不及翻譯</strong>：挑簡單一級的材料，"
            "規定自己不准回頭看，讀完再檢查理解了多少。一開始會覺得抓不牢，兩三週後就會發現不翻譯反而懂得更多。"))
    + sec("遇到生字時的三個線索",
      prose("讀文章時查每一個生字，等於把閱讀變成查字典。先用線索猜，猜不到再查：",
            "<strong>一、上下文。</strong>前後句通常會解釋或舉例。看到 <em>The soil was arid — nothing had grown "
            "there for years.</em> 就知道 arid 和「乾」有關。",
            "<strong>二、字首字根。</strong><em>un-</em>（不）、<em>re-</em>（再）、<em>-less</em>（沒有）、"
            "<em>-ful</em>（充滿）。認得幾十個字根，生字量會直接減半。",
            "<strong>三、詞性。</strong>就算不知道意思，從位置也能判斷它是名詞、動詞還是形容詞——"
            "光是這個就常常足以答對題目。"), soft=True)
    + sec("認得這 14 個字首字尾，生字量直接減半",
      prose("英文單字有一大半是「字首＋字根＋字尾」拼出來的。不用背字根，先認得最常見的字首字尾就夠用。")
      + tbl([["un-","不、相反","unhappy, unable, unlock"],["re-","再、回","redo, return, rewrite"],
             ["pre-","之前","preview, prepay, preschool"],["dis-","不、相反","dislike, disagree, disappear"],
             ["mis-","錯誤地","mistake, misread, misunderstand"],["im- / in-","不","impossible, incorrect, informal"],
             ["over-","過度","overeat, oversleep, overweight"],["-ful","充滿…的","helpful, careful, beautiful"],
             ["-less","沒有…的","careless, useless, homeless"],["-er / -or","做…的人","teacher, worker, actor"],
             ["-tion / -sion","（動詞變名詞）","action, decision, education"],["-ly","（形容詞變副詞）","quickly, slowly, carefully"],
             ["-able","能夠…的","readable, comfortable, washable"],["-ment","（動詞變名詞）","movement, agreement, payment"]],
            ["字首／字尾", "意思", "例字"]))
    + sec("略讀與尋讀：考試時真正在用的兩種讀法",
      prose("<strong>略讀（skimming）</strong>是快速看過抓大意——先看標題、每段第一句和最後一句。"
            "用在「這篇在講什麼」這類題目。",
            "<strong>尋讀（scanning）</strong>是帶著問題去找特定資訊，眼睛掃過去找關鍵字，不讀其他部分。"
            "用在「文中提到哪一年」這類題目。",
            "考試的正確順序是：<strong>先讀題目，再回頭尋讀</strong>。從頭逐句精讀整篇再看題目，時間一定不夠。"))
    + sec("依程度分級的免費閱讀練習（30 頁）",
      prose("劍橋的閱讀與寫作是同一份考卷，所以前四級的練習是合併的；PET 有獨立的閱讀練習。每題附中文解析。")
      + practice_cards([
        ("/starters-rw-practice-part1/","Starters 閱讀與寫作","劍橋第一級・看圖選字起步","5 頁"),
        ("/movers-rw-practice-part1/","Movers 閱讀與寫作","劍橋第二級","6 頁"),
        ("/flyers-rw-practice-part1/","Flyers 閱讀與寫作","劍橋第三級","6 頁"),
        ("/ket-rw-practice-part1/","KET 閱讀與寫作","CEFR A2・含選字填空","7 頁"),
        ("/pet-reading-practice-part1/","PET 閱讀","CEFR B1・獨立閱讀卷","6 頁"),
        ("/a2-vocabulary-practice/","A2 單字情境練習","讀不懂常常是字不夠","64 題"),
      ]))
    + sec("英文閱讀常見問題", faq([
      ("讀英文一定要查每個生字嗎？", "不要。一頁生字超過一成就代表材料太難，該換簡單一級的。"
        "生字在一成以內時，先用上下文和字根猜，讀完再挑三到五個真正重要的查——查得少反而記得牢。"),
      ("怎麼擺脫逐字翻譯的習慣？", "挑簡單一級的材料，規定自己不准回頭看、不准查字典，讀完再檢查理解多少。"
        "把速度逼快到來不及翻譯，習慣兩三週就會鬆動。"),
      ("孩子讀完都說看懂，一問就答不出來？", "那是「認得字」不是「理解」。讀完請他用中文講一遍在說什麼，"
        "講不出來就代表只是眼睛掃過去。用有題目的練習比純閱讀更能逼出理解。"),
      ("英文閱讀一天要讀多久？", "每天一篇短的，勝過一週一篇長的。國小階段一次十分鐘就夠，"
        "重點是形成習慣而不是累積字數。"),
      ("繪本和分級讀本哪個好？", "看階段。剛起步用繪本，圖片本身就是理解的支架；能讀完整句之後換分級讀本，"
        "它的難度梯度比較可控。可以參考我們的英文繪本選書指南。"),
      ("考試時閱讀來不及寫完怎麼辦？", "多半是讀法錯了。先讀題目再回頭尋讀，不要從頭精讀整篇。"
        "略讀抓大意、尋讀找細節，這兩招練熟通常就夠用了。"),
    ]), soft=True)
    + cta("閱讀真正的難關是「以為看懂了」。" + SKILL_FAQ_TAIL)),
  faq_n=6)

PAGES["english-speaking-practice"] = dict(
  target="英文口說", index=1.23,
  h1="英文口說怎麼練？不用找人對話也能開口的方法（附 6 場完整對話逐字稿）",
  title="英文口說練習：一個人也能練的方法＋6場完整對話逐字稿｜埃森美語",
  desc="英文口說練習方法：為什麼台灣學生「會寫不會說」、一個人怎麼練口說（自問自答、錄音回聽、"
       "跟讀）、以及劍橋各級口說考什麼——附六場完整對話逐字稿與中文對照，全部免費。",
  hero="會寫不會說，是台灣英語教育最典型的產出。原因不神秘：<strong>口說是唯一一個沒被考試逼著練的技能</strong>。"
       "好消息是它也最容易自己練——下面三個方法都不需要對象，最後有六場完整對話逐字稿可以直接跟著唸。",
  body=lambda: (
    sec("為什麼會寫卻說不出口",
      prose("寫作可以停下來想、可以改；口說必須<strong>即時產出</strong>。這中間差的是「提取速度」——"
            "字就在腦中，但拿不出來。",
            "第二個原因是<strong>怕錯</strong>。孩子在課堂上被糾正過幾次之後，會選擇不開口——沉默的成本看起來比說錯低。"
            "這也是為什麼在家練有價值：沒有人在看。",
            "第三個是<strong>沒有句子模板</strong>。母語者講話靠的是成組的固定說法，不是現場組裝文法。"
            "背十個能立刻用的句型，比背一百個單字更能讓孩子開口。"))
    + sec("一個人也能做的三種練習",
      prose("<strong>一、自問自答。</strong>拿一個題目——今天做了什麼、最喜歡哪個季節、介紹你的家人——"
            "用英文回答三十秒。講不下去就停，把卡住的地方記下來，查完再講一次。這正是劍橋口說 Part 1 的題型。",
            "<strong>二、錄音回聽。</strong>最有效也最少人做。錄三十秒自己聽一遍，你會立刻聽出自己的問題——"
            "速度太快、字尾吞掉、同一個連接詞用了五次。孩子聽自己的錄音，比大人糾正十次更有用。",
            "<strong>三、跟讀逐字稿。</strong>拿一段有逐字稿的對話，原速跟著唸，模仿節奏和語調。"
            "這同時練到發音、連音與流暢度——做法和聽力的跟讀相同，只是重點放在產出。"), soft=True)
    + sec("十個馬上能開口的句型",
      prose("母語者講話靠的是成組的固定說法。這十個句型能撐起大部分日常對話與劍橋口說 Part 1 的題目，先練到不用想。")
      + tbl([["My name is … and I'm … years old.","自我介紹","My name is Amy and I'm ten years old."],
             ["I like … because …","說喜好＋理由","I like dogs because they're friendly."],
             ["I don't really like …","說不喜歡（委婉）","I don't really like math."],
             ["My favorite … is …","最喜歡的","My favorite subject is art."],
             ["I usually … on …","說習慣","I usually play basketball on Saturdays."],
             ["Yesterday I … / Last weekend I …","說過去的事","Yesterday I went to the park."],
             ["I'm going to … / I want to …","說計畫","I'm going to visit my grandma."],
             ["There is / There are …","描述場景（口說看圖題）","There are three children in the picture."],
             ["I think … is better because …","比較與意見","I think summer is better because we can swim."],
             ["Can you say that again, please?","沒聽懂時（比沉默好一百倍）","Sorry, can you say that again, please?"]],
            ["句型", "用途", "例句"]))
    + sec("劍橋各級口說考什麼（附完整逐字稿）",
      prose("六場練習都附<strong>整場對話的逐字稿與中文對照</strong>，可以直接當跟讀材料用，也能看出各級的難度差在哪。")
      + practice_cards([
        ("/starters-speaking-practice/","Starters 口說","看圖回答・國小低年級起步","逐字稿"),
        ("/movers-speaking-practice/","Movers 口說","看圖說故事","逐字稿"),
        ("/flyers-speaking-practice/","Flyers 口說","找不同・描述圖片","逐字稿"),
        ("/ket-speaking-practice/","KET 口說","CEFR A2・個人問答與配對","逐字稿"),
        ("/pet-speaking-practice/","PET 口說","CEFR B1・討論與長回答","逐字稿"),
        ("/fce-speaking-practice/","FCE 口說","CEFR B2・申論與合作任務","逐字稿"),
      ]))
    + sec("英文口說常見問題", faq([
      ("在家沒有人對話，口說能練嗎？", "能，而且最該先在家練。自問自答、錄音回聽、跟讀逐字稿三種都不需要對象，"
        "練的是提取速度和流暢度。找人對話是驗收，不是起點。"),
      ("孩子怕說錯不敢開口怎麼辦？", "先把「錯」的成本降到零——在家練習時完全不糾正，只計時和錄音。"
        "等他願意開口了，再挑一兩個最影響理解的錯誤處理。一次糾正太多，下次就不講了。"),
      ("口說要先把文法學好嗎？", "不用等。口說用的是固定句型，不是現場組文法。先讓孩子背十個能立刻用的句子"
        "（我叫…、我喜歡…因為…、我昨天去了…），開口之後文法會自己跟上。"),
      ("發音不標準會不會影響口說？", "會影響「聽不聽得懂」，不影響「標不標準」。目標是清楚，不是像母語者。"
        "真正需要修的是會造成誤解的音，像 /l/ 和 /r/、長短母音——其他的口音是特色不是缺點。"),
      ("錄音回聽真的有用嗎？", "這是最被低估的一招。人講話時聽到的自己和別人聽到的不一樣，"
        "錄下來一放，孩子會自己發現問題，不用大人說。每週錄一次三十秒就夠。"),
      ("一天練多久？", "三到五分鐘。口說練的是反射，短而頻繁最有效。每天回答一個問題、錄一次音，"
        "比週末練半小時有用得多。"),
    ]), soft=True)
    + cta("口說是唯一一個非得有人聽你講、當場告訴你哪裡卡住的技能。" + SKILL_FAQ_TAIL)),
  faq_n=6)

PAGES["english-writing-practice"] = dict(
  target="英文寫作", index=0.81,
  h1="英文寫作怎麼練？從寫不出來到寫得完整的方法（附免費練習與範文）",
  title="英文寫作練習：短訊息到短文的方法＋免費題庫與範文解析｜埃森美語",
  desc="英文寫作練習方法：為什麼中翻英寫不好、句型模板怎麼用、短訊息與短文的結構差別，"
       "以及劍橋各級寫作免費練習——每題附範文與逐句中文解析。",
  hero="英文寫作最常見的卡點不是文法，是<strong>先在腦中想好中文再翻譯</strong>——翻出來的句子語序怪、用字硬，"
       "自己也知道不對但改不動。解法是反過來：先學會英文句子長什麼樣，再用它裝內容。",
  body=lambda: (
    sec("中翻英為什麼寫不好",
      prose("中文和英文的組織方式不同。中文可以把主詞省略、把時間放句尾、用逗號一路串下去；"
            "英文每個句子都要有主詞和動詞，時態必須標明，句子之間要有連接詞。",
            "所以逐句翻譯出來的英文，常常是<strong>文法沒錯但讀起來不像英文</strong>。",
            "換掉這個習慣的方法是<strong>句型優先</strong>：先記住幾個英文句子的骨架，寫的時候選一個骨架來裝內容，"
            "而不是先想中文再找對應的字。"))
    + sec("四個能立刻用的骨架",
      prose("<strong>表達意見：</strong>I think (that) … because …<br>"
            "<strong>比較：</strong>A is more … than B. / A is not as … as B.<br>"
            "<strong>舉例：</strong>For example, … / such as …<br>"
            "<strong>轉折：</strong>However, … / Although …, …",
            "四個骨架就能撐起一段完整的短文。先練到不用想就寫得出來，再往上加。",
            "寫完之後<strong>逐句檢查三件事</strong>：每句有沒有主詞和動詞、時態對不對、單複數對不對。"
            "這三樣佔了台灣學生作文扣分的絕大多數。"), soft=True)
    + sec("連接詞對照表：讓句子接起來的 16 個字",
      prose("短文和短訊息的差別在句子之間有沒有「接頭」。這 16 個連接詞依功能分好，寫的時候照功能挑。")
      + tbl([["並列","and / also / as well","I like tea and coffee."],["對比","but / however / although","It was cold, but we went out."],
             ["原因","because / since / as","I stayed home because it rained."],["結果","so / therefore / as a result","It rained, so we stayed home."],
             ["舉例","for example / such as","I like fruit, such as apples."],["順序","first / then / after that / finally","First, mix the eggs. Then add milk."],
             ["補充","in addition / besides","In addition, the food was great."],["條件","if / unless","If it rains, we'll stay in."],
             ["目的","so that / in order to","I study hard so that I can pass."],["時間","when / while / before / after","Call me when you arrive."],
             ["讓步","even though / despite","Even though it was late, we stayed."],["總結","in short / all in all / to sum up","All in all, it was a great trip."]],
            ["功能", "連接詞", "例句"]))
    + sec("短訊息和短文：兩種不同的題型",
      prose("<strong>短訊息（25–35 字）</strong>是劍橋 KET 寫作 Part 6 的題型：讀完一個情境，回覆三件指定的事。"
            "評分看的是<strong>三件事有沒有都回到</strong>，不是文采。寫之前先把三點列出來，一點一句，寫完數一遍。",
            "<strong>短文（80 字以上）</strong>需要結構：開頭一句說立場、中間兩三句給理由和例子、結尾一句收回來。"
            "沒有結構的短文即使文法全對，分數也上不去。",
            "兩種都可以用<a href=\"/english-letter-writing-guide/\">英文書信格式</a>裡的開頭與結尾句直接套。"))
    + sec("免費寫作練習與範文",
      prose("每一題都附<strong>範文與逐句中文解析</strong>——看別人怎麼寫，比自己空想有效得多。")
      + practice_cards([
        ("/ket-rw-practice-part6/","KET 寫作 Part 6","短訊息 25–35 字・附範文","免費"),
        ("/ket-rw-practice-part7/","KET 寫作 Part 7","看圖寫故事","免費"),
        ("/pet-writing-practice-part1/","PET 寫作 Part 1","CEFR B1・電子郵件","免費"),
        ("/fce-writing-practice-part1/","FCE 寫作 Part 1","CEFR B2・議論短文","免費"),
        ("/english-letter-writing-guide/","英文書信格式","開頭、結尾與常用句","對照表"),
        ("/english-self-introduction-kids/","英文自我介紹","範例與句型","範文"),
      ]))
    + sec("英文寫作常見問題", faq([
      ("寫作要先想中文再翻譯嗎？", "盡量不要。先記住幾個英文句型骨架，寫的時候選一個來裝內容。"
        "逐句翻譯出來的英文常常文法沒錯卻不像英文，而且很難自己改回來。"),
      ("字數不夠怎麼辦？", "加理由和例子，不要加形容詞。每個論點後面接一句 because… 或 For example…，"
        "字數自然會夠，而且分數比堆砌形容詞高。"),
      ("孩子作文文法一堆錯，要全改嗎？", "不要。一次只挑一類錯誤處理——這次只看時態，下次只看單複數。"
        "整篇改到滿江紅，孩子只會學到「我不會寫」。"),
      ("KET 寫作的短訊息怎麼拿分？", "題目會指定三件要回應的事，評分看的是三件有沒有都寫到。"
        "動筆前先把三點列出來，一點寫一句，寫完數一遍。這比用字漂亮重要得多。"),
      ("要背範文嗎？", "背句型，不要背整篇。整篇背下來的範文遇到不同題目就用不上，"
        "而且閱卷者看得出來。背四到六個能套進任何題目的骨架比較實用。"),
      ("寫完自己怎麼檢查？", "三步驟：每句有沒有主詞和動詞、時態一致嗎、單複數對嗎。"
        "這三樣佔了絕大多數扣分。唸出聲來檢查特別有效，怪的地方耳朵會先發現。"),
    ]), soft=True)
    + cta("寫作最需要的是有人真的讀完並告訴你哪裡不通。" + SKILL_FAQ_TAIL)),
  faq_n=6)

def collides(slug, target):
    """Refuse to create a second page for a keyword the site already targets.

    Twice in one session I built a page that duplicated an existing one that was
    already ranking (/english-abbreviations/ vs /english-abbreviations-guide/ at
    pos 8.2, /numbers-1-100-english/ vs /english-numbers-guide/ at 9,416 impressions).
    Two pages on one term compete with each other, and the new URL has no history —
    so the richer content belongs on the URL that already ranks.
    """
    import glob as _g
    hits = []
    for f in _g.glob(os.path.join(SITE, "*/index.html")):
        other = os.path.basename(os.path.dirname(f))
        if other == slug:
            continue
        head = open(f, encoding="utf-8").read()[:6000]
        m = re.search(r"<title>(.*?)</title>", head, re.S)
        if m and target and target in m.group(1):
            hits.append(other)
    return hits


def render(slug, cfg):
    shell = open(SHELL, encoding="utf-8").read()
    url = f"{ORIGIN}/{slug}/"
    head = shell.split("</head>")[0]
    head = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{cfg["desc"]}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">',
                  f'<link rel="canonical" href="{url}">', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*">',
                  f'<meta property="og:title" content="{cfg["h1"]}">', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*">',
                  f'<meta property="og:description" content="{cfg["desc"][:110]}">', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*">',
                  f'<meta property="og:url" content="{url}">', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", head, flags=re.S)
    art = {"@context": "https://schema.org", "@type": "Article", "headline": cfg["h1"],
           "description": cfg["desc"][:200], "inLanguage": "zh-Hant-TW",
           "mainEntityOfPage": {"@type": "WebPage", "@id": url},
           "author": {"@type": "Organization", "name": "American English 埃森美語"},
           "publisher": {"@type": "Organization", "name": "American English 埃森美語",
             "logo": {"@type": "ImageObject",
                      "url": ORIGIN + "/assets/img/american-english-banqiao-logo.jpg"}},
           "datePublished": "2026-09-14", "dateModified": "2026-09-14"}
    head = head.rstrip() + '\n<script type="application/ld+json">' + \
        json.dumps(art, ensure_ascii=False, separators=(",", ":")) + "</script>\n"

    main = (f'<main id="top">'
      f'<section class="page-hero"><div class="bg-deco"></div><div class="wrap">'
      f'<div class="breadcrumb reveal"><a href="/">首頁</a> › <a href="/blog/">學習資源</a> › {cfg["target"]}</div>'
      f'<h1 class="reveal d1">{cfg["h1"]}</h1><div class="divider reveal d1"></div>'
      f'<p class="body reveal d2">{cfg["hero"]}</p></div></section>'
      f'{cfg["body"]()}</main>')

    tail = shell.split("</head>", 1)[1]
    tail = re.sub(r'<main id="top">.*?</main>', main, tail, flags=re.S)
    tail = re.sub(r"<!-- AE:CHART.*?<!-- AE:CHART.*?end -->\n?", "", tail, flags=re.S)
    tail = re.sub(r"<!-- AE:ROUTE -->.*?<!-- /AE:ROUTE -->\n?", "", tail, flags=re.S)
    out = head + "</head>" + tail
    d = os.path.join(SITE, slug)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
    rows = out.count("<tr>")
    return rows, len(re.findall(r"[一-鿿]", re.sub(r"<[^>]+>", " ", out))) + \
           len(re.findall(r"\b[A-Za-z]{2,}\b", re.sub(r"<[^>]+>", " ", out)))

def add_to_sitemap(slugs):
    sm = os.path.join(SITE, "sitemap.xml")
    xml = open(sm, encoding="utf-8").read()
    anchor = '  <url><loc>https://americanenglish.com.tw/kk-phonetic-chart/</loc>'
    added = 0
    for s in slugs:
        if f"/{s}/</loc>" in xml:
            continue
        xml = xml.replace(anchor, f'  <url><loc>{ORIGIN}/{s}/</loc>'
                          f'<changefreq>monthly</changefreq><priority>0.8</priority></url>\n' + anchor, 1)
        added += 1
    open(sm, "w", encoding="utf-8").write(xml)
    return added

if __name__ == "__main__":
    want = sys.argv[1:] or list(PAGES)
    total_rows = 0
    for s in want:
        if s not in PAGES:
            print(f"  ?? unknown {s}"); continue
        clash = collides(s, PAGES[s].get("target", ""))
        if clash:
            print(f"  !! /{s}/ targets 「{PAGES[s]['target']}」 which these pages already "
                  f"target: {', '.join('/'+c+'/' for c in clash)}")
            print(f"     Check GSC impressions before proceeding — put the richer content on "
                  f"whichever URL already ranks, do not create a competitor.")
            continue
        r, w = render(s, PAGES[s])
        total_rows += r
        print(f"  /{s}/  {r:4d} rows  {w:5d} words   (pool index {PAGES[s]['index']})")
    n = add_to_sitemap(want)
    print(f"{total_rows} table rows across {len(want)} pages | sitemap: {n} new URLs")
