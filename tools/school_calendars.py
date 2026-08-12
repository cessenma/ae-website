#!/usr/bin/env python3
"""Fetch and parse Banqiao school calendars (行事曆) from their official sites.

Why this exists: a stale 段考 date on a cram-school website is worse than no calendar at all.
A parent who plans around a wrong date will not forgive it. So this re-checks weekly, records
WHEN it last succeeded, and fails loudly rather than quietly serving old data.

Every school calendar itself says 「本行事曆活動如有調整，以校網及各處室通知或公告為主」 — the
school's own notice always wins. That disclaimer must survive onto the published page.

    python3 school_calendars.py            # fetch + parse, write data/school-calendars.json
    python3 school_calendars.py --dry-run  # fetch + parse, print, write nothing
"""
import json, os, re, subprocess, sys, tempfile, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
TPE = timezone(timedelta(hours=8))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "school-calendars.json")

# Edit this list to change which schools appear on the page.
# mode: "pdf"  scrape the homepage for a 行事曆 PDF and parse it
#       "ical" read a public Google Calendar feed (better: live, structured)
#       "link" the school publishes its calendar as an IMAGE — we refuse to OCR a
#              段考 date and link to the source instead. A wrong exam date is the one
#              failure mode that actually damages the school's credibility.
SCHOOLS = [
    # The four schools the site itself claims as walking distance from 中正路 89 巷 4 號:
    # 板橋國中 5 min (~400m) · 板橋國小 5 min · 國光國小 8 min (~650m) · 大觀國小 10 min (~800m).
    # Do NOT add 江翠/海山/新埔/文聖 — our own pages state plainly that those are NOT nearby.
    #
    # These four schools publish calendars in four different ways: an image, a teachers-only
    # Google Form, a section page, and nothing on the homepage. Rather than OCR or guess, this
    # verifies each official location weekly and parses dates ONLY where parsing is safe.
    {"key": "pcjh", "name": "板橋國中", "full": "新北市立板橋國民中學", "walk": "步行 5 分鐘",
     "home": "https://www.pcjh.ntpc.edu.tw/", "page": "/junior-high-english-banqiao/",
     "calendar_page": "https://www.pcjh.ntpc.edu.tw/p/406-1000-10824,r62.php",
     "note": "行事曆以圖片公告，本頁不轉錄日期。"},
    {"key": "pcps", "name": "板橋國小", "full": "新北市板橋區板橋國民小學", "walk": "步行 5 分鐘",
     "home": "https://www.pcps.ntpc.edu.tw/", "page": "/banqiao-elementary-school-english/",
     "calendar_page": "https://www.pcps.ntpc.edu.tw/", "note": ""},
    {"key": "kkes", "name": "國光國小", "full": "新北市板橋區國光國民小學", "walk": "步行 8 分鐘",
     "home": "https://www.kkes.ntpc.edu.tw/", "page": "/guoguang-elementary-english/",
     "calendar_page": "https://www.kkes.ntpc.edu.tw/p/403-1000-36.php", "note": ""},
    {"key": "tgps", "name": "大觀國小", "full": "新北市板橋區大觀國民小學", "walk": "步行 10 分鐘",
     "home": "https://www.tgps.ntpc.edu.tw/", "page": "/daguan-elementary-english/",
     "calendar_page": "https://www.tgps.ntpc.edu.tw/", "note": ""},
]


LOOKAHEAD_DAYS = 150   # roughly one semester of "what's coming up"


def academic_year_window(now):
    """Taiwan 學年度 runs Aug 1 → Jul 31. Returns (start, end, roc_year)."""
    y = now.year if now.month >= 8 else now.year - 1
    return datetime(y, 8, 1, tzinfo=TPE), datetime(y + 1, 7, 31, tzinfo=TPE), y - 1911


def rolling_window(now):
    """What a parent actually wants: what is coming up, not the whole year.

    Also degrades gracefully — a school that has not yet published next semester
    simply shows nothing, instead of the page looking broken.
    """
    return now - timedelta(days=7), now + timedelta(days=LOOKAHEAD_DAYS)


def infer_year(month, now):
    """PDF calendars print MMDD with no year. A 上學期 calendar runs Aug→Jan."""
    return now.year if month >= 8 else now.year + (1 if now.month >= 8 else 0)


