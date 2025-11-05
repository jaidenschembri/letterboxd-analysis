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
PLOT_STYLE = "seaborn-v0_8"
COLOR_RATING = "#20639b"
COLOR_VOLUME = "#86c232"
COLOR_ACCENT = "#f6aa1c"
BACKGROUND_COLOR = "#f7f9fb"


def apply_plot_style() -> None:
    if plt is None:
        return
    try:
        plt.style.use(PLOT_STYLE)
    except OSError:
        # Style may be unavailable (e.g., stripped-down Matplotlib builds).
        pass
    plt.rcParams.update(
        {
            "axes.facecolor": BACKGROUND_COLOR,
            "figure.facecolor": BACKGROUND_COLOR,
            "axes.edgecolor": "#4a4a4a",
            "grid.color": "#d0d7de",
            "grid.linestyle": "--",
            "grid.alpha": 0.6,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "figure.autolayout": True,
        }
    )

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


def compute_yearly_trends(aggregates_path: Path) -> List[Dict[str, object]]:
    if not aggregates_path.exists():
        raise FileNotFoundError(
            f"Missing movie aggregates at {aggregates_path}. Run scripts/aggregate_movies.py first."
        )

    yearly_totals: Dict[int, Dict[str, object]] = {}

    with aggregates_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            year = to_int(row.get("year_released"), default=None)
            rating_count = to_int(row.get("rating_count"), default=0) or 0
            rating_mean = to_float(row.get("rating_mean"), default=0.0)
            if year is None or year < 1900 or year > 2025 or rating_count == 0:
                continue
            stats = yearly_totals.setdefault(
                year,
                {
                    "total_ratings": 0,
                    "weighted_sum": 0.0,
                },
            )
            stats["total_ratings"] = int(stats["total_ratings"]) + rating_count
            stats["weighted_sum"] = float(stats["weighted_sum"]) + (rating_mean * rating_count)

    yearly_stats: List[Dict[str, object]] = []
    for year in sorted(yearly_totals):
        stats = yearly_totals[year]
        total_ratings = int(stats["total_ratings"])
        weighted_sum = float(stats["weighted_sum"])
        avg_rating = weighted_sum / total_ratings if total_ratings else 0.0
        yearly_stats.append(
            {
                "year": year,
                "total_ratings": total_ratings,
                "avg_rating": round(avg_rating, 3),
            }
        )
    return yearly_stats


