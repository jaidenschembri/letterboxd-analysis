"""
Data cleaning utilities for the Letterboxd movie ratings project.

The cleaning pipeline addresses the primary issues surfaced in
reports/eda_summary.txt: missing identifiers, sparse categorical fields,
and inconsistent numeric types across the three core datasets.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
PROCESSED_DIR = DATA_DIR / "processed"


@dataclass
class CleaningReport:
    """Simple container for recording cleaning actions and row counts."""

    name: str
    notes: List[str]

    def add(self, message: str) -> None:
        self.notes.append(message)

    def render(self) -> str:
        header = f"## {self.name}\n"
        lines = "\n".join(f"- {note}" for note in self.notes)
        return f"{header}{lines}\n"


def parse_str_list(value) -> List[str]:
    """Convert serialized list strings into real Python lists."""
    if pd.isna(value):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return []
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            parsed = [chunk.strip() for chunk in value.split(",") if chunk.strip()]
        if isinstance(parsed, list):
            # Filter out falsy entries such as empty strings
            return [str(item).strip() for item in parsed if str(item).strip()]
    return []


def ensure_numeric(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Force columns to numeric dtype in-place."""
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")


def clean_movies(movies: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
    report = CleaningReport("Movies", [])
    df = movies.copy()

    starting_rows = len(df)
    df = df.drop_duplicates(subset="movie_id")
    report.add(
        f"Removed {starting_rows - len(df)} duplicate movies based on movie_id."
    )

    missing_ids = df["movie_id"].isna().sum()
    missing_titles = df["movie_title"].isna().sum()
    if missing_ids or missing_titles:
        df = df.dropna(subset=["movie_id", "movie_title"])
        report.add(
            f"Dropped {missing_ids + missing_titles} movies missing identifiers or titles."
        )

    # Parse list-like columns that are currently serialized strings.
    list_columns = ["genres", "production_countries", "spoken_languages"]
    for column in list_columns:
        df[column] = df[column].apply(parse_str_list)

    df["original_language"] = df["original_language"].fillna("unknown")
    df["overview"] = df["overview"].fillna("")

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    ensure_numeric(df, ["year_released", "runtime", "popularity", "vote_average", "vote_count"])

    # Fill numeric nulls with sensible defaults.
    if df["runtime"].notna().any():
        df["runtime"] = df["runtime"].fillna(df["runtime"].median())
    if df["popularity"].notna().any():
        df["popularity"] = df["popularity"].fillna(df["popularity"].median())
    if df["vote_average"].notna().any():
        df["vote_average"] = df["vote_average"].fillna(df["vote_average"].mean())
    df["vote_count"] = df["vote_count"].fillna(0).astype("Int64")

    # Reconstruct year from parsed release_date when possible.
    missing_year_mask = df["year_released"].isna() & df["release_date"].notna()
    rebuilt_years = missing_year_mask.sum()
    if rebuilt_years:
        df.loc[missing_year_mask, "year_released"] = (
            df.loc[missing_year_mask, "release_date"].dt.year
        )
        report.add(f"Backfilled {rebuilt_years} missing year_released values from release_date.")
    df["year_released"] = df["year_released"].round().astype("Int64")

    report.add(f"Movies cleaned: {len(df)} rows remaining.")
    return df, report


def clean_ratings(ratings: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
    report = CleaningReport("Ratings", [])
    df = ratings.copy()

    missing_movie_ids = df["movie_id"].isna().sum()
    if missing_movie_ids:
        df = df.dropna(subset=["movie_id"])
        report.add(f"Removed {missing_movie_ids} ratings lacking a movie_id.")

    ensure_numeric(df, ["rating_val"])
    invalid_ratings = df["rating_val"].isna().sum()
    if invalid_ratings:
        df = df.dropna(subset=["rating_val"])
        report.add(f"Dropped {invalid_ratings} rows with invalid rating values.")

    df["rating_val"] = df["rating_val"].clip(0, 10).astype("Int64")
    report.add(f"Ratings cleaned: {len(df)} rows remaining.")
    return df, report


def clean_users(users: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
    report = CleaningReport("Users", [])
    df = users.copy()

    missing_names = df["display_name"].isna().sum()
    if missing_names:
        df["display_name"] = df["display_name"].fillna(df["username"])
        report.add(f"Filled {missing_names} blank display names with usernames.")

    ensure_numeric(df, ["num_ratings_pages", "num_reviews"])
    df["num_ratings_pages"] = df["num_ratings_pages"].fillna(0).astype("Int64")
    df["num_reviews"] = df["num_reviews"].fillna(0).astype("Int64")

    report.add(f"Users cleaned: {len(df)} rows remaining.")
    return df, report


def build_ratings_movies(ratings: pd.DataFrame, movies: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    merge_columns = [
        "movie_id",
        "movie_title",
        "year_released",
        "genres",
        "original_language",
        "runtime",
        "vote_average",
        "vote_count",
    ]
    merged = ratings.merge(
        movies[merge_columns],
        on="movie_id",
        how="inner",
        validate="many_to_one",
    )
    stats = {
        "ratings_rows": len(ratings),
        "merged_rows": len(merged),
        "dropped_unmatched": len(ratings) - len(merged),
    }
    return merged, stats


def write_clean_outputs(
    movies: pd.DataFrame,
    ratings: pd.DataFrame,
    users: pd.DataFrame,
    merged: pd.DataFrame,
) -> None:
    PROCESSED_DIR.mkdir(exist_ok=True)
    movies.to_csv(PROCESSED_DIR / "movies_clean.csv", index=False)
    users.to_csv(PROCESSED_DIR / "users_clean.csv", index=False)
    ratings.to_csv(PROCESSED_DIR / "ratings_clean.csv.gz", index=False, compression="gzip")
    merged.to_csv(PROCESSED_DIR / "ratings_with_movies.csv.gz", index=False, compression="gzip")


def save_report(reports: Iterable[CleaningReport], merge_stats: Dict[str, int]) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    lines = ["# Data Cleaning Report\n"]
    for report in reports:
        lines.append(report.render())
    lines.append("## Ratings ↔ Movies Merge\n")
    lines.append(
        f"- Ratings rows before merge: {merge_stats['ratings_rows']}\n"
        f"- Ratings rows after merge: {merge_stats['merged_rows']}\n"
        f"- Ratings without matching movie_id: {merge_stats['dropped_unmatched']}\n"
    )
    (REPORTS_DIR / "data_cleaning_report.md").write_text("\n".join(lines))


def main() -> None:
    movies = pd.read_csv(DATA_DIR / "movies.csv")
    ratings = pd.read_csv(DATA_DIR / "ratings.csv")
    users = pd.read_csv(DATA_DIR / "users.csv")

    movies_clean, movies_report = clean_movies(movies)
    ratings_clean, ratings_report = clean_ratings(ratings)
    users_clean, users_report = clean_users(users)

    merged_ratings, merge_stats = build_ratings_movies(ratings_clean, movies_clean)

    write_clean_outputs(movies_clean, ratings_clean, users_clean, merged_ratings)
    save_report(
        [movies_report, ratings_report, users_report],
        merge_stats,
    )


if __name__ == "__main__":
    main()
