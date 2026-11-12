import pandas as pd

from santamaria import parameters as p


def test_shipped_parameter_files_load_with_expected_shapes(params):
    assert len(params.newspapers) == 42  # "42 online newspapers" in the README
    assert {"Element", "DPTO"} <= set(params.rivers.columns)
    assert not any(c.startswith("Unnamed") for c in params.newspapers.columns)
    assert params.municipalities.columns[0] == "DPTO"  # BOM removed


def test_merge_duplicate_elements_concatenates_departments():
    table = pd.DataFrame({"Element": ["Río A", "Río B", "Río A"], "DPTO": ["HUILA", "CAUCA", "TOLIMA"]})
    merged = p.merge_duplicate_elements(table)
    assert list(merged["Element"]) == ["Río A", "Río B"]
    assert merged.loc[0, "DPTO"] == "HUILATOLIMA"


def test_rivers_and_reservoirs_merge_to_unique_elements(params):
    for table in (params.rivers, params.reservoirs):
        merged = p.merge_duplicate_elements(table)
        assert merged["Element"].is_unique


def test_split_departments_uses_longest_names_first():
    known = ["SANTANDER", "NORTE DE SANTANDER", "CAUCA", "VALLE DEL CAUCA", "RISARALDA", "TOLIMA"]
    assert p.split_departments("NORTE DE SANTANDERSANTANDER", known) == ["NORTE DE SANTANDER", "SANTANDER"]
    assert p.split_departments("VALLE DEL CAUCAVALLE DEL CAUCA", known) == ["VALLE DEL CAUCA"]
    assert p.split_departments("RISARALDATOLIMATOLIMA", known) == ["RISARALDA", "TOLIMA"]
    assert p.split_departments("", known) == []


def test_newspapers_for_a_river_between_two_departments(params):
    merged = p.merge_duplicate_elements(params.rivers).set_index("Element")
    papers = p.newspapers_for(merged.loc["Río Risaralda", "DPTO"], params.newspapers)
    assert {"EL TIEMPO", "SEMANA"} <= set(papers["Newspaper"])  # national papers always included
    assert "EL DIARIO" in set(papers["Newspaper"])  # RISARALDA
    assert "EL PAÍS" not in set(papers["Newspaper"])  # VALLE DEL CAUCA is not crossed


def test_norte_de_santander_does_not_pull_santander_papers(params):
    papers = p.newspapers_for("NORTE DE SANTANDER", params.newspapers)
    assert "VANGUARDIA LIBERAL" not in set(papers["Newspaper"])  # a SANTANDER paper
    assert "LA OPINIÓN" in set(papers["Newspaper"])


def test_topics_of_drops_empty_cells(params):
    water = p.topics_of(params.keywords, "Water")
    assert water[:2] == ["Sequia", "Inundación"] and len(water) == 17
    assert len(p.topics_of(params.keywords, "City")) == 6