def compute_language_summary(aggregates_path: Path) -> List[Dict[str, object]]:
    if not aggregates_path.exists():
        raise FileNotFoundError(
            f"Missing movie aggregates at {aggregates_path}. Run scripts/aggregate_movies.py first."
        )

    language_totals: Dict[str, Dict[str, object]] = {}

    with aggregates_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            language = row.get("original_language", "unknown") or "unknown"
            language = language.strip().lower() or "unknown"
            rating_count = to_int(row.get("rating_count"), default=0) or 0
            rating_mean = to_float(row.get("rating_mean"), default=0.0)
            if rating_count == 0:
                continue
            stats = language_totals.setdefault(
                language,
                {
                    "movie_count": 0,
                    "total_ratings": 0,
                    "weighted_sum": 0.0,
                    "rating_values": [],
                },
            )
            stats["movie_count"] = int(stats["movie_count"]) + 1
            stats["total_ratings"] = int(stats["total_ratings"]) + rating_count
            stats["weighted_sum"] = float(stats["weighted_sum"]) + (rating_mean * rating_count)
            ratings_list: List[float] = stats["rating_values"]  # type: ignore[assignment]
            ratings_list.append(rating_mean)

    language_stats: List[Dict[str, object]] = []
    for language, stats in language_totals.items():
        total_ratings = int(stats["total_ratings"])
        weighted_sum = float(stats["weighted_sum"])
        ratings_list = stats["rating_values"]  # type: ignore[assignment]
        avg_rating = weighted_sum / total_ratings if total_ratings else 0.0
        median_rating = median(ratings_list) if ratings_list else 0.0
        language_stats.append(
            {
                "original_language": language or "unknown",
                "movie_count": int(stats["movie_count"]),
                "total_ratings": total_ratings,
                "avg_rating": round(avg_rating, 3),
                "median_movie_rating": round(median_rating, 3),
            }
        )

    language_stats.sort(key=lambda item: item["total_ratings"], reverse=True)
    return language_stats


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
    lines.append(
        "- Visual outputs: `reports/rating_distribution.png`, `reports/top_genres_average_rating.png`, "
        "`reports/yearly_rating_trends.png`, `reports/language_rating_volume.png`"
    )
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
    apply_plot_style()

    ratings = [int(item["rating_val"]) for item in rating_distribution]
    counts = [int(item["rating_count"]) for item in rating_distribution]
    shares = [float(item["share"]) for item in rating_distribution]
    total = sum(counts) or 1

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(ratings, counts, color=COLOR_RATING, edgecolor="#12314c")

    peak_index = counts.index(max(counts))
    peak_rating = ratings[peak_index]
    peak_count = counts[peak_index]
    peak_share = shares[peak_index]

    for bar, share in zip(bars, shares):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{share * 100:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#1f2933",
        )

    ax.set_title("Letterboxd Rating Distribution")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Ratings")
    ax.set_xticks(ratings)
    ax.set_ylim(0, max(counts) * 1.15)
    ax.grid(True, axis="y")

    ax.annotate(
        f"Peak at {peak_rating}\n{peak_share * 100:.1f}% ({peak_count:,})",
        xy=(peak_rating, peak_count),
        xytext=(peak_rating + 0.5, peak_count * 1.05),
        arrowprops=dict(arrowstyle="->", color=COLOR_ACCENT),
        fontsize=10,
        color="#2b2d42",
        ha="left",
    )

    ax.text(
        0.02,
        0.92,
        f"{total:,} total ratings",
        transform=ax.transAxes,
        fontsize=10,
        color="#4a4a4a",
        bbox=dict(facecolor="white", edgecolor="#d0d7de", boxstyle="round,pad=0.2"),
    )

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_top_genres(
    genre_stats: List[Dict[str, object]],
    output_path: Path,
    min_rating_threshold: int = 20000,
) -> None:
    if plt is None:
        return
    apply_plot_style()
    filtered = [
        item for item in genre_stats if int(item["total_ratings"]) >= min_rating_threshold
    ]
    filtered.sort(key=lambda item: item["avg_rating"], reverse=True)
    top_items = filtered[:10]
    if not top_items:
        return

    genres = [item["genre"] for item in top_items]
    avg_ratings = [float(item["avg_rating"]) for item in top_items]
    rating_counts = [int(item["total_ratings"]) for item in top_items]

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    bars = ax.barh(genres[::-1], avg_ratings[::-1], color=COLOR_ACCENT, edgecolor="#915c08")

    for bar, rating, volume in zip(bars, avg_ratings[::-1], rating_counts[::-1]):
        ax.text(
            bar.get_width() + 0.05,
            bar.get_y() + bar.get_height() / 2,
            f"{rating:.2f} ({volume:,})",
            va="center",
            fontsize=9,
            color="#2b2d42",
        )

    ax.set_title(f"Top Genres by Average Rating (≥ {min_rating_threshold:,} ratings)")
    ax.set_xlabel("Average Rating")
    ax.set_xlim(0, 10)
    ax.grid(True, axis="x")

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def rolling_average(values: List[float], window: int) -> List[float]:
    if window <= 1:
        return values
    smoothed: List[float] = []
    for idx in range(len(values)):
        start = max(0, idx - window + 1)
        window_slice = values[start : idx + 1]
        if not window_slice:
            smoothed.append(values[idx])
        else:
            smoothed.append(sum(window_slice) / len(window_slice))
    return smoothed


