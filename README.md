# 🚦 Urban Mobility & Safety Dashboard

A Streamlit-based interactive dashboard for exploring urban mobility and safety reports across city districts.

![Dashboard Preview](screenshots/screenshot_dashboard.png)

---

## 📁 Project Structure

```
DW_project/
├── app.py                    # Main Streamlit application
├── districts.geojson         # District boundary polygons
├── cleaned_reports.csv       # Cleaned and processed dataset
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── screenshots/
    ├── screenshot_filters.png
    ├── screenshot_kpi.png
    ├── screenshot_map.png
    ├── screenshot_charts.png
    ├── screenshot_district_comparison.png
    ├── screenshot_table.png
    └── screenshot_insights.png
```

---

## 📂 Data

The raw dataset `mobility_reports.xlsx` is not included in this repository due to file size. To run the app, place it in the project root folder alongside `app.py`.

The cleaned output `cleaned_reports.csv` is included and shows the result of the full wrangling pipeline.

---

## ▶️ How to Run

### Requirements

Make sure you have Anaconda installed. Then open **Anaconda Prompt** and install dependencies:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pandas geopandas shapely plotly streamlit openpyxl
```

### Running the App

1. Open **Anaconda Prompt**
2. Navigate to the project folder:
   ```bash
   cd C:\Users\YourName\DW_project
   ```
3. Run the app:
   ```bash
   python -m streamlit run app.py
   ```
4. The dashboard will open automatically in your browser at `http://localhost:8501`

> ⚠️ Do NOT run this from Jupyter Notebook. It must be run from Anaconda Prompt or terminal.

---

## 🔧 What the App Does

### Data Wrangling Pipeline
- Parses `reported_at` and `resolved_at` with mixed timezone handling (`utc=True`)
- Deduplicates by `report_id`, keeping the latest valid entry
- Normalizes `issue_type` (lowercase, strip spaces, merge typo variants)
- Converts `severity` from mixed text/numeric to numeric 1–5 scale
- Cleans `estimated_impact_cost` by removing `$`, commas, and blanks
- Validates and drops rows with out-of-range coordinates (lat/lon)
- Engineers new features: `resolution_days`, `is_unresolved`, `report_week`, `report_month`, `severity_band`
- Assigns each report to a district via spatial join with `districts.geojson`

### Filters (Sidebar)
- Date range on `reported_at`
- Issue type multi-select
- District multi-select
- Unresolved only toggle
- Severity band selector (low / medium / high)

### Dashboard Components
- **KPI Cards**: Total reports, % unresolved, median resolution days, total impact cost
- **Choropleth Map**: Districts colored by report count / unresolved rate / median resolution days
- **Time Series Chart**: Reports grouped by week or month
- **Bar Chart**: Top 10 issue types by frequency
- **District Comparison Chart**: Unresolved rate by district
- **Summary Table**: Per-district stats (reports, unresolved %, resolution days, avg severity)
- **Insight Panel**: 3 auto-computed observations from the filtered data
- **CSV Export**: Download the cleaned filtered dataset

---

## 🤖 AI Tools Used

**Claude (Anthropic)** was used throughout this project as a coding assistant:

- Generated the initial roadmap and step-by-step plan from the task brief
- Suggested the data cleaning approach for each messy column
- Wrote and debugged the full `app.py` Streamlit application
- Fixed multiple errors during development:
  - `TypeError` from mixed tz-aware/tz-naive timestamps → fixed with `utc=True`
  - `KeyError: district_name` → identified real column name as `zone_name`
  - `NameError: null` → caused by Jupyter notebook metadata leaking into `app.py`
  - `streamlit not recognized` → resolved by using `python -m streamlit run`
  - `Python not found` → resolved by switching to Anaconda Prompt

All AI suggestions were reviewed and tested before use. The final code was understood and verified at each step.

---

## ✅ What Worked

- Full data cleaning pipeline ran without errors on all 22,000 rows
- Spatial join correctly assigned districts using `zone_name` from GeoJSON
- All 5 sidebar filters dynamically update every dashboard component
- Choropleth map renders correctly with hover tooltips for all districts
- Insight panel auto-computes meaningful observations from filtered data
- `@st.cache_data` prevents reloading/reprocessing data on every interaction

## ⚠️ What Did Not Work / Limitations

- The notebook (`.ipynb`) could not run Streamlit directly — had to convert to `app.py` and run from terminal
- Some `issue_type` typo variants (e.g. `"unsafe xing"`, `"pot hole near crossing"`) were caught but may not cover all edge cases in real data
- `district_hint` column from the original data was not used — district assignment relies entirely on coordinates via spatial join, which is more accurate
- The last week in the time series shows a drop because it is a partial week (data cutoff mid-week)

---

## 📦 Cleaned Data Export

After running the app, click **"Download filtered CSV"** at the bottom of the dashboard to export the cleaned dataset. The exported file contains all engineered features and the assigned district column.