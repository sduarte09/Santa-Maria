"""Text cleaning, stop words and noun extraction for Spanish news."""
from __future__ import annotations

import re
import string
from pathlib import Path
from typing import Callable, Iterable, List, Optional

# Words of the web pages (ad servers, share buttons, layout) that are not article content.
# The original script removed these as substrings, which also damaged real words (for example
# "uno" in "alguno"); here they are removed as whole words.
BOILERPLATE = frozenset("""
adsdisplay call invoke function googletag div push appnexus cdata cx display queue cmd gpt ad
window click passback breakpoints share opens enableservices pubads bannerupduplicadomovil
facebook whatsapp pinterest twitter linkedin telegram skype print themoneytizer compartir
robapagina validateitemultimahora weather widgets sabagh widget location size sizes browser in
new do día top sección value target node text lk out of banner mega slug año tag sense page
short types breakpots nids second channel colors background border url id unit lun vie míe mar
sab dom mobile adsense table dfp seccion slot type ft ee export section block settgs tema
pattern module to contenl args term sobrescrito link posicion sobreescrito adunit field
machinename adid ads pagina blacklist settings targeting contenido foto network sitionuevo
wrapper addservice com cryptocanthon uno dos tres defineslot maicolmedia slider ss parameter
thumbnail json parse apto archivo prototype style width allign nid ids
""".split())

_BRACKETS = re.compile(r"\[.*?\]")
_PUNCT = re.compile("[%s]" % re.escape(string.punctuation))
_WITH_DIGITS = re.compile(r"\w*\d\w*")
_QUOTES = re.compile("[‘’“”…«»]")


def clean_round1(text: str) -> str:
    """Lower case; drop text in square brackets, punctuation and words that contain digits."""
    text = _BRACKETS.sub(" ", text.lower())
    text = _PUNCT.sub(" ", text)
    return _WITH_DIGITS.sub("", text)


def clean_round2(text: str) -> str:
    """Drop typographic quotes and turn line breaks into spaces."""
    return _QUOTES.sub("", text).replace("\n", " ")


def remove_boilerplate(text: str, words: Iterable[str] = BOILERPLATE) -> str:
    drop = set(words)
    return " ".join(w for w in text.split() if w not in drop)


def clean_text(text: str) -> str:
    """The three cleaning rounds applied to one article."""
    return remove_boilerplate(clean_round2(clean_round1(text)))


def load_stop_words(spanish_file, extra: Iterable[str] = ("kilometro", "qué", "call"),
                    nltk_words: Iterable[str] = ()) -> List[str]:
    """Stop words from a text file (one per line) plus NLTK's list and a few extras."""
    words = Path(spanish_file).read_text(encoding="utf-8").splitlines()
    return list(dict.fromkeys([w.strip() for w in words if w.strip()] + list(nltk_words) + list(extra)))


def nouns(text: str, tokenize: Optional[Callable] = None, tag: Optional[Callable] = None) -> str:
    """Keep only the nouns (tag starting with ``NN``).

    NLTK is used by default. Its default tagger is trained on English, so on Spanish text the
    selection is rough; pass a Spanish ``tag`` function (e.g. spaCy) to improve it.
    """
    if tokenize is None or tag is None:
        from nltk import pos_tag, word_tokenize  # optional dependency

        tokenize = tokenize or (lambda t: word_tokenize(t, language="spanish"))
        tag = tag or pos_tag
    return " ".join(word for word, pos in tag(tokenize(text)) if pos[:2] == "NN")
