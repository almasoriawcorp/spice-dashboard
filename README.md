# SPICE Energy Dashboard — MVP

**Solar Power Investment Cooperative of Edmonton** — CMPT 3835 Team 11

## Quick Start

```bash
cd spice-dashboard
streamlit run app.py
```

## Sharing with Classmates (Local Setup Guide)

1. **Get the folder**  
   - Download or copy the project folder. Either keep the data folders next to the dashboard **or** place the files inside `spice-dashboard/data`. The simplest layout is:

```
CMPT_3835_MLWI_II/
  └── spice-dashboard/
       ├── app.py
       ├── data/
       │    ├── bissell/   ← Bissell_Thrift Excel
       │    └── weather/   ← spg (1) (1).csv
       └── README.md
```

> **Alternative:** If you keep `data_annette_dautel/` and `lab2_eda/` one level up (old layout), the app will still find them. The new `spice-dashboard/data/...` folders simply make sharing easier.

2. **Copy datasets into spice-dashboard/data**  
   - If you chose to place the data inside `spice-dashboard/data`, copy the following files:
     - `Bissell_Thrift_118_Ave_01012025-01012026.xlsx` into `spice-dashboard/data/bissell/`
     - `spg (1) (1).csv` into `spice-dashboard/data/weather/`

3. **Open a terminal with Python + pip**  
   - Recommend using **Anaconda Prompt** on Windows (already has `python` on PATH).  
   - `cd` into the dashboard folder. If you cloned/copied the repo outside OneDrive (recommended), the command is:
     ```powershell
     cd "C:\Users\almas\CMPT_3835_MLWI_II\spice-dashboard"
     ```
     > Adjust the path if you keep the project elsewhere (e.g., inside OneDrive).

4. **Install required packages** (one time):
3. **Install required packages** (one time):
   ```bash
   pip install "streamlit>=1.30" plotly openpyxl pandas numpy "altair<5"
   ```
   > The `altair<5` constraint keeps compatibility between Streamlit and Altair.

4. **Run the dashboard**:
   ```bash
   python -m streamlit run app.py
   ```
   Streamlit will show a local URL (e.g., `http://localhost:8501`). Open it in the browser.

5. **Troubleshooting tips**:
   - If `streamlit` isn’t found, ensure you’re in the same terminal session where `python` works and use `python -m streamlit run app.py` (forces the current environment).
   - If you see `ModuleNotFoundError: altair.vegalite.v4`, reinstall Altair with `pip install "altair<5"`.
   - If Streamlit warns about `use_container_width`, it’s informational only; the app still runs.

## Features

1. **Portfolio Overview** — All 4 SPICE projects at a glance, total capacity, key metrics
2. **Bissell Thrift Store** — Deep dive into real solar production data (3 inverters, daily/monthly)
3. **Environmental Impact** — CO₂ avoided, trees equivalent, cars off road, cumulative charts
4. **Financial Analysis** — Electricity savings, 20-year projections with adjustable rate assumptions
5. **Weather & ML Insights** — Weather-solar correlations, cloud cover analysis, ML model summary

## Data Sources

- `Data From Annette Dautel/Bissell_Thrift_118_Ave_01012025-01012026.xlsx` — Real Fronius inverter data
- `Lab2_EDA/spg (1) (1).csv` — Weather + solar generation dataset (4,213 records)

## Requirements

- Python 3.9+
- streamlit, plotly, openpyxl, pandas, numpy
