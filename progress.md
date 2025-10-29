## Day 1 – Project Setup and Initial Data Inspection

**Summary:**
Set up project structure, virtual environment, and Git repository.  
Loaded the three Letterboxd datasets (`movies.csv`, `ratings.csv`, `users.csv`) for initial exploration.

**Issue Encountered:**
While loading `movies.csv`, encountered a `pandas.errors.ParserError: Buffer overflow caught` error during parsing.  
Verified that the first ~70,000 rows loaded correctly; issue was caused by a malformed line later in the file.

**Resolution:**
To fix this quickly and permanently:
- Created a temporary script (`fix_movies_csv.py`)
- Read the file using `pd.read_csv(..., engine="python", on_bad_lines="skip", encoding="utf-8")`
- Dropped duplicates and saved a cleaned version of the dataset
- Replaced the original `movies.csv` with the cleaned file
- Removed the temporary cleaning script after verification

**Outcome:**
- All datasets (`movies.csv`, `ratings.csv`, `users.csv`) now load cleanly with the default Pandas parser
- Environment and project structure confirmed working
- Ready to proceed with exploratory data analysis (EDA)
