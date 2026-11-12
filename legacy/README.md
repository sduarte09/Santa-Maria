# Legacy code

The four Python scripts of the original analysis, unchanged. They need Windows paths, an `API_KEY.csv`, and old versions of pandas and scikit-learn. See `../docs/LEGACY_NOTES.md` for what was changed in the package and why.

| Script | Purpose |
|---|---|
| `La_Santa_Maria_-_Download_Rivers.py` / `..._Download_Reservoirs.py` | Google Custom Search for each river / reservoir |
| `La_Santa_Maria_-_Web_Scrapping.py` | Download and read the articles |
| `La_Santa_Maria_-_Text_Analysis.py` | Cleaning, word clouds, topics, sentiment, GIS table |
