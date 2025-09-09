# src/siiha_sdk/calendar.py
from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import pytz
from dateutil.parser import isoparse

from siiha_sdk.auth import get_calendar_service
from siiha_sdk.utils import cleanse_text, normalize_attendees
from siiha_sdk.config import DEFAULT_TIMEZONE, DEFAULT_CALENDAR_ID, GOOGLE_SEND_UPDATES

TZ = pytz.timezone(DEFAULT_TIMEZONE)

# ---------- helpers for robust dedupe ----------

def _norm_title(s: Optional[str]) -> str:
    """標題正規化：trim / 合併空白 / 統一逗號 / 英文大小寫無關"""
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("，", ",")
    s = re.sub(r"\s*,\s*", ", ", s)
    return s.casefold()

def _same_instant(a_iso: str, b_iso: str) -> bool:
    """兩個 RFC3339 是否指向同一瞬間（跨時區也成立）"""
    try:
        return isoparse(a_iso) == isoparse(b_iso)
    except Exception:
        return False

def _day_window(start_iso: str) -> tuple[str, str]:
    """在 Asia/Taipei 展開該天的整日窗口（避免 Z 導致 UTC 偏移）。"""
    dt = isoparse(start_iso)                 # aware datetime
    dt_local = dt.astimezone(TZ)             # 轉成本地時區再切日界
    start_of_day = dt_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    return start_of_day.isoformat(), end_of_day.isoformat()

