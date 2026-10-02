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
  - each Answer gets encodingFormat and, when the generator passed `position`, keeps it;
  - a page left with no multiple-choice question gets no Quiz block at all (returns None).

Google has announced it is phasing out the practice-problem rich result; the markup is still
valid schema.org and still describes the page, so it is kept clean rather than removed.
"""

FMT = "text/html"


def _answer(a, pos=None):
    a = dict(a)
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
            q["eduQuestionType"] = "Multiple choice"
            q["acceptedAnswer"] = _answer(q["acceptedAnswer"], 0 if acc == "Yes" else 1)
            q["suggestedAnswer"] = [_answer({"@type": "Answer", "text": other}, 0 if other == "Yes" else 1)]
        elif kind != "Multiple choice" or not q.get("suggestedAnswer") or not name:
            continue
        else:
            q["acceptedAnswer"] = _answer(q["acceptedAnswer"], q["acceptedAnswer"].get("position"))
            q["suggestedAnswer"] = [_answer(a, a.get("position")) for a in q["suggestedAnswer"]]
        q["text"] = name
        q["encodingFormat"] = FMT
        parts.append(q)
    if not parts:
        return None
    ld = dict(ld)
    ld["hasPart"] = parts
    return ld
