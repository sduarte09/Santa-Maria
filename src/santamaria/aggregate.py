"""Per-water-body results by year, month and overall, and the table read by the Earth Engine apps."""
from __future__ import annotations

import math
from typing import Callable, Dict, Iterable, List, Optional

import pandas as pd

from .sentiment import classify

NOT_INFO = "Not Info"


def monthly_periods(start: str = "2016-01", end: str = "2020-06") -> List[pd.Period]:
    """Months from ``start`` to ``end`` inclusive (the news analysis stops in June 2020)."""
    return list(pd.period_range(start, end, freq="M"))


def month_label(period: pd.Period) -> str:
    return f"{period.year}-{period.month}"  # no zero padding, as in the original columns


def _summarize(news: pd.DataFrame, topic_fn: Optional[Callable[[pd.DataFrame], List[str]]]):
    if news.empty:
        return {"articles": 0, "sentiment": float("nan"), "links": NOT_INFO, "topics": []}
    return {
        "articles": int(len(news)),
        "sentiment": float(news["Sentiment"].mean()),
        "links": " \n".join(news["link"]),
        "topics": topic_fn(news) if topic_fn else [],
    }


def summarize_element(articles: pd.DataFrame, years: Iterable[int], months: Iterable[pd.Period],
                      topic_fn: Optional[Callable[[pd.DataFrame], List[str]]] = None) -> Dict[str, object]:
    """One row of results for a water body.

    ``articles`` needs ``date``, ``link`` and ``Sentiment`` (plus ``text clean`` if ``topic_fn``
    uses it). Columns are named ``Sentiment 2018``, ``Topics 2018``, ``Links 2018``,
    ``Total Articles 2018``, the same with ``2018-5`` for months, and ``... Overall``.
    """
    dates = pd.to_datetime(articles["date"]) if len(articles) else pd.Series(dtype="datetime64[ns]")
    row: Dict[str, object] = {}

    def put(label, news, total_name):
        s = _summarize(news, topic_fn)
        row[f"Sentiment {label}" if label else "Sentiment Overall"] = s["sentiment"]
        row[f"Topics {label}" if label else "Topics Overall"] = ", ".join(s["topics"]) or NOT_INFO
        row[f"Links {label}" if label else "Links Overall"] = s["links"]
        row[total_name] = s["articles"]

    put("", articles, "Total Articles")
    for year in years:
        put(str(year), articles[dates.dt.year == year] if len(articles) else articles,
            f"Total Articles {year}")
    for period in months:
        label = month_label(period)
        mask = (dates.dt.year == period.year) & (dates.dt.month == period.month) if len(articles) else None
        put(label, articles[mask] if len(articles) else articles, f"Total Articles {label}")
    return row


def to_gee_table(results: pd.DataFrame, years: Iterable[int]) -> pd.DataFrame:
    """Columns read by the Earth Engine scripts in ``gee/``.

    For each year: ``Sent YYYY`` (score as text), ``Top YYYY`` (key words), ``Art YYYY``
    (article count) and ``Tens YYYY`` (``Malo``, ``Neutro``, ``Bueno`` or ``No``). ``results``
    has one row per water body with ``Element``, optional ``Class`` and the columns made by
    :func:`summarize_element`.
    """
    out = results[[c for c in ("Element", "Class") if c in results.columns]].copy()
    for year in years:
        score = pd.to_numeric(results[f"Sentiment {year}"], errors="coerce")
        out[f"Sent {year}"] = [f"{s:.3f}" if not math.isnan(s) else NOT_INFO for s in score]
        out[f"Top {year}"] = results[f"Topics {year}"].fillna(NOT_INFO).replace("", NOT_INFO)
        out[f"Art {year}"] = results[f"Total Articles {year}"].fillna(0).astype(int).astype(str)
        out[f"Tens {year}"] = [classify(float(s)) for s in score]
    return out
