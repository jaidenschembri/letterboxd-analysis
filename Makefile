SHELL := /bin/bash
PYTHON := venv/bin/python

.PHONY: pipeline visuals clean_data aggregate analyze load_data

pipeline: clean_data aggregate analyze

visuals: analyze

load_data:
	$(PYTHON) scripts/load_data.py

clean_data:
	$(PYTHON) scripts/clean_data.py

aggregate:
	$(PYTHON) scripts/aggregate_movies.py

analyze:
	$(PYTHON) scripts/analyze_genres.py
