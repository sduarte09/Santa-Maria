# Santa Maria

[![tests](https://github.com/sduarte09/Santa-Maria/actions/workflows/tests.yml/badge.svg)](https://github.com/sduarte09/Santa-Maria/actions/workflows/tests.yml)

News-based monitoring of 207 water bodies of the Magdalena River Basin (Colombia). Digital news from 42 national and regional newspapers (2016 to June 2020) is searched, downloaded and analysed with natural language processing, and the sentiment and key words of each water body are shown by year in Google Earth Engine apps. Developed for the competition *Buscando el Magdalena* 2020.

> Duarte, S., Corzo Perez, G. A., Santos, G., Solomatine, D. P. (2023). *Application of Natural Language Processing to Identify Extreme Hydrometeorological Events in Digital News Media: Case of the Magdalena River Basin, Colombia.* In Corzo Perez & Solomatine (eds.), Special Publications book series. https://doi.org/10.1002/9781119639268.ch10

## What is in the repository

| Folder | Content |
|---|---|
| `src/santamaria/` | The pipeline as a Python package: search queries, result cleaning, article extraction, text cleaning, topics, sentiment classes, aggregation, export for Earth Engine |
| `tests/` | pytest tests on synthetic data and on the shipped parameter files (run in CI) |
| `data/parameters/` | Rivers, reservoirs, municipalities, key words, newspapers (with the HTML classes used to read each one) and the Spanish stop words |
| `gee/` | The six Earth Engine scripts (unchanged) and a description of the table they read |
| `legacy/python/` | The original four scripts (unchanged) |
| `docs/` | `WORKFLOW.md` (the workflow diagram, step by step, mapped to code), `LEGACY_NOTES.md` (what changed and why), the original diagram |

## Install

```bash
pip install -e ".[test]"          # package and tests
pip install -e ".[search,scrape,nlp]"   # to run the full pipeline: Google API, download, NLTK / gensim
pytest
```

The Spanish sentiment model (`from classifier import SentimentClassifier`, the *senti-py* project) is not on PyPI. Install it from its repository, or pass any function `predict(text) -> float in [0, 1]`.

The parameter files are found relative to the repository (editable install). Elsewhere, set `SANTA_MARIA_PARAMETERS` to a folder with the CSV files.

Google Custom Search credentials are read from `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`. Never commit them.

## Example

```python
import pandas as pd
from santamaria import aggregate, parameters, search, scrape, sentiment, text, topics

params = parameters.load_parameters()
rivers = parameters.merge_duplicate_elements(params.rivers)
river = rivers[rivers["Element"] == "Río Risaralda"].iloc[0]

# 1. search (needs credentials) -- here a stand-in that returns one fake result
papers = parameters.newspapers_for(river["DPTO"], params.newspapers)
fetch = lambda query, start=1, **kw: [{"link": "https://eldiario.com.co/a", "displayLink": "eldiario.com.co",
                                       "snippet": "12 mar. 2018 El río Risaralda..."}] if start == 1 else None
items, n_queries = search.search_element(river["Element"], papers.head(1), ["Inundación"], fetch)

# 2. clean the result list, then (online) fetch_html + extract_text give the article text
articles = scrape.clean_results(items)
articles["text"] = "El río creció y la inundación afectó el acueducto. Compartir en Facebook"

# 3. text, sentiment, topics, aggregation
stop_words = text.load_stop_words(parameters.parameters_dir() / "spanish.txt")
articles["text clean"] = articles["text"].map(text.clean_text)
articles["Sentiment"] = sentiment.score_texts(articles["text clean"], lambda t: 0.25)  # replace with the classifier
row = aggregate.summarize_element(articles, [2018], [], topic_fn=lambda n: topics.top_terms(" ".join(n["text clean"]), stop_words, n_words=3))
table = aggregate.to_gee_table(pd.DataFrame([{"Element": river["Element"], **row}]), [2018])
print(table.T)
```

## What has been tested

The functions above are covered by tests that need no network: query strings, pagination limits and the query budget (with a fake search function), date parsing of Spanish snippets, result cleaning, selection of newspapers by department, text cleaning, sentiment classes, per-period aggregation and the Earth Engine table. The shipped parameter files are checked too (for example, 42 newspapers).

Not run here, because they need external services or models: the Google Custom Search calls, downloading from the newspaper sites (page layouts change, so the HTML classes in `Newspapers.csv` need checking), NLTK noun tagging, gensim LDA, the Spanish sentiment classifier, and the Earth Engine scripts. The package does not reproduce the figures of the chapter on its own, because the news database was not published; see `docs/LEGACY_NOTES.md` for the differences from the original scripts.

## Cite

Use the *Cite this repository* button on GitHub (`CITATION.cff`). A Zenodo release gives the software its own DOI.
