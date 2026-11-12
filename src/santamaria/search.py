"""Google Custom Search queries for news about a water body."""
from __future__ import annotations

from typing import Callable, Dict, List, NamedTuple, Optional

import pandas as pd

DEFAULT_AFTER, DEFAULT_BEFORE = "2016-01-01", "2020-12-31"
PAGE_SIZE, MAX_RESULTS = 10, 100  # the API returns at most 10 per page; 100 per query is its cap


class SearchLimitReached(RuntimeError):
    """The daily query budget (100 per day free tier, 10 000 paid) has been used up."""


class QueryBudget:
    def __init__(self, limit: int = 9500):
        self.limit, self.used = limit, 0

    def spend(self, n: int = 1) -> None:
        self.used += n
        if self.used > self.limit:
            raise SearchLimitReached(f"{self.used} queries used, limit {self.limit}")


def _plus(text: str) -> str:
    return text.replace(" ", "+")


def element_query(element: str, site: str, after=DEFAULT_AFTER, before=DEFAULT_BEFORE) -> str:
    """Quoted water-body name restricted to one newspaper site and a date window."""
    return f'"{_plus(element)}" site:{site} after:{after} before:{before}'


def topic_query(topic: str, site: str, after=DEFAULT_AFTER, before=DEFAULT_BEFORE) -> str:
    """Keyword restricted to one site; the water body goes in ``exactTerms``."""
    return f"'{_plus(topic)}' site:{site} after:{after} before:{before}"


Fetch = Callable[..., Optional[List[dict]]]  # fetch(query, start=1, **kwargs) -> items or None


def google_fetch(api_key: str, cse_id: str) -> Fetch:
    """A ``fetch`` function backed by the Google Custom Search API."""
    from googleapiclient.discovery import build  # imported here: optional dependency

    service = build("customsearch", "v1", developerKey=api_key)

    def fetch(query, start=1, **kwargs):
        try:
            result = service.cse().list(q=query, cx=cse_id, num=PAGE_SIZE, start=start, **kwargs).execute()
            return result["items"]
        except Exception as error:  # no results come back as a missing "items" key
            print(error)
            return None

    return fetch


def collect_pages(fetch: Fetch, query: str, budget: Optional[QueryBudget] = None,
                  max_results: int = MAX_RESULTS, **kwargs):
    """All result pages of one query, up to ``max_results`` items.

    Stops at the first page that is short (last page) or missing. Returns
    ``(items, queries_used)``.
    """
    items, used, start = [], 0, 1
    while start <= max_results:
        if budget:
            budget.spend()
        page = fetch(query, start=start, **kwargs)
        used += 1
        if not page:
            break
        items.extend(page)
        if len(page) < PAGE_SIZE:
            break
        start += PAGE_SIZE
    return items, used


def search_element(element: str, newspapers: pd.DataFrame, topics: List[str], fetch: Fetch,
                   after=DEFAULT_AFTER, before=DEFAULT_BEFORE, budget: Optional[QueryBudget] = None):
    """Search every newspaper for a water body and every keyword.

    For each newspaper one probe query for the name is made; if it fails or finds nothing
    the keywords are skipped for that paper. Returns ``(items, queries_used)``.
    """
    items, used = [], 0
    for site in newspapers["URL"]:
        probe, n = collect_pages(fetch, element_query(element, site, after, before),
                                 budget, max_results=PAGE_SIZE)
        used += n
        if not probe:
            continue
        for topic in topics:
            found, n = collect_pages(fetch, topic_query(topic, site, after, before), budget,
                                     exactTerms=_plus(element), sort="date")
            used += n
            items.extend(found)
    return items, used
