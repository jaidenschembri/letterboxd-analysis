# Letterboxd Movie Ratings Analysis – Project Plan

## 🎯 Objective
Analyze user and movie rating data from the Letterboxd dataset to uncover trends in viewer preferences, genre popularity, and rating behaviors.  
This project demonstrates proficiency in **Python**, **NumPy**, **Pandas**, and **data analysis workflows**.

## 📁 Current Project Structure

letterboxd-analysis/
├── data/ # local CSV files (ignored by git)
├── reports/ # analysis outputs (e.g., EDA summaries)
├── scripts/ # Python scripts for loading, cleaning, analyzing
├── README.md
├── progress.md
├── requirements.txt
├── project_plan.md
└── .gitignore

## 🧱 Setup Summary
- Created clean, reproducible Python environment (`venv`)
- Installed dependencies: `pandas`, `numpy`, `matplotlib`, `seaborn`
- Configured `.gitignore` to exclude data and environment files
- Initialized local Git repo for version control

## 📊 Progress So Far

### **Day 1 – Setup & Data Loading**
- Established folder structure and Git workflow
- Verified data integrity and loading via `load_data.py`
- Resolved a parsing error in `movies.csv`  
  → created a one-time fix script to clean malformed lines

### **Day 2 – Initial Data Exploration**
- Extended `load_data.py` to generate EDA summaries:
  - Shape and column info
  - Missing values and duplicates
- Auto-generated report written to `reports/eda_summary.txt`

## 🔮 Next Steps
| Phase | Task | Description |
|-------|------|-------------|
| 1 | **Data Cleaning** | Standardize columns, handle missing values, and prepare merged dataset |
| 2 | **Exploratory Analysis** | Compute averages, rating distributions, and genre trends |
| 3 | **Visualization** | Use Matplotlib/Seaborn to visualize rating patterns over time and by genre |
| 4 | **Insights & Reporting** | Summarize key findings in a Markdown or PDF report |
| 5 | **Version Control & Publishing** | Push repo to GitHub and write a blog post explaining findings |

## ✅ Current Status
✔️ Environment set up  
✔️ Data successfully loaded and cleaned  
✔️ Basic EDA summary generated  
🕐 Next: Merge datasets and compute per-movie statistics

*Maintained by: [Jaiden]*  
*Last updated: October 2025*
