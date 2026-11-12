"""Key words that describe a set of articles."""
from __future__ import annotations

from typing import Iterable, List


def top_terms(text: str, stop_words: Iterable[str] = (), n_words: int = 10) -> List[str]:
    """Most frequent terms of a text, after removing stop words."""
    from sklearn.feature_extraction.text import CountVectorizer

    stop = list(stop_words)
    if not text.strip():
        return []
    vectorizer = CountVectorizer(stop_words=stop or None)
    try:
        counts = vectorizer.fit_transform([text])
    except ValueError:  # only stop words
        return []
    totals = counts.toarray().ravel()
    terms = vectorizer.get_feature_names_out()
    order = sorted(range(len(terms)), key=lambda i: (-totals[i], terms[i]))
    return [terms[i] for i in order[:n_words]]


def lda_terms(text: str, stop_words: Iterable[str] = (), num_topics: int = 2, passes: int = 10,
              n_words: int = 10) -> List[str]:
    """Top words of the dominant LDA topic of one text (gensim).

    The original analysis fitted the LDA on a single document made of all articles of the
    period; with one document the topics reflect word frequency rather than themes. Fit it on
    one document per article for thematic topics.
    """
    from gensim import matutils, models
    from sklearn.feature_extraction.text import CountVectorizer
    import scipy.sparse

    vectorizer = CountVectorizer(stop_words=list(stop_words) or None)
    counts = vectorizer.fit_transform([text])
    corpus = matutils.Sparse2Corpus(scipy.sparse.csr_matrix(counts.T))
    id2word = {i: t for t, i in vectorizer.vocabulary_.items()}
    lda = models.LdaModel(corpus=corpus, id2word=id2word, num_topics=num_topics, passes=passes)
    best = max(lda[corpus][0], key=lambda pair: pair[1])[0]
    return [word for word, _ in lda.show_topic(best, topn=n_words)]
