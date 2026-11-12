"""Santa Maria: news-based monitoring of water bodies in the Magdalena River Basin.

Pipeline (see ``docs/WORKFLOW.md``): search news for each water body -> clean the result
list and download the article text -> clean the text, score sentiment and extract topics
-> aggregate per water body and period -> publish to the Google Earth Engine apps in ``gee/``.

Everything that does not need the network or a heavy NLP model is plain, tested Python;
Google search, web download, NLTK, gensim and the Spanish sentiment classifier are imported
only when used and can be replaced by any callable.
"""
from . import aggregate, config, parameters, scrape, search, sentiment, text, topics

__version__ = "0.1.0"

__all__ = ["aggregate", "config", "parameters", "scrape", "search", "sentiment", "text",
           "topics", "__version__"]
