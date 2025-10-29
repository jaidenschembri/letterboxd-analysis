import pandas as pd 
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_datasets():
    movies = pd.read_csv(DATA_DIR / "movies_clean.csv")
    ratings = pd.read_csv(DATA_DIR / "ratings.csv")
    users = pd.read_csv(DATA_DIR / "users.csv")

    return movies, ratings, users

if __name__ == "__main__":
    movies, ratings, users = load_datasets()

    print("Movies shape:", movies.shape)
    print("Ratings shape:", ratings.shape)
    print("Users shape:", users.shape)

    print("\nMovies columns:\n", movies.columns)
    print("\nRatings columns:\n", ratings.columns)
    print("\nUsers columns:\n", users.columns)

    print("\nFirst few rows of Movies:")
    print(movies.head())

    print("\nMissing values summary (Movies):")
    print(movies.isna().sum())
