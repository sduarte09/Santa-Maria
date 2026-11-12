# Notes on the original scripts

The original scripts are kept unchanged in `legacy/python/` and `gee/`. This is what was changed when they were turned into the package, and what was found on the way. Results produced by the package can differ slightly from the chapter because of items 5 to 7.

## Fixed in the package

1. **Paths and keys.** Windows paths (`C:/Users/.../La Santa Maria/`) and `API_KEY.csv` in the project folder are replaced by `data/parameters/`, and the environment variables `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`.
2. **Counter file name.** `Download Rivers` reads `counter_rivers.csv` but writes `counte_riversr.csv`, so the saved counter was never read back.
3. **Relative dates.** `timedelta(months=...)` is not valid Python; the bare `except` caught the error and silently dropped those articles as "obsolete pages". Months are now counted as 30 days.
4. **Domain clean-up.** `displayLink.replace('m.', '')` also removes `m.` inside domains such as `elpais.com.co`. Only a leading `m.` is removed now.
5. **Newspapers by department.** A paper was selected with `Extension in DPTO` (substring), so `SANTANDER` papers were also used for `NORTE DE SANTANDER` water bodies and `CAUCA` papers for `VALLE DEL CAUCA`. Department names are now split with the longest name first.
6. **Web boilerplate removal.** The long `.replace(...)` chain removed substrings, so `uno`, `dos`, `tres`, `tag`, `field`, `call`, `foto`, `archivo`, `apto` were also cut out of real words (for example in `alguno`). The same word list is now removed as whole words only. Square-bracket removal (`\[.*?¿\]\%`) never matched the intended text; it is now `\[.*?\]`.
7. **Missing guards.** `container_list` was undefined when `container_list.csv` did not exist, and `elements.index[80:]` hard-coded a resume point.

## Kept, but worth knowing

* **Topics.** The LDA is fitted on one document (all articles of a period joined together), so the "topics" are close to word frequencies. `santamaria.topics.top_terms` does this openly; `lda_terms` reproduces the original and its docstring says what to change.
* **Nouns.** `nltk.pos_tag` uses an English tagger on Spanish tokens.
* **Annual key-word bag.** `bag_words.append(... noticias_gis['Topics '+str(i)] ...)` used a leftover variable `i` (the last month) instead of the year being processed; it is not part of the package.
* **Cached results.** `noticias_gis.loc[...] = local_GIS` assigned a file *path* to the row instead of reading the file.
* **Old library versions.** `DataFrame.append` (pandas 2) and `CountVectorizer.get_feature_names` (scikit-learn 1.2) no longer exist; the package uses `concat` and `get_feature_names_out`.
* **Dates.** Searches use `before:2020-12-31` while the analysis and the app text stop at 1 June 2020.

## Earth Engine scripts (unchanged)

* `gee/Precipitacion.js`: `mipaleta.reverse()` is called inside `showMosaic`, and `reverse()` changes the array in place, so the colour ramp flips every time the slider moves.
* In the click handlers `links` is read from the `Class` property, not from a links column, and `print(...)` calls are left in.
* The assets (`users/santiagoduarte09/lasantamaria/...`) are private to that account; see `gee/README.md`.
