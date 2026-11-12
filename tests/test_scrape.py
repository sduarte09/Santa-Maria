from datetime import datetime

import pandas as pd
import pytest

from santamaria import scrape as sc


def test_parse_absolute_spanish_dates():
    assert sc.parse_snippet_date("15 ene. 2018 ... el río crece") == datetime(2018, 1, 15)
    assert sc.parse_snippet_date("3 dic 2019 - texto") == datetime(2019, 12, 3)
    assert sc.parse_snippet_date("7 sept. 2017 ...") == datetime(2017, 9, 7)
    assert sc.parse_snippet_date("31 feb. 2018 ...") is None  # impossible date


def test_parse_relative_dates_with_a_fixed_today():
    today = datetime(2020, 6, 1)
    assert sc.parse_snippet_date("Hace 12 días ... texto", today) == datetime(2020, 5, 20)
    assert sc.parse_snippet_date("hace 2 meses ...", today) == datetime(2020, 4, 2)  # month = 30 days
    assert sc.parse_snippet_date("sin fecha", today) is None
    assert sc.parse_snippet_date("", today) is None


def test_normalize_domain_only_strips_a_mobile_prefix():
    assert sc.normalize_domain("m.eltiempo.com") == "eltiempo.com"
    assert sc.normalize_domain("elpais.com.co") == "elpais.com.co"  # the original mangled this


def test_clean_results_drops_pdfs_undated_and_duplicates():
    items = [
        {"link": "https://x.com/a", "displayLink": "m.x.com", "snippet": "1 ene. 2017 ...", "htmlTitle": "t"},
        {"link": "https://x.com/a", "displayLink": "x.com", "snippet": "1 ene. 2017 ..."},
        {"link": "https://x.com/doc.pdf", "displayLink": "x.com", "snippet": "1 ene. 2017 ..."},
        {"link": "https://x.com/b", "displayLink": "x.com", "snippet": "sin fecha"},
        {"link": "https://x.com/c", "displayLink": "x.com", "snippet": "2 mar. 2018 ..."},
    ]
    out = sc.clean_results(items)
    assert list(out["link"]) == ["https://x.com/a", "https://x.com/c"]
    assert out.loc[0, "sourceLink"] == "https://x.com/"
    assert "htmlTitle" not in out.columns
    assert out.loc[1, "date"] == pd.Timestamp("2018-03-02")


def test_clean_results_of_nothing_is_empty():
    assert sc.clean_results([]).empty


def test_selectors_for_newspaper(params):
    assert sc.selectors_for("www.eltiempo.com", params.newspapers)[0] == "articulo-contenido"
    assert len(sc.selectors_for("eltiempo.com", params.newspapers)) == 4
    assert sc.selectors_for("unknown.org", params.newspapers) == []


def test_extract_text_tries_the_classes_in_order():
    pytest.importorskip("bs4")
    html = "<html><body><div class='b'> Segundo </div><div class='c'>Tercero</div></body></html>"
    assert sc.extract_text(html, ["a", "b", "c"]) == "Segundo"
    assert sc.extract_text(html, ["a"]) is None


def test_fetch_html_handles_status_and_errors():
    class R:
        def __init__(self, code):
            self.status_code, self.content = code, b"ok"

    assert sc.fetch_html("u", get=lambda url, timeout: R(200)) == b"ok"
    assert sc.fetch_html("u", get=lambda url, timeout: R(404)) is None

    def boom(url, timeout):
        raise OSError("down")

    assert sc.fetch_html("u", get=boom) is None