def plot_yearly_trends(
    yearly_stats: List[Dict[str, object]],
    output_path: Path,
    min_total_ratings: int = 2000,
    rolling_window: int = 5,
) -> None:
    if plt is None or not yearly_stats:
        return
    apply_plot_style()

    filtered = [
        item for item in yearly_stats if int(item["total_ratings"]) >= min_total_ratings
    ]
    if len(filtered) < 3:
        filtered = yearly_stats

    filtered.sort(key=lambda item: item["year"])
    years = [int(item["year"]) for item in filtered]
    volumes = [int(item["total_ratings"]) for item in filtered]
    averages = [float(item["avg_rating"]) for item in filtered]

    smoothed = rolling_average(averages, rolling_window)

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(years, volumes, color=COLOR_VOLUME, alpha=0.6, label="Rating volume")
    ax1.set_xlabel("Release Year")
    ax1.set_ylabel("Total Ratings", color=COLOR_VOLUME)
    ax1.tick_params(axis="y", labelcolor=COLOR_VOLUME)
    ax1.grid(True, axis="y")

    ax2 = ax1.twinx()
    ax2.plot(years, smoothed, color=COLOR_RATING, linewidth=2, label=f"{rolling_window}-year rolling avg")
    ax2.set_ylabel("Average Rating", color=COLOR_RATING)
    ax2.tick_params(axis="y", labelcolor=COLOR_RATING)
    ax2.set_ylim(4.5, 7.5)

    peak_idx = volumes.index(max(volumes))
    ax1.annotate(
        f"Volume peak\n{years[peak_idx]} ({volumes[peak_idx]:,})",
        xy=(years[peak_idx], volumes[peak_idx]),
        xytext=(years[peak_idx], volumes[peak_idx] * 1.1),
        arrowprops=dict(arrowstyle="->", color="#333333"),
        fontsize=10,
        ha="center",
    )

    ax1.set_title("Rating Volume & Average by Release Year")
    fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.92))

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_language_breakdown(
    language_stats: List[Dict[str, object]],
    output_path: Path,
    top_n: int = 10,
    min_total_ratings: int = 20000,
) -> None:
    if plt is None or not language_stats:
        return
    apply_plot_style()

    filtered = [
        item for item in language_stats if int(item["total_ratings"]) >= min_total_ratings
    ][:top_n]
    if not filtered:
        return

    filtered.sort(key=lambda item: item["avg_rating"])
    languages = [item["original_language"].upper() for item in filtered]
    volumes = [int(item["total_ratings"]) for item in filtered]
    averages = [float(item["avg_rating"]) for item in filtered]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(languages, volumes, color="#4cc9f0", edgecolor="#1c658c")
    ax.set_xlabel("Total Ratings")
    ax.set_title(f"Top {len(filtered)} Languages by Rating Volume")
    ax.grid(True, axis="x")

    for bar, avg in zip(bars, averages):
        ax.text(
            bar.get_width() * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"{avg:.2f}",
            va="center",
            fontsize=9,
            color="#2b2d42",
        )

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


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
    yearly_stats = compute_yearly_trends(aggregates_path)
    language_stats = compute_language_summary(aggregates_path)
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
    plot_yearly_trends(
        yearly_stats,
        REPORTS_DIR / "yearly_rating_trends.png",
    )
    plot_language_breakdown(
        language_stats,
        REPORTS_DIR / "language_rating_volume.png",
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
    write_csv(
        PROCESSED_DIR / "yearly_rating_trends.csv",
        yearly_stats,
        ["year", "total_ratings", "avg_rating"],
    )
    write_csv(
        PROCESSED_DIR / "language_stats.csv",
        language_stats,
        ["original_language", "movie_count", "total_ratings", "avg_rating", "median_movie_rating"],
    )

    return genre_stats, rating_distribution


if __name__ == "__main__":
    main()
