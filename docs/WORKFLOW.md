# Workflow

Translated from `Workflow_Spanish.pdf` (the original diagram is kept next to this file) and mapped to the code.

| Step | In the paper workflow | Code |
|---|---|---|
| 1 | Create a Google Cloud project, enable the Custom Search API, create a search engine and get its ID | `santamaria.config.load_credentials` (env `GOOGLE_API_KEY`, `GOOGLE_CSE_ID`) |
| 2 | List the water bodies and the departments they cross | `data/parameters/Rivers.csv`, `Reservoirs.csv`, `Municipalities.csv` |
| 3 | National and regional newspapers, with the HTML class that holds the article body | `data/parameters/Newspapers.csv`, `santamaria.parameters.newspapers_for` |
| 4 | Search URLs and dates of articles for each water body | `santamaria.search` (`search_element`) |
| 5 | Remove repeated URLs, PDFs and unreadable pages | `santamaria.scrape.clean_results` |
| 6 | Download each page and read the article, trying several `div` classes | `santamaria.scrape.fetch_html`, `selectors_for`, `extract_text` |
| 7 | Clean the text in three rounds (punctuation, case, web boilerplate) | `santamaria.text.clean_text` |
| 8 | Stop words and word cloud | `santamaria.text.load_stop_words`; word clouds are in `legacy/python/` |
| 9 | Tokenize, keep nouns, extract key words of the topics | `santamaria.text.nouns`, `santamaria.topics` |
| 10 | Sentiment of each article | `santamaria.sentiment` (Spanish classifier, score in [0, 1]) |
| 11 | Aggregate per water body: overall, per year, per month | `santamaria.aggregate.summarize_element` |
| 12 | Join with the river / lake / reservoir geometries and load into Google Earth Engine | `santamaria.aggregate.to_gee_table`, scripts in `gee/` |
| 13 | Add ERA5 precipitation and temperature and publish the apps | `gee/Precipitacion.js`, `gee/Temperatura.js` |

Sentiment classes in the maps: negative (*Malo*) below 0.3, positive (*Bueno*) above 0.6, neutral (*Neutro*) in between, *No* when there are no articles.
