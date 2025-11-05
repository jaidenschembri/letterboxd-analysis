# Letterboxd Ratings – Findings Report
_Generated: 2025-11-04_

## Executive Summary
The cleaned Letterboxd corpus covers **11.1M user ratings across 283K films**, with sentiment clustering between **6–8 stars (57% of all activity)**. High-engagement genres such as Drama and Comedy dominate volume, yet prestige-weighted categories (War, History, Documentary) sustain higher averages. Rating momentum has accelerated for films released after 2010, peaking in 2019, while non-English titles—especially Korean, French, and Japanese releases—outperform the global mean.

## Methodology Snapshot
- **Data sources**: Letterboxd `movies.csv`, `ratings.csv`, `users.csv`.
- **Processing pipeline**:
  - `scripts/clean_data.py` standardizes identifiers, type-casts numeric columns, and materializes `data/processed/ratings_with_movies.csv.gz`.
  - `scripts/aggregate_movies.py` derives per-film aggregates, saved to `data/processed/movie_aggregates.csv`.
  - `scripts/analyze_genres.py` produces genre, rating-distribution, release-year, and language summaries plus supporting CSV exports.
- **Outputs referenced**: Markdown summaries in `reports/`, CSV tables in `data/processed/`, and visual artifacts noted below.

## Key Findings
### Rating Behavior
- **Mid-to-high clustering**: Ratings of 6–8 stars account for 57% of all submissions, with the single largest bar at **8 stars (19.6%)**.  
  _See_ `reports/rating_distribution.png`.
- **Long tail of extremes**: Only 1.7% and 6.8% of ratings land at 1 and 10 stars respectively, indicating relatively few polarizing reactions.

### Genre Performance
- **Volume leaders**: Drama (~4.78M ratings) and Comedy (~3.28M) dwarf other genres, reflecting their broad catalog presence.  
- **Quality standouts**: Among genres with ≥5K ratings, **War (avg 7.05)**, **History (6.92)**, and **Documentary (6.86)** lead on weighted averages, suggesting strong audience resonance within niche segments.
  _See_ `reports/top_genres_average_rating.png`.

### Temporal Trends
- **Modern era surge**: Release years **2017–2019** capture the highest engagement, peaking in **2019 with 513,577 ratings** and a **6.36** average.  
- **Recent dip & rebound**: 2020–2021 volumes contract (pandemic gap), yet average scores stay above 6.2, hinting at resilient audience sentiment.  
  _See_ `reports/yearly_rating_trends.png` and `data/processed/yearly_rating_trends.csv`.

### Language Insights
- **English dominance, global excellence**: English-language titles generate **~9.05M ratings (avg 6.38)**, but **Korean (avg 7.32)**, **Japanese (7.22)**, and **French (7.06)** films eclipse the global mean while sustaining sizable volume.  
- **Undeclared metadata**: “Unknown” language rows (158K ratings, avg 7.14) suggest catalog gaps worth backfilling.
  _See_ `reports/language_rating_volume.png` and `data/processed/language_stats.csv`.

## Recommended Next Steps
1. **Narrative packaging**: Convert these insights and visuals into presentation-ready slides or a blog post targeted at film analytics enthusiasts.
2. **User segmentation**: Profile high-activity vs casual raters to understand how engagement levels influence scoring patterns.
3. **Cross-platform benchmarking**: Compare Letterboxd averages with TMDb or IMDb to contextualize community bias.
4. **Data quality follow-up**: Investigate “unknown” language entries and low-volume recent years for metadata completion or ingestion issues.
