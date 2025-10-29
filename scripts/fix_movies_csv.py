import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_FILE = DATA_DIR / "movies.csv"
TEMP_FILE = DATA_DIR / "movies_clean.csv"

print(f"Cleaning {RAW_FILE.name}...")

movies = pd.read_csv(
    RAW_FILE,
    engine="python",
    on_bad_lines="skip",
    encoding="utf-8"
)

movies.drop_duplicates(inplace=True)
movies.reset_index(drop=True, inplace=True)

movies.to_csv(TEMP_FILE, index=False)
print(f"Cleaned file saved as {TEMP_FILE.name}")

print("Rows after cleaning:", len(movies))

