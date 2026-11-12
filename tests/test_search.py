import pandas as pd
import pytest

from santamaria import search as s


def test_queries_match_the_original_strings():
    assert s.element_query("Río Cauca", "eltiempo.com") == \
        '"Río+Cauca" site:eltiempo.com after:2016-01-01 before:2020-12-31'
    assert s.topic_query("El Niño", "semana.com", "2017-01-01", "2018-01-01") == \
        "'El+Niño' site:semana.com after:2017-01-01 before:2018-01-01"


def _pages(*sizes):
    """fetch that returns pages of the given sizes, then None."""
    calls = []
    pages = iter(sizes)

    def fetch(query, start=1, **kwargs):
        calls.append((query, start, kwargs))
        n = next(pages, None)
        return None if n is None else [{"link": f"u{start}-{i}"} for i in range(n)]

    fetch.calls = calls
    return fetch


def test_collect_pages_stops_at_a_short_page():
    fetch = _pages(10, 10, 4)
    items, used = s.collect_pages(fetch, "q")
    assert len(items) == 24 and used == 3
    assert [c[1] for c in fetch.calls] == [1, 11, 21]


def test_collect_pages_is_capped_at_ten_pages():
    fetch = _pages(*([10] * 20))
    items, used = s.collect_pages(fetch, "q")
    assert len(items) == 100 and used == 10 and fetch.calls[-1][1] == 91


def test_collect_pages_passes_extra_arguments_and_handles_errors():
    fetch = _pages()
    items, used = s.collect_pages(fetch, "q", exactTerms="Río+Cauca")
    assert items == [] and used == 1 and fetch.calls[0][2] == {"exactTerms": "Río+Cauca"}


def test_budget_raises_when_exhausted():
    budget = s.QueryBudget(limit=2)
    fetch = _pages(10, 10, 10)
    with pytest.raises(s.SearchLimitReached):
        s.collect_pages(fetch, "q", budget)


def test_search_element_skips_topics_for_papers_without_hits():
    papers = pd.DataFrame({"URL": ["a.com", "b.com"]})
    seen = []

    def fetch(query, start=1, **kwargs):
        seen.append(query)
        if "site:b.com" in query:
            return None  # nothing for this paper
        return [{"link": query + str(start)}] * (3 if "exactTerms" in kwargs else 1)

    items, used = s.search_element("Río Cauca", papers, ["sequia", "peces"], fetch)
    assert len(items) == 6  # two topics x 3 hits on paper a; probe results are not kept
    assert not any("sequia" in q and "b.com" in q for q in seen)
    assert used == 1 + 2 + 1  # probe a, two topic queries, probe b