def find_existing_event(service, title: str, start_iso: str) -> Optional[Dict]:
    """同一天窗內：『同一瞬間』且『標題正規化後相等』→ 視為重複。"""
    tmin, tmax = _day_window(start_iso)
    want_title = _norm_title(title)

    res = service.events().list(
        calendarId=DEFAULT_CALENDAR_ID,
        q=want_title,                 # 只作為篩選提示；實際仍做嚴格比對
        timeMin=tmin,
        timeMax=tmax,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    for e in res.get("items", []):
        e_start_iso = e.get("start", {}).get("dateTime")
        if not e_start_iso:
            # 跳過全日事件（若未來要支援，再另開邏輯）
            continue
        same = _same_instant(e_start_iso, start_iso)
        same_title = _norm_title(e.get("summary")) == want_title
        if same and same_title:
            return e
    return None

# ---------- public API ----------

def create_calendar_event(
    title: str,
    start_iso: str,
    end_iso: str,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    description: Optional[str] = None,
    timezone: str = DEFAULT_TIMEZONE,
    dedupe: bool = True,
) -> Dict:
    """
    Create a Google Calendar event (local OAuth).
    Assumes start_iso/end_iso are RFC3339 strings WITH timezone.
    """
    try:
        service = get_calendar_service()

        title = cleanse_text(title) or ""
        location = cleanse_text(location)
        description = cleanse_text(description)
        attendees = normalize_attendees(attendees)

        if dedupe:
            existing = find_existing_event(service, title, start_iso)
            if existing:
                return {
                    "ok": True,
                    "eventId": existing["id"],
                    "htmlLink": existing.get("htmlLink"),
                    "start": existing["start"].get("dateTime"),
                    "end": existing["end"].get("dateTime"),
                    "attendees": [a["email"] for a in existing.get("attendees", [])],
                    "timezone": timezone,
                    "deduped": True,
                }

        body = {
            "summary": title,
            "location": location,
            "description": description,
            "start": {"dateTime": start_iso, "timeZone": timezone},
            "end": {"dateTime": end_iso, "timeZone": timezone},
        }
        if attendees:
            body["attendees"] = [{"email": e} for e in attendees]

        event = service.events().insert(
            calendarId=DEFAULT_CALENDAR_ID,
            body=body,
            sendUpdates=GOOGLE_SEND_UPDATES,
        ).execute()

        return {
            "ok": True,
            "eventId": event["id"],
            "htmlLink": event.get("htmlLink"),
            "start": event["start"].get("dateTime"),
            "end": event["end"].get("dateTime"),
            "attendees": [a["email"] for a in event.get("attendees", [])],
            "timezone": timezone,
            "deduped": False,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ======== SDK additions: tidy_title / parsing helpers / parse_event ========
import json
from dateutil import parser as dateparser

MIN_DUR, MAX_DUR = 5, 180
EMAIL_RE = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")

# --- title tidy（收斂自 UI 版） ---
_TITLE_TRASH_PREFIX = re.compile(
    r'(?i)^\s*(?:now|next|this|today|tomorrow|tmr|'
    r'(?:next|this)\s+(?:mon|tue|wed|thu|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday))'
    r'\s*[:：,\-–—]*\s*'
)
_TITLE_VERB_PREFIX = re.compile(
    r'(?i)^\s*(?:create|add|schedule|set\s*up|安排|建立|新增|排(?:會議|行程)?)\s+'
    r'(?:a\s+)?(?:calendar\s+)?(?:event|meeting)\s*:?-?\s*|^\s*(?:create|add|schedule|set\s*up|安排|建立|新增|排(?:會議|行程)?)\s*'
)
_TITLE_INVITE_TAIL  = re.compile(r'(?i)[,;，；]\s*(?:invite|invites?|邀請|受邀)\b.*$')
_TITLE_TIME_CHUNKS  = re.compile(
    r'(?i)\b(?:'
    r'(?:\d{4}[/-]\d{1,2}[/-]\d{1,2})|'                           # 2025-09-10 / 2025/09/10
    r'(?:\d{1,2}/\d{1,2}(?:/\d{2,4})?)|'                          # 9/10, 09/10/2025（僅保留 /，避免 9-10 與時間衝突）
    r'(?:\d{1,2}:[0-5]\d)|'                                       # 裸 HH:MM
    r'(?:\d{1,2}(:[0-5]\d)?\s*(?:am|pm))|'                        # 10am, 10:30pm
    r'(?:\d{1,2}(:[0-5]\d)?\s*[-–—]\s*\d{1,2}(:[0-5]\d)?\s*(?:am|pm)?)|'  # 9-10am, 9:00–10:00
    r'(?:\b[0-2]?\d\s*[-–—]\s*[0-2]?\d\b)|'                       # 裸小時區間 9-10    
    r'(?:from\s+\d{1,2}(:[0-5]\d)?\s*(?:am|pm)?\s*[-–—]\s*\d{1,2}(:[0-5]\d)?\s*(?:am|pm)?)|'
    r'(?:at\s+\d{1,2}(:[0-5]\d)?\s*(?:am|pm)?)'
    r')\b'
)
_TITLE_AT_LOC = re.compile(r'(?i)\s*(?:,|，)?\s*(?:at|@|在|於)\s+[^\s,，。]+$')
_TITLE_REL_PHRASES = re.compile(
    r'(?i)\b(?:in\s+\d+\s*(?:hours?|hrs?|minutes?|mins?)|for\s+\d+\s*(?:hours?|hrs?|minutes?|mins?))\b'
    r'|[一二兩三四五六七八九十\d]+\s*(?:小時半|小時|分鐘)'
)
_TITLE_LABEL_FIELDS = re.compile(
    r'(?i)\b(?:start|end|開始|結束|title)\s*[:：]\s*[^\n,;，；]+'
)

def tidy_title(title: str, idea_text: str = "") -> str:
    s = (title or "").strip().strip('"\'')
    if not s:
        s = (idea_text or "").strip()
    # 先清掉 email，避免殘留在標題
    s = EMAIL_RE.sub("", s)
    # 也清掉明確欄位標籤（start:, end:, title:）
    s = _TITLE_LABEL_FIELDS.sub("", s)
    s = _TITLE_TRASH_PREFIX.sub("", s)
    s = _TITLE_VERB_PREFIX.sub("", s)
    s = _TITLE_INVITE_TAIL.sub("", s)
    s = _TITLE_TIME_CHUNKS.sub("", s)
    s = _TITLE_REL_PHRASES.sub("", s)
    s = _TITLE_AT_LOC.sub("", s)
    s = re.sub(r"\s*[-–—]+\s*(?=with\b)", " ", s, flags=re.I)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[,\，；;]\s*(?=[,\，；;])", "", s)
    # 去掉可能因移除 email 造成的尾端 to/給
    s = re.sub(r"(?i)\b(?:to|給)\b\s*$", "", s)
    s = s.strip(" ,，。．;；-–—")
    return (s or "Meeting")[:80]

# --- generic helpers（純函式） ---
_TIME_ONLY = re.compile(r'(?i)^\s*\d{1,2}(:[0-5]\d)?\s*(?:am|pm)?\s*$')
_DATE_TOKEN = re.compile(
    r'(?i)\b(today|tomorrow|tmr|day\s+after\s+tomorrow|this|next|mon|tue|wed|thu|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
    r'|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'                           # 年-月-日 / 年/月/日
    r'|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b'                           # 僅允許 / 形式的月/日，避免把 9-10 誤當日期
    r'|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b'    
)

def looks_like_time_string(s: str) -> bool:
    return bool(s and _TIME_ONLY.match(s.strip()))

def has_explicit_date(text: str) -> bool:
    return bool(text and _DATE_TOKEN.search(text))

_ZH_NUM = {"零":0,"一":1,"二":2,"兩":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}
def _zh_to_int(s: str) -> int:
    if not s: return 0
    if s.isdigit(): return int(s)
    if "十" in s:
        a,b = s.split("十", 1)
        tens = _ZH_NUM.get(a, 1 if a=="" else 0)
        ones = _ZH_NUM.get(b, 0) if b != "" else 0
        return tens*10 + ones
    return _ZH_NUM.get(s, 0)

_REL_PATS = [
    re.compile(r"\bin\s+(\d+)\s*(minutes?|mins?)\b", re.I),
    re.compile(r"\bin\s+(\d+)\s*(hours?|hrs?)\b", re.I),
    re.compile(r"\bin\s+(\d+)\s*(days?)\b", re.I),
    re.compile(r"\b(\d+)\s*(minutes?|mins?)\s+later\b", re.I),
    re.compile(r"\b(\d+)\s*(hours?|hrs?)\s+later\b", re.I),
    re.compile(r"\b(\d+)\s*(days?)\s+later\b", re.I),
    re.compile(r"([一二兩三四五六七八九十]+)\s*分鐘後"),
    re.compile(r"([一二兩三四五六七八九十]+)\s*小時後"),
    re.compile(r"([一二兩三四五六七八九十]+)\s*天後"),
]

def _parse_relative_offset(text: str, tz: str) -> Optional[datetime]:
    if not text: return None
    now = datetime.now(pytz.timezone(tz))
    s = text.strip()
    for pat in _REL_PATS:
        m = pat.search(s)
        if not m: continue
        g1 = m.group(1)
        if g1.isdigit():
            n = int(g1)
            unit = m.group(2).lower() if len(m.groups()) >= 2 else ""
        else:
            n = _zh_to_int(g1)
            unit = "分鐘" if "分鐘" in pat.pattern else ("小時" if "小時" in pat.pattern else "天")
        if n <= 0: return now
        if unit.startswith(("min","分鐘")):  return now + timedelta(minutes=n)
        if unit.startswith(("hour","hr","小時")): return now + timedelta(hours=n)
        return now + timedelta(days=n)
    if re.search(r"\bday after tomorrow\b|後天", s, re.I): return now + timedelta(days=2)
    if re.search(r"\btomorrow\b|明天", s, re.I): return now + timedelta(days=1)
    return None

def _coerce_datetime(x, tz: str):
    """str/dict/datetime -> aware datetime( tz )；失敗回 None"""
    # 統一本函式以 local tz 產生 aware dt，供上層再做微調
    # 相對詞優先，其次自然語句，再退 ISO    
    if not x: return None
    if isinstance(x, datetime):
        return x if x.tzinfo else pytz.timezone(tz).localize(x)
    if isinstance(x, dict):
        x = x.get("dateTime") or x.get("date") or ""
    # 相對詞優先
    rel = _parse_relative_offset(str(x), tz)
    if rel: return rel
    try:
        # default 決定未給日期時以今天 00:00 為基準
        def_dt = datetime.now(pytz.timezone(tz)).replace(hour=0, minute=0, second=0, microsecond=0)
        dt = dateparser.parse(str(x), fuzzy=True, default=def_dt)
        if dt.tzinfo is None:
            dt = pytz.timezone(tz).localize(dt)
        return dt
    except Exception:
        try:
            dt = isoparse(str(x))
            return dt if dt.tzinfo else pytz.timezone(tz).localize(dt)
        except Exception:
            return None

def _to_rfc3339_any(x, tz: str) -> Optional[str]:
    dt = _coerce_datetime(x, tz)
    return dt.isoformat() if dt else None

_ONLY_HHMM = re.compile(r'^\s*([0-2]?\d):([0-5]\d)\s*$')
_SIMPLE_RANGE_HH = re.compile(r'\b([0-2]?\d)\s*[-–—~]\s*([0-2]?\d)\b')
# 小時區間（僅小時，無分鐘）：避免吃到日期的連字號，要求左右不是「-」或數字
_HOUR_RANGE = re.compile(r'(?<!\d)(?<!-)\b([01]?\d|2[0-3])\s*[-–—~]\s*([01]?\d|2[0-3])\b(?!-)(?!\d)')
# 僅小時（可帶 am/pm）
_ONLY_HH = re.compile(r'^\s*([0-2]?\d)\s*(am|pm)?\s*$', re.I)
# 任兩個時間 token（HH[:MM][am/pm]?），供「無 dash」情境用；遇到明確日期則不啟動
_TIME_TOK  = re.compile(r'\b([01]?\d|2[0-3])(?::([0-5]\d))?\s*(am|pm)?\b', re.I)

def _extract_duration_minutes(s: str) -> Optional[int]:
    if not s: return None
    m = re.search(r"\bfor\s+(\d+(?:\.\d+)?)\s*(hours?|hrs?)\b", s, re.I)
    if m: return int(round(float(m.group(1))*60))
    m = re.search(r"\bfor\s+(\d+(?:\.\d+)?)\s*(minutes?|mins?)\b", s, re.I)
    if m: return int(round(float(m.group(1))))
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(hours?|hrs?)\b", s, re.I)
    if m: return int(round(float(m.group(1))*60))
    m = re.search(r"\b(\d+)\s*(minutes?|mins?)\b", s, re.I)
    if m: return int(m.group(1))
    if "半小時" in s or "半個小時" in s: return 30
    m = re.search(r"([一二兩三四五六七八九十\d]+)\s*小時半", s)
    if m: return _zh_to_int(m.group(1))*60 + 30
    m = re.search(r"([一二兩三四五六七八九十\d]+)\s*小時", s)
    if m: return _zh_to_int(m.group(1))*60
    m = re.search(r"([一二兩三四五六七八九十\d]+)\s*分鐘", s)
    if m: return _zh_to_int(m.group(1))
    return None

def _split_emails(s: str) -> list[str]:
    if not s: return []
    out, seen = [], set()
    for em in EMAIL_RE.findall(s):
        em = em.lower()
        if em not in seen:
            out.append(em); seen.add(em)
    return out

def parse_event(text: str, tz: str = DEFAULT_TIMEZONE, default_minutes: int = 60) -> Dict:
    """
    解析自然語句為事件：title/body/location/attendees/start/end/timeZone/flags。
    - 若只給時間或含 today/今天，且開始時間已過 → 自動 +1 天（flags 含 "rolled_to_next_day"）
    - 回傳 start/end 為 RFC3339（含 tz）；可能為 None
    - 盡量避免把 'at 10AM …' 當成地點
    """
    s = (text or "").strip()
    tz = tz or DEFAULT_TIMEZONE
    flags: list[str] = []
    now = datetime.now(pytz.timezone(tz))
    used_labeled = False

    # 抽可能的 body/location/attendees（極簡規則）
    body = ""
    m = re.search(r"\b(body|description)\s*[:：]\s*([^\n]+)", s, re.I)
    if m: body = m.group(2).strip()

    location = None
    m = re.search(r"(?:\blocation\b|地點)\s*[:：]\s*([^\n,;]+)", s, re.I)
    if not m:
        m = re.search(r"\bat\s+([^\n,;]+)", s, re.I)
    if m:
        cand = m.group(1).strip()
        if not looks_like_time_string(cand):
            location = cand

    attendees = _split_emails(s)

    # start/end 解析（1）顯式 start:/end:
    # 注意：start 的值改成「非貪婪」，並在下一個 end 標籤/分隔符/行尾前停下，避免吃到 end 內容
    ms = re.search(r"\bstart\s*[:：]\s*([^\n]+?)(?=\s+\bend\b|[,;，、]|$)", s, re.I)
    # end 支援 HH、HH:MM、HH(am/pm)
    me = re.search(r"\bend\s*[:：]\s*([0-2]?\d(?::[0-5]\d)?(?:\s*(?:am|pm))?)", s, re.I)    

    start_dt = _coerce_datetime(ms.group(1), tz) if ms else None
    end_dt   = _coerce_datetime(me.group(1), tz) if me else None
    used_labeled = bool(ms or me)
    # 若 end 只有 HH:MM，且有 start 的日期 → 用 start 的日期補齊
    if start_dt and me:
        raw_e = (me.group(1) or "").strip()
        mhm = _ONLY_HHMM.match(raw_e)
        if mhm:
            hh, mm = int(mhm.group(1)), int(mhm.group(2))
            end_dt = start_dt.replace(hour=hh, minute=mm, second=0, microsecond=0)
        else:
            mh = _ONLY_HH.match(raw_e)
            if mh:
                hh = int(mh.group(1))
                ap = (mh.group(2) or "").lower()
                if ap in ("am","pm"):
                    hh = (0 if hh == 12 else hh) + (12 if ap == "pm" else 0)
                end_dt = start_dt.replace(hour=hh, minute=0, second=0, microsecond=0)

    # start/end 解析（2）時間區間 like '9:00–10:00'
    if not (start_dt and end_dt):
        m = re.search(r"\b([0-2]?\d:[0-5]\d)\s*[-–—~]\s*([0-2]?\d:[0-5]\d)\b", s)
        if m:
            h1, h2 = m.group(1), m.group(2)
            base = now.replace(second=0, microsecond=0)
            start_dt = pytz.timezone(tz).localize(dateparser.parse(h1, default=base))
            end_dt   = pytz.timezone(tz).localize(dateparser.parse(h2, default=base))

    # start/end 解析（2-2）裸小時區間 '9-10' → 09:00–10:00（以當地時區今日為基準）
    if not (start_dt and end_dt):
        m = _SIMPLE_RANGE_HH.search(s)
        if m:
            h1, h2 = int(m.group(1)), int(m.group(2))
            # 小的當 start，大的當 end；避免誤解為 21–22
            if h1 > h2:
                h1, h2 = h2, h1
            base = now.astimezone(pytz.timezone(tz))
            start_dt = base.replace(hour=h1, minute=0, second=0, microsecond=0)
            end_dt   = base.replace(hour=h2, minute=0, second=0, microsecond=0)

    # start/end 解析（2b）僅小時區間：'9-10' → 09:00–10:00（以當地時區當天為基準）
    if not (start_dt and end_dt):
        m = _HOUR_RANGE.search(s)
        if m:
            h1, h2 = int(m.group(1)), int(m.group(2))
            base = now.replace(minute=0, second=0, microsecond=0)
            sdt = base.replace(hour=h1)
            edt = base.replace(hour=h2)
            # 小的當 start，大的當 end
            start_dt, end_dt = (sdt, edt) if h1 <= h2 else (edt, sdt)

    # start/end 解析（2c）兩個時間 token 無 dash：小的當 start，大的當 end
    # 僅在「沒有明確日期」時啟用，避免把 2025-09-10 的「09」「10」當時間
    if not (start_dt and end_dt) and not has_explicit_date(s):
        toks = list(_TIME_TOK.finditer(s))
        if len(toks) >= 2:
            def _tok_to_minutes(m):
                h = int(m.group(1)); mm = int(m.group(2) or 0); ap = (m.group(3) or "").lower()
                if ap in ("am","pm"):
                    h = (0 if h == 12 else h) + (12 if ap == "pm" else 0)
                return h*60 + mm
            t1, t2 = _tok_to_minutes(toks[0]), _tok_to_minutes(toks[1])
            a, b = (t1, t2) if t1 <= t2 else (t2, t1)
            sh, sm, eh, em = a//60, a%60, b//60, b%60
            start_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
            end_dt   = now.replace(hour=eh, minute=em, second=0, microsecond=0)

    # start/end 解析（3）單一時間 / 日期時間
    if not (start_dt or end_dt):
        single = _coerce_datetime(s, tz)
        if single:
            start_dt = single

    # end 缺 → 用時長/預設補齊；end <= start → 用時長補齊（不直接跨日）
    dur = _extract_duration_minutes(s) or default_minutes
    dur = max(MIN_DUR, min(MAX_DUR, int(dur)))
    if start_dt and not end_dt:
        end_dt = start_dt + timedelta(minutes=dur)
    if start_dt and end_dt and end_dt <= start_dt:
        end_dt = start_dt + timedelta(minutes=dur)

    # 只給時間或含 today/今天，且已過 → +1 天
    if start_dt:
        # 「9-10」不再被視為日期，因此會觸發順延；today/今天 一律受保護
        if (not has_explicit_date(s) or re.search(r"(?:\b(today)\b|今天)", s, re.I)):
            if start_dt < now:
                start_dt = start_dt + timedelta(days=1)
                if end_dt: end_dt = end_dt + timedelta(days=1)
                flags.append("rolled_to_next_day")

    # 統一去秒/微秒（log 更乾淨）
    if start_dt:
        start_dt = start_dt.replace(second=0, microsecond=0)
    if end_dt:
        end_dt = end_dt.replace(second=0, microsecond=0)

    # title（避開時間/地點殘影）
    # 先把顯式欄位移除再 tidy
    scrub = re.sub(r"(?:\battendees?\b|受邀|來賓)\s*[:：][^\n]+", "", s, flags=re.I)
    scrub = re.sub(r"(?:\blocation\b|地點)\s*[:：][^\n,;]+", "", scrub, flags=re.I)
    scrub = re.sub(r"\b(body|description)\s*[:：][^\n]+", "", scrub, flags=re.I)
    # 同理：清掉 start: 的時候也要在下一個 end/分隔符/行尾前停，避免把後面的 Title 一起吃掉
    scrub = re.sub(r"\bstart\s*[:：][^\n]+?(?=\s+\bend\b|[,;，、]|$)", "", scrub, flags=re.I)
    # 僅移除 end: 的時間 token，避免吃掉後面的標題字樣
    scrub = re.sub(r"\bend\s*[:：]\s*[0-2]?\d(?::[0-5]\d)?(?:\s*(?:am|pm))?", "", scrub, flags=re.I)    
    title = tidy_title(scrub, s)

    # 粗略信心值：有明確 start/end 標籤較高；加上 location/attendees 微加分
    confidence = 0.6 + (0.2 if used_labeled else 0.0) + (0.05 if location else 0.0) + (0.05 if attendees else 0.0)
    confidence = max(0.0, min(1.0, confidence))

    return {
        "parse_source": "sdk",
        "title": title,
        "body": body,
        "location": location or "",
        "attendees": attendees,
        "timeZone": tz,
        "start": start_dt.isoformat() if start_dt else None,
        "end":   end_dt.isoformat() if end_dt else None,
        "flags": flags,
        "confidence": confidence,
    }

