from __future__ import annotations

import ast
import csv
import gzip
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Tuple
import matplotlib.pyplot as plt  # Optional; skipped if unavailable

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"

def parse_str_list(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    try:
        parsed = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        parsed = [chunk.strip() for chunk in text.split(",") if chunk.strip()]
    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]
    return []


def to_int(value, default: int | None = 0) -> int | None:
    if value is None:
        return default
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def to_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return default
    try:
        return float(text)
    except ValueError:
        return default


def compute_genre_summary(aggregates_path: Path) -> Tuple[List[Dict[str, object]], int]:
    if not aggregates_path.exists():
        raise FileNotFoundError(
            f"Missing movie aggregates at {aggregates_path}. Run scripts/aggregate_movies.py first."
        )

    genre_totals: Dict[str, Dict[str, object]] = {}
    movies_with_genre = set()

    with aggregates_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            movie_id = row.get("movie_id", "")
            rating_count = to_int(row.get("rating_count"), default=0) or 0
            rating_mean = to_float(row.get("rating_mean"), default=0.0)
            genres = parse_str_list(row.get("genres"))

            if genres:
                movies_with_genre.add(movie_id)

            for genre in genres:
                stats = genre_totals.setdefault(
                    genre,
                    {
                        "movie_count": 0,
                        "total_ratings": 0,
                        "weighted_sum": 0.0,
                        "movie_rating_values": [],
                    },
                )
                stats["movie_count"] = int(stats["movie_count"]) + 1
                stats["total_ratings"] = int(stats["total_ratings"]) + rating_count
                stats["weighted_sum"] = float(stats["weighted_sum"]) + (rating_mean * rating_count)
                ratings_list: List[float] = stats["movie_rating_values"]  # type: ignore[assignment]
                ratings_list.append(rating_mean)

    summary: List[Dict[str, object]] = []
    for genre, stats in genre_totals.items():
        total_ratings = int(stats["total_ratings"])
        weighted_sum = float(stats["weighted_sum"])
        ratings_list = stats["movie_rating_values"]  # type: ignore[assignment]
        avg_rating = weighted_sum / total_ratings if total_ratings else 0.0
        median_rating = median(ratings_list) if ratings_list else 0.0

        summary.append(
            {
                "genre": genre,
                "movie_count": int(stats["movie_count"]),
                "total_ratings": total_ratings,
                "avg_rating": round(avg_rating, 3),
                "median_movie_rating": round(median_rating, 3),
            }
        )

    summary.sort(key=lambda item: item["total_ratings"], reverse=True)
    return summary, len(movies_with_genre)


