# NASA-ADS-data
A collection of tools for processing/analyzing NASA ADS data

Here are a collection of files for performing some analyses on NASA ADS data. _work in progress_

`extract_json.py` contains some methods for extracting relevant fields from the raw data (extracted via `curl`; see [adsabs /
adsabs-dev-api](https://github.com/adsabs/adsabs-dev-api))

`make_model.py` contains code to derive word2vec type embeddings for article references.

`classify_refs.py` contains code (in progress, but functional) for measuring the intersection (via cosine similarity) of the __keywords__ of a test article to its k-nearest neighbors, distance measured by the average of the reference embeddinggs (from `make_model.py`).