def ical_events(cal_id, now):
    """Read a public Google Calendar and keep this academic year's key events."""
    enc = urllib.parse.quote(cal_id)
    txt = get(f"https://calendar.google.com/calendar/ical/{enc}/public/basic.ics")
    start, end = rolling_window(now)
    events, seen = [], set()
    for blk in txt.split("BEGIN:VEVENT")[1:]:
        d = re.search(r"DTSTART[^:]*:(\d{4})(\d{2})(\d{2})", blk)
        sm = re.search(r"SUMMARY:(.+)", blk)
        if not d or not sm:
            continue
        yy, mm, dd = int(d.group(1)), int(d.group(2)), int(d.group(3))
        try:
            when = datetime(yy, mm, dd, tzinfo=TPE)
        except ValueError:
            continue
        if not (start <= when <= end):
            continue
        label = re.sub(r"\\,", ",", sm.group(1)).strip()[:48]
        for kind, rx in EVENT_KINDS:
            if not rx.search(label):
                continue
            k = (mm, dd, kind, label)
            if k in seen:
                break
            seen.add(k)
            events.append({"month": mm, "day": dd, "year": yy,
                           "kind": kind, "label": label})
            break
    events.sort(key=lambda e: (e["year"], e["month"], e["day"]))
    return events

# Events worth surfacing to a parent. Order matters — first match wins.
EVENT_KINDS = [
    ("段考",     re.compile(r"第\s*[一二三1-3]\s*次\s*段考|段考")),
    ("定期評量", re.compile(r"定期評量|學習評量")),
    ("開學",     re.compile(r"開學")),
    ("休業式",   re.compile(r"休業式|結業式")),
    ("寒暑假",   re.compile(r"寒假開始|暑假開始")),
    ("校慶",     re.compile(r"校慶|運動會")),
    ("親師",     re.compile(r"親師|班親會")),
]
DATE_RE = re.compile(r"(?<!\d)(\d{2})(\d{2})(?!\d)")


