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
    inner = "".join(f'<div class="faq-item"><h3 class="faq-h">{q}</h3>'
                    f'<div class="faq-a">{a}</div></div>' for q, a in items)
    return f'<div class="faq">{inner}</div>'

def cta(line):
    # bg-blue is the site's closing-CTA convention and the anchor route_blocks.py
    # inserts its "what next" section before — without it the page gets no route block.
    return ('<section class="section bg-blue"><div class="wrap"><div class="center stack reveal">'
            f'<h2>單字背起來了，用得出來嗎？</h2><p class="body">{line}</p>'
            '<a class="btn btn-primary" href="/line/">預約免費試上一堂</a></div></div></section>')

N  = DATA["numbers"]; M = DATA["months"]; D = DATA["days"]

PAGES = {
"numbers-1-100-english": dict(
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
        "<strong>四個不規則拼法要單獨記</strong>：four 有 u，但 forty <u>沒有</u> u（不是 fourty）；five 變 fifteen 和 fifty；nine 變 ninety（去掉 e）；eight 加 h 變 eighteen、eighty。",
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
"colors-english": dict(
  target="顏色英文", index=1.28,
  h1="顏色英文對照表：62 個常用顏色、深淺說法與 colour／color 的差別",
  title="顏色英文62個對照表：深淺說法、拼法差異與形容詞順序｜埃森美語",
  desc="顏色英文完整對照表，收錄 62 個常用顏色與中文對照，分基本色、深淺、紅粉紫、黃橙棕與藍綠五組；並說明 colour 與 color 的拼法差別、light／dark 的用法，以及顏色在形容詞裡的正確位置。",
  hero="顏色是孩子最早學會的一批英文單字，但大多數人停在十個基本色就沒再往下走。下面這份表收了 62 個，分成五組——先給表，再講三個真正會用到的規則。",
  body=lambda: (
    sec("顏色英文對照表（62 個）",
      prose("按色系分組，找起來比按字母快。深淺的說法在第二組，實際寫作最常用到。")
      + grouped([(g[0], [[w, z] for w, z in g[1]]) for g in DATA["colors"]], ["英文", "中文"]))
    + sec("colour 還是 color？",
      prose("<strong>color 是美式，colour 是英式</strong>，兩個都正確。同一組差異還有 grey（英）／gray（美）。",
        "台灣的教科書與劍橋、全民英檢多採<strong>英式</strong>拼法，多益與美系教材則用美式。考試不會因為你用另一套而扣分，但<strong>同一篇文章裡必須一致</strong>——這才是真正會被扣分的地方。"), soft=True)
    + sec("深淺怎麼說：light、dark 與 -ish",
      prose("<strong>light + 顏色</strong> = 淺（light blue 淺藍）；<strong>dark + 顏色</strong> = 深（dark green 深綠）。",
        "<strong>pale</strong> 比 light 更淡、偏無血色；<strong>bright</strong> 是鮮豔；<strong>deep</strong> 比 dark 更濃郁。",
        "口語裡還有一個好用的字尾 <strong>-ish</strong>，表示「有點…色的」：reddish（偏紅）、greenish（帶點綠）。不確定是什麼顏色時特別好用。"))
    + sec("顏色放在形容詞的哪個位置",
      prose("英文形容詞有固定順序，顏色排在<strong>倒數第三</strong>：<em>數量 → 評價 → 大小 → 形狀 → 年齡 → 顏色 → 來源 → 材質 → 用途 → 名詞</em>。",
        "所以是 <strong>a big old red wooden box</strong>，不是 a red old big wooden box。母語者不會背這個順序，但講錯會立刻聽出來。",
        "實務上很少同時用到五個形容詞，記住「<strong>顏色永遠緊貼在材質前面</strong>」就夠應付大部分句子。"), soft=True)
    + sec("顏色英文常見問題", faq([
      ("colour 和 color 哪個對？", "都對。colour 是英式、color 是美式，grey／gray 同理。台灣教科書和劍橋考試偏英式，多益偏美式。重點是同一篇文章從頭到尾一致。"),
      ("淺藍色的英文是什麼？", "light blue。更淡可以說 pale blue，天空那種藍是 sky blue，很淺的嬰兒藍是 baby blue。深藍則是 dark blue 或 navy。"),
      ("顏色可以當名詞用嗎？", "可以。Red is my favourite colour（紅色是我最喜歡的顏色）裡 red 就是名詞。當形容詞時放在名詞前：a red car。"),
      ("金色銀色算顏色嗎？", "算，gold 和 silver 既是金屬也是顏色。它們同時可以當名詞和形容詞：a gold medal、painted silver。"),
      ("孩子幾歲學顏色最好？", "學齡前就可以，顏色是最容易「指著實物說」的一類字。建議直接在生活裡教——穿衣服、吃水果、玩積木時順口問一句，比看字卡有效得多。"),
      ("為什麼有些顏色要加 -ish？", "-ish 表示「大約、有點」，用在不確定或介於兩色之間時：reddish 偏紅、yellowish 偏黃。這個字尾也能用在其他形容詞上，像 tallish（有點高）。"),
    ]), soft=True)
    + cta("顏色、水果、動物這些字，孩子背得起來卻用不出來，原因通常是從沒在句子裡講過。我們的課堂用實物和遊戲練，說出口的頻率比看字卡高得多。")),
  faq_n=6),

"fruits-english": dict(
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
 ("/numbers-1-100-english/", "英文數字 1-100", "0 到 100 完整拼法，附 13／30 的分辨方法", "101"),
 ("/months-english/", "月份英文 1-12", "月份、縮寫與天數，in／on 用法一次說清", "12"),
 ("/days-of-week-english/", "星期英文", "七天的縮寫、口語說法與 on Monday 的差別", "7"),
 ("/colors-english/", "顏色英文", "62 個顏色分五組，含深淺說法與拼法差異", "62"),
 ("/fruits-english/", "水果英文", "47 種水果，含芭樂、蓮霧、釋迦等台灣水果", "47"),
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
        prose("每一頁都是完整對照表，不是節錄；每個英文字旁邊的喇叭可以點開聽發音，"
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
        r, w = render(s, PAGES[s])
        total_rows += r
        print(f"  /{s}/  {r:4d} rows  {w:5d} words   (pool index {PAGES[s]['index']})")
    n = add_to_sitemap(want)
    print(f"{total_rows} table rows across {len(want)} pages | sitemap: {n} new URLs")
