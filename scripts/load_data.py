import pandas as pd 
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

def load_datasets():
    movies = pd.read_csv(DATA_DIR / "movies.csv")
    ratings = pd.read_csv(DATA_DIR / "ratings.csv")
    users = pd.read_csv(DATA_DIR / "users.csv")
    return movies, ratings, users

def summarize_df(df, name):
    summary = [
        f"{name.upper()}",
        f"Shape: {df.shape}",
        f"Columns: {list(df.columns)}",
        f"Missing values:\n{df.isna().sum().to_string()}",
        f"Duplicate rows: {df.duplicated().sum()}",
        "",
    ]
    return "\n".join(summary)

if __name__ == "__main__":
    REPORTS_DIR.mkdir(exist_ok=True)

    movies, ratings, users = load_datasets()

    summaries = [
        summarize_df(movies, "movies"),
        summarize_df(ratings, "ratings"),
        summarize_df(users, "users"),
    ]

    report_text = "\n".join(summaries)

    print(report_text)

    with open(REPORTS_DIR / "eda_summary.txt", "w") as f:
        f.write(report_text)

    print("\n EDA summary written to reports/eda_summary.txt")