def get(url, binary=False, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Language": "zh-TW,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return raw if binary else raw.decode("utf-8", "replace")


def _file_links(html, base):
    """Any downloadable file link on a page, PDF first."""
    out = []
    for m in re.finditer(r'href="([^"]+)"', html, re.I):
        h = m.group(1)
        if re.search(r"\.(pdf)(\?|$)", h, re.I):
            out.insert(0, urllib.parse.urljoin(base, h))
        elif re.search(r"/var/file/|download|attach", h, re.I) and not re.search(
                r"\.(css|js|png|jpe?g|gif|webp|ico|svg)(\?|$)", h, re.I):
            out.append(urllib.parse.urljoin(base, h))
    return list(dict.fromkeys(out))


def find_calendar_pdf(home, extra_page=None):
    """Find the newest 行事曆 PDF.

    New Taipei school sites use two patterns: a direct PDF link on the homepage, or a
    link to an announcement page that carries the file. This follows one hop.
    """
    html = get(home)
    cands = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
        href, text = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        text = re.sub(r"\s+|&nbsp;", "", text)
        if not re.search(r"行事曆|行事歷|校曆", text):
            continue
        score = 0
        if re.search(r"\(\s*上\s*\)|上學期|第1學期|第一學期", text):
            score += 10
        yr = re.search(r"(1[0-2]\d)", text)
        if yr:
            score += int(yr.group(1))
        cands.append((score, urllib.parse.urljoin(home, href), text))
    if extra_page:
        cands.append((-1, extra_page, "（指定公告頁）"))
    if not cands:
        raise ValueError("no link containing 行事曆 found on the homepage")
    cands.sort(reverse=True)

    for _, url, text in cands[:4]:
        if re.search(r"\.pdf(\?|$)", url, re.I):
            return url, text
        # one hop: the link is an announcement page holding the file
        try:
            page = get(url)
        except Exception:
            continue
        for f in _file_links(page, url):
            try:
                head = get(f, binary=True)[:5]
            except Exception:
                continue
            if head.startswith(b"%PDF"):
                return f, text
    raise ValueError(f"found {len(cands)} 行事曆 link(s) but no PDF behind any of them")


def pdf_text(url):
    raw = get(url, binary=True)
    if not raw[:5].startswith(b"%PDF"):
        raise ValueError(f"not a PDF (got {raw[:16]!r})")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(raw)
        tmp = f.name
    try:
        # pdftotext -layout is required: pypdf inserts a space between every CJK
        # character, which silently breaks every keyword match.
        out = subprocess.run(["pdftotext", "-layout", tmp, "-"],
                             capture_output=True, timeout=60)
        if out.returncode != 0:
            raise ValueError(f"pdftotext failed: {out.stderr[:120]!r}")
        return out.stdout.decode("utf-8", "replace")
    finally:
        os.unlink(tmp)


def parse_events(text, now=None):
    """Pull MMDD-coded events out of the calendar's own notation."""
    now = now or datetime.now(TPE)
    lo, hi = rolling_window(now)
    events, seen = [], set()
    for line in text.splitlines():
        line = re.sub(r"\s{2,}", "  ", line).strip()
        if len(line) < 6:
            continue
        for m in DATE_RE.finditer(line):
            mm, dd = m.group(1), m.group(2)
            if not (1 <= int(mm) <= 12 and 1 <= int(dd) <= 31):
                continue
            tail = line[m.end():m.end() + 60].strip(" -–—")
            if len(tail) < 2:
                continue
            for kind, rx in EVENT_KINDS:
                if not rx.search(tail):
                    continue
                label = re.split(r"\s{2,}", tail)[0][:48]
                k = (mm, dd, kind, label)
                if k in seen:
                    break
                seen.add(k)
                yy = infer_year(int(mm), now)
                try:
                    when = datetime(yy, int(mm), int(dd), tzinfo=TPE)
                except ValueError:
                    break
                if not (lo <= when <= hi):
                    break
                events.append({"year": yy, "month": int(mm), "day": int(dd),
                               "kind": kind, "label": label})
                break
    events.sort(key=lambda e: (e["year"], e["month"], e["day"]))
    return events


def check(url):
    """Confirm a URL still resolves. Returns (ok, status, bytes)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
        return True, r.status, len(body)
    except Exception as e:
        return False, getattr(e, "code", type(e).__name__), 0


def main():
    dry = "--dry-run" in sys.argv
    now = datetime.now(TPE)
    out = {"checked_at": now.strftime("%Y-%m-%d %H:%M"), "schools": [], "errors": []}

    for s in SCHOOLS:
        rec = dict(s)
        ok, status, size = check(s["calendar_page"])
        rec["link_ok"], rec["http"], rec["bytes"] = ok, status, size
        rec["events"] = []
        # Opportunistic: if a real PDF calendar is discoverable, parse it. Never required.
        try:
            pdf_url, label = find_calendar_pdf(s["home"], s.get("calendar_page"))
            rec["pdf_url"], rec["pdf_label"] = pdf_url, label
            evs = parse_events(pdf_text(pdf_url), now)
            if evs:
                rec["events"] = evs
        except Exception as e:
            rec["parse_note"] = f"{type(e).__name__}: {e}"[:120]

        n = len(rec["events"])
        exam = sum(1 for e in rec["events"] if e["kind"] == "段考")
        if not ok:
            out["errors"].append(f"{s['name']}: 行事曆頁無法連線 (HTTP {status})")
            print(f"  ✗ {s['name']:<8} LINK DEAD (HTTP {status})")
        elif n:
            print(f"  ✓ {s['name']:<8} link ok · {n} events parsed ({exam} 段考)")
        else:
            print(f"  · {s['name']:<8} link ok · dates not parsed → linking to source")
        out["schools"].append(rec)

    dead = len(out["errors"])
    print(f"\n  {len(SCHOOLS)-dead}/{len(SCHOOLS)} official calendar pages reachable "
          f"at {out['checked_at']}")
    if dry:
        print("\n(dry run — nothing written)")
        return 1 if dead else 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  wrote {OUT}")
    # Red only if a school's official page has MOVED or died — that is the thing a
    # weekly job must catch. "Dates not parseable" is a known, permanent condition
    # for these four schools and must not cry wolf every week.
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
