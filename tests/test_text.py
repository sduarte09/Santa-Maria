from santamaria import text as t


def test_round1_lowercases_and_drops_punctuation_brackets_and_digit_words():
    assert t.clean_round1("El Río, [foto: EFE] crece 2018 y a3b") .split() == ["el", "río", "crece", "y"]


def test_round2_removes_quotes_and_newlines():
    assert t.clean_round2("«hola»\nmundo…") == "hola mundo"


def test_boilerplate_is_removed_as_whole_words_only():
    out = t.clean_text("Compartir en Facebook. Alguno de los uno ríos tres inundación")
    assert "facebook" not in out and "compartir" not in out
    assert "alguno" in out  # the substring "uno" must not damage real words
    assert "inundación" in out


def test_load_stop_words_combines_sources_without_duplicates(tmp_path):
    f = tmp_path / "s.txt"
    f.write_text("de\nla\n\nque\n", encoding="utf-8")
    words = t.load_stop_words(f, nltk_words=["la", "sobre"])
    assert words == ["de", "la", "que", "sobre", "kilometro", "qué", "call"]


def test_shipped_spanish_stop_word_file(params):
    from conftest import DATA

    words = t.load_stop_words(DATA / "spanish.txt")
    assert "de" in words and "tenido" in words and len(words) > 300


def test_nouns_with_injected_tokenizer_and_tagger():
    tag = lambda tokens: [(w, "NN" if w in {"río", "lluvia"} else "VB") for w in tokens]
    assert t.nouns("el río sube con lluvia", tokenize=str.split, tag=tag) == "río lluvia"
