# Letterboxd Movie Ratings – Progress & Plan
_Last updated: 2025-11-04_

## Objective
Analyze the Letterboxd public dataset to surface trends in viewer preferences, genre performance, and overall rating behavior using a reproducible Python data pipeline.

## Current Workflow
- **Data ingestion & quick EDA** – `scripts/load_data.py` loads the three CSV exports and publishes structural summaries to `reports/eda_summary.txt`.
- **Cleaning & enrichment** – `scripts/clean_data.py` standardizes movie, rating, and user tables; rebuilds a ratings↔movies join; and writes cleaned outputs to `data/processed/` alongside `reports/data_cleaning_report.md`.
- **Per-movie aggregates** – `scripts/aggregate_movies.py` computes rating distribution statistics per title and writes both `data/processed/movie_aggregates.csv` and `reports/movie_aggregates_summary.md`.
- **Genre & distribution analysis** – `scripts/analyze_genres.py` derives cross-genre rollups, exports supporting CSVs, and renders charts at `reports/rating_distribution.png` and `reports/top_genres_average_rating.png`.

## Completed Milestones
| Phase | Status | Highlights | Key Outputs |
| --- | --- | --- | --- |
| Project setup & ingestion | ✅ | Virtualenv, requirements, and repo initialized; raw CSVs validated and loaded; baseline summaries automated. | `venv/`, `requirements.txt`, `scripts/load_data.py`, `reports/eda_summary.txt` |
| Data cleaning | ✅ | Deduplicated movies, harmonized typed columns, clipped invalid ratings, and merged ratings with movie metadata. | `data/processed/movies_clean.csv`, `data/processed/ratings_clean.csv.gz`, `data/processed/ratings_with_movies.csv.gz`, `reports/data_cleaning_report.md` |
| Per-movie aggregates | ✅ | Generated rating stats (count, mean, median, dispersion) plus unique rater totals per film; summarized top performers. | `data/processed/movie_aggregates.csv`, `reports/movie_aggregates_summary.md` |
| Genre & rating distribution | ✅ | Ranked genres by engagement and average rating, produced supporting CSV exports, and rendered first-pass visuals. | `data/processed/genre_stats.csv`, `data/processed/rating_distribution.csv`, `reports/genre_analysis_report.md`, PNG charts |

## Current Insights Snapshot
- Cleaned catalog: 283,348 movies (`reports/data_cleaning_report.md`).
- Ratings coverage: 11,068,098 matched ratings with a global mean score of 5.64 (`reports/movie_aggregates_summary.md`).
- Engagement leaders: Drama (~4.78M ratings) and Comedy (~3.28M ratings); best-performing high-volume genres include War (7.05 average) and History (6.92) (`reports/genre_analysis_report.md`).
- Rating sentiment: 57% of all ratings land between 6–8 stars, confirming a mid-to-high clustering trend (`reports/genre_analysis_report.md`).

## In Flight & Next Up
1. **Visualization polish** – Iterate on layouts, annotations, and color palettes for the existing Matplotlib charts; consider small multiples for temporal or language trends.
2. **Narrative reporting** – Draft a cohesive findings report (Markdown and/or PDF) that stitches together quantitative takeaways with selected visuals.
3. **Extended analyses** – Explore user segmentation (power users vs casual), temporal patterns (release year trends), or compare TMDb vote averages against Letterboxd distributions.
4. **Publication readiness** – Finalize README, document execution steps, and prepare the GitHub repository/blog post rollout.

## Open Questions / Dependencies
- Confirm long-term storage location for processed CSVs (~hundreds of MB) before pushing to remote.
- Determine whether downstream consumers need notebook artifacts or if the script-driven pipeline suffices.
- Align on visual branding requirements (color palette, typography) ahead of presentation drafting.
