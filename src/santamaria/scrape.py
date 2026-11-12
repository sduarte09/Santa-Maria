"""Cleaning of search results and extraction of the article text."""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Iterable, List, Optional

import pandas as pd

_MONTHS = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
           "jul": 7, "ago": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dic": 12}
_ABSOLUTE = re.compile(r"^\s*(\d{1,2})\s+([A-Za-zñ]{3,4})\.?\s+(\d{4})")
_RELATIVE = re.compile(r"hace\s+(\d+)\s+(hora|horas|día|días|dia|dias|semana|semanas|mes|meses)", re.I)
_UNIT_DAYS = {"hora": 0, "horas": 0, "día": 1, "días": 1, "dia": 1, "dias": 1,
              "semana": 7, "semanas": 7, "mes": 30, "meses": 30}


def parse_snippet_date(snippet: str, today: Optional[datetime] = None) -> Optional[datetime]:
    """Publication date from the start of a Google snippet.

    Handles ``"15 ene. 2018 ..."`` and relative forms such as ``"Hace 3 días ..."`` (a month is
    counted as 30 days). Returns ``None`` when the snippet has no recognisable date.
    """
    absolute = _ABSOLUTE.match(snippet or "")
    if absolute:
        day, month, year = absolute.groups()
        number = _MONTHS.get(month.lower())
        if number:
            try:
                return datetime(int(year), number, int(day))
            except ValueError:
                return None
    relative = _RELATIVE.search((snippet or "")[:30])
    if relative:
        amount, unit = int(relative.group(1)), relative.group(2).lower()
        return (today or datetime.today()) - timedelta(days=amount * _UNIT_DAYS[unit])
    return None


def normalize_domain(display_link: str) -> str:
    """Domain of a result with the mobile ``m.`` prefix removed (only as a prefix)."""
    return display_link[2:] if display_link.startswith("m.") else display_link


def is_document_link(link: str) -> bool:
    return "pdf" in link.lower()


def clean_results(items: Iterable[dict], today: Optional[datetime] = None) -> pd.DataFrame:
    """Search items -> one row per article link with ``date`` and ``sourceLink``.

    Drops PDFs and items whose date cannot be read, removes the HTML fields and repeated links.
    """
    rows = []
    for item in items:
        item = dict(item)
        for key in ("htmlSnippet", "htmlTitle"):
            item.pop(key, None)
        link = item.get("link", "")
        if not link or is_document_link(link):
            continue
        date = parse_snippet_date(item.get("snippet", ""), today)
        if date is None:
            continue
        item["displayLink"] = normalize_domain(item.get("displayLink", ""))
        item["sourceLink"] = f"https://{item['displayLink']}/"
        item["date"] = pd.Timestamp(date)
        rows.append(item)
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    return frame.sort_values("link").drop_duplicates("link").reset_index(drop=True)


def selectors_for(display_link: str, newspapers: pd.DataFrame) -> List[str]:
    """Candidate CSS classes (``class`` .. ``class4``) of the article container of a newspaper."""
    domain = normalize_domain(display_link).replace("www.", "").replace("sostenibilidad.", "")
    rows = newspapers[newspapers["URL"] == domain]
    if rows.empty:
        return []
    row = rows.iloc[0]
    return [str(row[c]).strip() for c in ("class", "class2", "class3", "class4")
            if c in row and pd.notna(row[c]) and str(row[c]).strip()]


def extract_text(html, classes: Iterable[str]) -> Optional[str]:
    """Text of the first ``<div>`` that matches one of the classes, tried in order."""
    from bs4 import BeautifulSoup  # optional dependency

    soup = BeautifulSoup(html, "lxml") if _has_lxml() else BeautifulSoup(html, "html.parser")
    for cls in classes:
        found = soup.find_all("div", class_=cls)
        if found:
            return found[0].text.strip()
    return None


def _has_lxml() -> bool:
    try:
        import lxml  # noqa: F401
        return True
    except ImportError:
        return False


def fetch_html(url: str, get=None, timeout: float = 30.0) -> Optional[bytes]:
    """Page content, or ``None`` on a network error or a non-200 status."""
    if get is None:
        from requests import get  # optional dependency
    try:
        response = get(url, timeout=timeout)
    except Exception as error:
        print(error)
        return None
    return response.content if response.status_code == 200 else None
