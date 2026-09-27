from __future__ import annotations

import re
from datetime import date
from typing import Optional

MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "october": 10, "oct": 10,
    "november": 11, "nov": 11, "december": 12, "dec": 12,
}

ISO_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
LONG_RE = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:,)?\s+(20\d{2})\b",
    re.I,
)
HISTORICAL_HINT = re.compile(
    r"\b(as of|as-of|between|on april|on may|on june|on july|in april|in may|in june|in july|april 15|may 1|june 20)\b",
    re.I,
)


def parse_iso(value: str | date | None) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def extract_dates_from_text(text: str) -> list[date]:
    found: list[date] = []
    for m in ISO_RE.finditer(text or ""):
        found.append(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
    for m in LONG_RE.finditer(text or ""):
        month = MONTHS[m.group(1).lower().rstrip(".")]
        found.append(date(int(m.group(3)), month, int(m.group(2))))
    # unique preserve order
    out: list[date] = []
    for d in found:
        if d not in out:
            out.append(d)
    return out


def looks_historical(text: str) -> bool:
    return bool(HISTORICAL_HINT.search(text or ""))


def resolve_query_dates(
    question: str,
    valid_as_of: date | None,
    system_as_of: date | None,
) -> tuple[Optional[date], Optional[date], Optional[str]]:
    """Return (valid, system, error). Error if historical language and no date can be parsed."""
    mentioned = extract_dates_from_text(question)
    valid = valid_as_of or (mentioned[0] if mentioned else None)
    system = system_as_of
    if system is None and len(mentioned) >= 2 and "between" not in question.lower():
        system = mentioned[1]
    elif system is None and valid is not None and system_as_of is None:
        # User may send only valid; keep system independent — do not copy unless they asked "what we knew then"
        q = question.lower()
        if "knew" in q or "known" in q or "system time" in q or "as known" in q:
            system = valid
        else:
            system = valid
    if looks_historical(question) and valid is None and not mentioned:
        return None, None, (
            "I couldn't determine the requested date. Please specify a date such as April 15, 2025."
        )
    return valid, system, None
