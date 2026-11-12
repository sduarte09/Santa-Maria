import math

import numpy as np
import pandas as pd
import pytest

from santamaria import aggregate as ag
from santamaria import sentiment as se
from santamaria import topics as tp


def test_top_terms_orders_by_frequency_then_alphabet():
    pytest.importorskip("sklearn")
    out = tp.top_terms("río río río lluvia lluvia sequia de la", stop_words=["de", "la"], n_words=2)
    assert out == ["río", "lluvia"]
    assert tp.top_terms("   ") == []
    assert tp.top_terms("de la", stop_words=["de", "la"]) == []


@pytest.mark.parametrize("score,label", [(0.1, "Malo"), (0.3, "Neutro"), (0.45, "Neutro"),
                                         (0.6, "Neutro"), (0.61, "Bueno"), (float("nan"), "No"), (None, "No")])
def test_classify_uses_the_legend_thresholds(score, label):
    assert se.classify(score) == label


def test_score_texts_calls_the_predictor():
    assert se.score_texts(["a", "bb"], lambda t: len(t) / 10) == [0.1, 0.2]


def test_load_classifier_gives_a_clear_error_when_missing():
    try:
        import classifier  # noqa: F401
        pytest.skip("senti-py installed")
    except ImportError:
        with pytest.raises(ImportError, match="senti-py"):
            se.load_classifier()


def _articles():
    return pd.DataFrame({
        "date": pd.to_datetime(["2016-02-10", "2016-02-20", "2017-05-01"]),
        "link": ["l1", "l2", "l3"],
        "Sentiment": [0.2, 0.4, 0.9],
        "text clean": ["a", "b", "c"],
    })


def test_monthly_periods_cover_2016_to_june_2020():
    months = ag.monthly_periods()
    assert len(months) == 54 and str(months[0]) == "2016-01" and str(months[-1]) == "2020-06"
    assert ag.month_label(months[0]) == "2016-1"


def test_summarize_element_counts_and_means():
    row = ag.summarize_element(_articles(), [2016, 2017, 2018], [pd.Period("2016-02"), pd.Period("2016-03")],
                               topic_fn=lambda news: list(news["text clean"]))
    assert row["Total Articles"] == 3
    assert row["Sentiment Overall"] == pytest.approx(0.5)
    assert row["Total Articles 2016"] == 2 and row["Sentiment 2016"] == pytest.approx(0.3)
    assert row["Topics 2016"] == "a, b"
    assert row["Total Articles 2016-2"] == 2
    assert row["Total Articles 2016-3"] == 0 and row["Topics 2016-3"] == ag.NOT_INFO
    assert math.isnan(row["Sentiment 2018"]) and row["Links 2018"] == ag.NOT_INFO
    assert row["Links 2017"] == "l3"


def test_summarize_element_without_articles():
    empty = pd.DataFrame(columns=["date", "link", "Sentiment", "text clean"])
    row = ag.summarize_element(empty, [2016], [pd.Period("2016-01")])
    assert row["Total Articles"] == 0 and row["Total Articles 2016-1"] == 0


def test_to_gee_table_matches_the_earth_engine_property_names():
    row = ag.summarize_element(_articles(), [2016, 2017, 2018], [], topic_fn=lambda n: list(n["text clean"]))
    results = pd.DataFrame([{"Element": "Río Cauca", "Class": "Río", **row}])
    out = ag.to_gee_table(results, [2016, 2017, 2018]).iloc[0]
    assert out["Sent 2016"] == "0.300" and out["Tens 2016"] == "Neutro"
    assert out["Sent 2017"] == "0.900" and out["Tens 2017"] == "Bueno"
    assert out["Sent 2018"] == ag.NOT_INFO and out["Tens 2018"] == "No"
    assert out["Art 2016"] == "2" and out["Top 2018"] == ag.NOT_INFO
