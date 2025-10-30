# Data Cleaning Report

## Movies
- Removed 427 duplicate movies based on movie_id.
- Dropped 2167 movies missing identifiers or titles.
- Backfilled 530 missing year_released values from release_date.
- Movies cleaned: 283348 rows remaining.

## Ratings
- Removed 6 ratings lacking a movie_id.
- Ratings cleaned: 11078161 rows remaining.

## Users
- Filled 307 blank display names with usernames.
- Users cleaned: 8139 rows remaining.

## Ratings ↔ Movies Merge

- Ratings rows before merge: 11078161
- Ratings rows after merge: 11068098
- Ratings without matching movie_id: 10063
