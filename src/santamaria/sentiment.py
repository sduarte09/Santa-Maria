"""Sentiment scores and the three classes shown in the maps."""
from __future__ import annotations

import math
from typing import Callable, Iterable, List

NEGATIVE_BELOW, POSITIVE_ABOVE = 0.3, 0.6  # thresholds stated in the map legend
LABELS = {"negative": "Malo", "neutral": "Neutro", "positive": "Bueno", "none": "No"}


def load_classifier() -> Callable[[str], float]:
    """Spanish sentiment model: ``predict(text)`` returns a probability of positive tone in [0, 1].

    The original code uses ``from classifier import SentimentClassifier`` (the ``senti-py``
    project). It is not on PyPI; install it from its repository or pass any ``predict`` callable
    to the functions in this package.
    """
    try:
        from classifier import SentimentClassifier
    except ImportError as error:
        raise ImportError("The Spanish sentiment classifier ('classifier', senti-py) is not "
                          "installed; pass your own predict(text) -> float instead") from error
    return SentimentClassifier().predict


def score_texts(texts: Iterable[str], predict: Callable[[str], float]) -> List[float]:
    return [float(predict(t)) for t in texts]


def classify(score: float, negative_below: float = NEGATIVE_BELOW,
             positive_above: float = POSITIVE_ABOVE) -> str:
    """``Malo`` below 0.3, ``Bueno`` above 0.6, ``Neutro`` in between, ``No`` without a score."""
    if score is None or (isinstance(score, float) and math.isnan(score)):
        return LABELS["none"]
    if score < negative_below:
        return LABELS["negative"]
    if score > positive_above:
        return LABELS["positive"]
    return LABELS["neutral"]