def compute_rating_distribution(ratings_path: Path) -> List[Dict[str, object]]:
    if not ratings_path.exists():
        raise FileNotFoundError(
            f"Missing ratings_with_movies at {ratings_path}. Run scripts/clean_data.py first."
        )

    counts: Counter[int] = Counter()

    with gzip.open(ratings_path, mode="rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rating_val = to_int(row.get("rating_val"), default=None)
            if rating_val is None:
                continue
            counts[rating_val] += 1

    total = sum(counts.values())
    distribution: List[Dict[str, object]] = []
    for rating in sorted(counts):
        count = counts[rating]
        share = count / total if total else 0.0
        distribution.append(
            {
                "rating_val": rating,
                "rating_count": count,
                "share": round(share, 4),
            }
        )
    return distribution


def build_ascii_distribution(rating_distribution: List[Dict[str, object]], width: int = 40) -> List[str]:
    if not rating_distribution:
        return []
    max_count = max(item["rating_count"] for item in rating_distribution)  # type: ignore[arg-type]
    chart_lines = ["```\nRating | Distribution", "------ | ------------"]
    for item in rating_distribution:
        rating = int(item["rating_val"])
        count = int(item["rating_count"])
        share = float(item["share"])
        bar_len = int(round((count / max_count) * width)) if max_count else 0
        bar = "#" * bar_len
        chart_lines.append(f"{rating:>6} | {bar:<{width}} {share * 100:5.2f}% ({count:,})")
    chart_lines.append("```")
    return chart_lines


def render_genre_report(
    genre_stats: List[Dict[str, object]],
    rating_distribution: List[Dict[str, object]],
    movies_with_genre_count: int,
    output_path: Path,
    min_rating_threshold: int = 5000,
) -> None:
    genre_count = len(genre_stats)
    total_movies_listed = sum(item["movie_count"] for item in genre_stats)  # type: ignore[arg-type]

    top_by_volume = [
        item for item in genre_stats if int(item["total_ratings"]) >= min_rating_threshold
    ][:10]
    top_by_rating = sorted(
        (item for item in genre_stats if int(item["total_ratings"]) >= min_rating_threshold),
        key=lambda d: d["avg_rating"],
        reverse=True,
    )[:10]

    lines = ["# Genre Analysis Report\n"]
    lines.append(f"- Genres evaluated: {genre_count}")
    lines.append(f"- Movies with at least one genre: {movies_with_genre_count}")
    lines.append(f"- Genre assignments across all movies: {total_movies_listed}\n")

    lines.append(f"## Top Genres by Rating Volume (≥ {min_rating_threshold:,} ratings)\n")
    if top_by_volume:
        for item in top_by_volume:
            lines.append(
                f"- {item['genre']}: {int(item['total_ratings']):,} ratings across "
                f"{int(item['movie_count'])} movies (avg: {item['avg_rating']})"
            )
    else:
        lines.append("- No genres reached the minimum rating threshold.")
    lines.append("")

    lines.append(f"## Highest Rated Genres (≥ {min_rating_threshold:,} ratings)\n")
    if top_by_rating:
        for item in top_by_rating:
            lines.append(
                f"- {item['genre']}: average {item['avg_rating']} from "
                f"{int(item['total_ratings']):,} ratings (median movie: {item['median_movie_rating']})"
            )
    else:
        lines.append("- No genres reached the minimum rating threshold.")
    lines.append("")

    lines.append("## Rating Distribution (all ratings)\n")
    for item in rating_distribution:
        lines.append(
            f"- {int(item['rating_val'])}: {int(item['rating_count']):,} ratings "
            f"({float(item['share']) * 100:.2f}%)"
        )
    lines.append("")
    lines.extend(build_ascii_distribution(rating_distribution))
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def plot_rating_distribution(rating_distribution: List[Dict[str, object]], output_path: Path) -> None:
    if plt is None or not rating_distribution:
        return
    ratings = [int(item["rating_val"]) for item in rating_distribution]
    counts = [int(item["rating_count"]) for item in rating_distribution]

    plt.figure(figsize=(8, 4.5))
    plt.bar(ratings, counts, color="#3776ab")
    plt.title("Letterboxd Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Number of Ratings")
    plt.xticks(ratings)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_top_genres(
    genre_stats: List[Dict[str, object]],
    output_path: Path,
    min_rating_threshold: int = 20000,
) -> None:
    if plt is None:
        return
    filtered = [
        item for item in genre_stats if int(item["total_ratings"]) >= min_rating_threshold
    ]
    filtered.sort(key=lambda item: item["avg_rating"], reverse=True)
    top_items = filtered[:10]
    if not top_items:
        return

    genres = [item["genre"] for item in top_items]
    avg_ratings = [float(item["avg_rating"]) for item in top_items]

    plt.figure(figsize=(8, 4.5))
    plt.barh(genres[::-1], avg_ratings[::-1], color="#ffb703")
    plt.title(f"Top Genres by Average Rating (≥ {min_rating_threshold:,} ratings)")
    plt.xlabel("Average Rating")
    plt.xlim(0, 10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    aggregates_path = PROCESSED_DIR / "movie_aggregates.csv"
    ratings_path = PROCESSED_DIR / "ratings_with_movies.csv.gz"

    genre_stats, movies_with_genre_count = compute_genre_summary(aggregates_path)
    rating_distribution = compute_rating_distribution(ratings_path)

    REPORTS_DIR.mkdir(exist_ok=True)
    render_genre_report(
        genre_stats,
        rating_distribution,
        movies_with_genre_count,
        REPORTS_DIR / "genre_analysis_report.md",
    )

    plot_rating_distribution(
        rating_distribution,
        REPORTS_DIR / "rating_distribution.png",
    )
    plot_top_genres(
        genre_stats,
        REPORTS_DIR / "top_genres_average_rating.png",
    )

    write_csv(
        PROCESSED_DIR / "genre_stats.csv",
        genre_stats,
        ["genre", "movie_count", "total_ratings", "avg_rating", "median_movie_rating"],
    )
    write_csv(
        PROCESSED_DIR / "rating_distribution.csv",
        rating_distribution,
        ["rating_val", "rating_count", "share"],
    )

    return genre_stats, rating_distribution


if __name__ == "__main__":
    main()
