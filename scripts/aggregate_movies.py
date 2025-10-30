from __future__ import annotations

import ast
from pathlib import Path
from typing import List

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def parse_str_list(value) -> List[str]:
    if pd.isna(value):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            parsed = [chunk.strip() for chunk in value.split(",") if chunk.strip()]
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    return []


def load_ratings_with_movies() -> pd.DataFrame:
    path = PROCESSED_DIR / "ratings_with_movies.csv.gz"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing processed ratings file at {path}. Run scripts/clean_data.py first."
        )
    df = pd.read_csv(path, compression="gzip")
    df["genres"] = df["genres"].apply(parse_str_list)
    return df


def compute_movie_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    aggregated = (
        df.groupby("movie_id")
        .agg(
            movie_title=("movie_title", "first"),
            year_released=("year_released", "first"),
            original_language=("original_language", "first"),
            genres=("genres", "first"),
            runtime=("runtime", "first"),
            tmdb_vote_average=("vote_average", "first"),
            tmdb_vote_count=("vote_count", "first"),
            rating_count=("rating_val", "count"),
            rating_mean=("rating_val", "mean"),
            rating_median=("rating_val", "median"),
            rating_std=("rating_val", "std"),
            rating_min=("rating_val", "min"),
            rating_max=("rating_val", "max"),
            user_count=("user_id", pd.Series.nunique),
        )
        .reset_index()
    )

    # Replace NaN std (single rating) with 0 and enforce numeric types.
    aggregated["rating_std"] = aggregated["rating_std"].fillna(0.0)
    aggregated["rating_count"] = aggregated["rating_count"].astype("Int64")
    aggregated["user_count"] = aggregated["user_count"].astype("Int64")

    numeric_cols = ["rating_mean", "rating_median", "rating_std"]
    aggregated[numeric_cols] = aggregated[numeric_cols].round(3)

    return aggregated


def write_outputs(aggregated: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    out_path = PROCESSED_DIR / "movie_aggregates.csv"
    aggregated.to_csv(out_path, index=False)

    summary_lines = [
        "# Movie Aggregates Summary\n",
        f"- Movies with ratings: {len(aggregated)}\n",
        f"- Median rating count: {aggregated['rating_count'].median():.0f}\n",
        f"- Median user count: {aggregated['user_count'].median():.0f}\n",
        f"- Mean user rating (global): {aggregated['rating_mean'].mean():.2f}\n",
    ]

    top_rated = (
        aggregated[aggregated["rating_count"] >= 100]
        .sort_values(by="rating_mean", ascending=False)
        .head(5)
    )
    if not top_rated.empty:
        summary_lines.append("## Top Rated (≥100 ratings)\n")
        for _, row in top_rated.iterrows():
            title = row["movie_title"]
            avg_rating = row["rating_mean"]
            count = row["rating_count"]
            summary_lines.append(f"- {title}: {avg_rating} average from {count} ratings\n")

    (REPORTS_DIR / "movie_aggregates_summary.md").write_text("\n".join(summary_lines))


def main() -> None:
    df = load_ratings_with_movies()
    aggregated = compute_movie_aggregates(df)
    write_outputs(aggregated)


if __name__ == "__main__":
    main()
