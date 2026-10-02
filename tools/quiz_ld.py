"""Make a Quiz JSON-LD block acceptable to Google's practice-problem report.

Search Console (2026-10-02) flagged every practice page:
  - Missing field "text" (in "hasPart"): each Question carried its wording in `name` only.
  - Missing field "suggestedAnswer": Google's practice problems are multiple choice (or
    checkbox) only, so a Question without wrong options is invalid there.
  - warnings: encodingFormat and position on the question and its answers.

google_ready() is applied by both generators (tools/prerender_practice.py for the Cambridge /
YLE / vocabulary pages, ae-question-bank/tools/build_gept_pages.py for GEPT):
  - every kept Question gets `text` (same as `name`) and encodingFormat text/html;
  - a true/false item becomes a two-option multiple choice (Yes / No);
  - short-answer and open-ended items are left out of the markup (they stay on the page);
  - each Answer gets encodingFormat, keeps the generator's `position`, and its explanation
    (passed as `_why`) as `comment`; each Question gets a hint (`comment`), the CEFR level as
    educationalAlignment and a typicalAgeRange from the page's level;
  - a page left with no multiple-choice question gets no Quiz block at all (returns None).

Google has announced it is phasing out the practice-problem rich result; the markup is still
valid schema.org and still describes the page, so it is kept clean rather than removed.
"""

FMT = "text/html"

# Typical candidate ages by the page's level (URL prefix). "Typical", not a rule: Cambridge's
# YLE tests are for 7–12-year-olds; GEPT 初級 is mostly sat at 9–15 (LTTC 2025 report).
AGES = [("starters", "7-9"), ("movers", "8-11"), ("flyers", "9-12"), ("ket", "10-15"), ("a2-", "10-15"),
        ("pet", "12-17"), ("b1-", "12-17"), ("fce", "14-"), ("b2-", "14-"), ("gept-kids", "7-12"),
        ("gept-elementary", "9-15"), ("gept-intermediate", "12-18"), ("gept-high-intermediate", "15-")]

# A short, true hint per kind of question (Question.comment).
HINT_LISTEN = "先快速看過選項，聽的時候抓住關鍵字，再刪去明顯不對的選項。"
HINT_GAP = "先看空格前後的字，判斷需要的詞性、時態或搭配，再刪去不合的選項。"
HINT_READ = "回到文章找出題目關鍵字所在的句子，再逐一比對選項。"


def _hint(q, assesses):
    if "Listening" in str(assesses):
        return HINT_LISTEN
    t = q.get("name", "")
    return HINT_GAP if ("___" in t or "格" in t or t.startswith("(")) else HINT_READ


def _ages(url):
    path = str(url or "").split("americanenglish.com.tw/")[-1]
    return next((a for k, a in AGES if path.startswith(k)), None)


def _answer(a, pos=None):
    a = dict(a)
    why = a.pop("_why", None)           # the generator's explanation for this option
    if why:
        a["comment"] = {"@type": "Comment", "text": why, "encodingFormat": FMT}
    a["encodingFormat"] = FMT
    if pos is not None:
        a["position"] = pos
    expl = a.get("answerExplanation")
    if isinstance(expl, dict):
        expl = dict(expl)
        expl.setdefault("encodingFormat", FMT)
        a["answerExplanation"] = expl
    return a


def google_ready(ld):
    if not ld:
        return None
    parts = []
    for q in ld.get("hasPart", []):
        q = dict(q)
        name = (q.get("name") or "").strip()
        kind = q.get("eduQuestionType")
        if kind == "True or false":
            acc = q["acceptedAnswer"]["text"]
            other = "No" if acc == "Yes" else "Yes"
            why = q["acceptedAnswer"].get("_why")     # one explanation covers both: it says which is true
            q["eduQuestionType"] = "Multiple choice"
            q["acceptedAnswer"] = _answer(q["acceptedAnswer"], 0 if acc == "Yes" else 1)
            q["suggestedAnswer"] = [_answer({"@type": "Answer", "text": other, "_why": why}, 0 if other == "Yes" else 1)]
        elif kind != "Multiple choice" or not q.get("suggestedAnswer") or not name:
            continue
        else:
            q["acceptedAnswer"] = _answer(q["acceptedAnswer"], q["acceptedAnswer"].get("position"))
            q["suggestedAnswer"] = [_answer(a, a.get("position")) for a in q["suggestedAnswer"]]
        q["text"] = name
        q["encodingFormat"] = FMT
        q["comment"] = {"@type": "Comment", "text": _hint(q, ld.get("assesses")), "encodingFormat": FMT}
        level = str(ld.get("educationalLevel", "")).replace("CEFR", "").strip()
        if level:
            q["educationalAlignment"] = {"@type": "AlignmentObject", "alignmentType": "educationalLevel",
                                         "educationalFramework": "CEFR", "targetName": level}
        ages = _ages(ld.get("url"))
        if ages:
            q["typicalAgeRange"] = ages
        parts.append(q)
    if not parts:
        return None
    ld = dict(ld)
    ld["hasPart"] = parts
    return ld
