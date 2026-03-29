# Data Used Per Dashboard Page

## Abbreviations

| Abbreviation | Full Name | What It Is |
|-------------|-----------|------------|
| **TIER** | Technology Innovation and Emissions Reduction | Alberta's industrial carbon pricing regulation that publishes grid emission factors |
| **EPA** | Environmental Protection Agency | US federal agency; publishes greenhouse gas equivalency calculators (trees, cars) |
| **NRCan** | Natural Resources Canada | Canadian federal department; publishes solar resource maps and photovoltaic potential data |
| **AUC** | Alberta Utilities Commission | Alberta's energy regulator; sets the Regulated Rate Option (RRO) tariff |
| **RRO** | Regulated Rate Option | The default electricity rate for Alberta consumers who haven't chosen a competitive retailer |
| **AESO** | Alberta Electric System Operator | Operates Alberta's wholesale electricity market; publishes real-time and historical pool prices |
| **kWp** | Kilowatt-peak | Maximum power output of a solar system under standard test conditions (1000 W/m², 25°C) |
| **kWh** | Kilowatt-hour | Unit of energy; 1 kWh = running a 1 kW device for 1 hour |
| **MWh** | Megawatt-hour | 1,000 kWh |
| **CO₂e** | Carbon Dioxide Equivalent | Standard unit for measuring greenhouse gas emissions, normalizing different gases to CO₂ impact |
| **t** | Tonne | Metric tonne = 1,000 kg |
| **Micro-gen** | Micro-generation | Alberta regulation allowing small producers (≤5 MW) to sell excess electricity back to the grid |

---

## Quick Summary Table

| Page | From Datasets (Files) | From Published Constants / Institutions | Why |
|------|----------------------|----------------------------------------|-----|
| **1 — Portfolio Overview** | Bissell Excel: `total_system_kwh` (energy, CO₂, savings metrics + area chart) | SPICE project specs — hardcoded from SPICE documentation by Annette Dautel (project cards + capacity bar chart). Alberta emission factor 0.45 t/MWh (Gov. of Alberta TIER). Alberta electricity rate $0.18/kWh (AUC Regulated Rate Option). | Executive summary; Bissell is the only project with measured data |
| **2 — Bissell Deep Dive** | Bissell Excel: `total_system_kwh`, `inverter_1/2/3_kwh`, `inverter_1/2/3_kwh_per_kwp` (all charts + raw table) | None | All performance data lives in the Fronius export — no external constants needed |
| **3 — Environmental Impact** | Bissell Excel: `total_system_kwh` (cumulative CO₂ chart, monthly breakdown) | Alberta emission factor 0.45 t CO₂e/MWh (Gov. of Alberta TIER 2023). Tree absorption 0.022 t/tree/year (US EPA). Car emissions 4.6 t/car/year (US EPA). Edmonton solar yield 1,100 kWh/kWp/year (NRCan). | Need published conversion factors to credibly translate kWh into environmental metrics |
| **4 — Financial Analysis** | Bissell Excel: `total_system_kwh` grouped by month (savings bar chart) | Alberta RRO rate $0.18/kWh default (AUC — Alberta Utilities Commission). Edmonton solar yield 1,100 kWh/kWp/year (NRCan) for 20-year projections. | Investors need dollar values; rate comes from Alberta's regulated tariff |
| **5 — Forecasting & Scenarios** | Bissell Excel: `total_system_kwh` Aug–Nov (decomposition + Holt-Winters forecast). Actual monthly totals Sep/Oct/Nov from Fronius (annual projection). | AESO pool prices Aug–Dec 2025 (aeso.ca). Edmonton monthly irradiance + daylight hours (NRCan). RRO $0.18/kWh (AUC). Micro-gen credit $0.12/kWh (Alberta micro-generation regulation). Alberta emission factor 0.45 (Gov. of Alberta). Edmonton yield 1,100 kWh/kWp/year (NRCan). | Revenue forecasting needs both production history and external pricing/solar context |
| **6 — Weather & ML Insights** | SPG CSV: all 21 columns — 4,213 rows (scatter plot, correlation chart, cloud cover box plot) | Lab 2/4 model results — hardcoded summary of team's own model training (ML table). | Bissell has no weather columns; SPG enables weather-energy analysis from Labs 2–4 |

---

## Page 1: Portfolio Overview

**Data:** Bissell Thrift Store Excel (`Bissell_Thrift_118_Ave_01012025-01012026.xlsx`) + hardcoded SPICE project specs.

- The 4 metric cards (energy, CO₂, savings) are calculated from the `total_system_kwh` column in the Bissell Excel file — this is real measured production data from the Fronius inverter monitoring system.
- The project cards and capacity bar chart use hardcoded project information (names, capacities, locations) from SPICE documentation provided by Annette Dautel.
- The daily production area chart plots `date` vs `total_system_kwh` from the Bissell Excel.

**Why:** This page is an executive summary. The Bissell production data is the only real measured data available, so all live metrics come from it. The other three projects are shown with specs only because their monitoring data wasn't provided to the team.

---

## Page 2: Bissell Thrift Store

**Data:** Bissell Thrift Store Excel only.

- Daily production bar chart + 7-day rolling average: `date` and `total_system_kwh`.
- Per-inverter breakdown (stacked area + individual lines): `inverter_1_kwh`, `inverter_2_kwh`, `inverter_3_kwh`.
- Monthly summary (total + avg daily): `total_system_kwh` grouped by `month_name`.
- Inverter performance box plot: `inverter_1_kwh_per_kwp`, `inverter_2_kwh_per_kwp`, `inverter_3_kwh_per_kwp`.
- Raw data table: all columns above.

**Why:** This page focuses exclusively on the Bissell system's hardware-level performance. All the data needed — daily totals, per-inverter breakdowns, and normalized kWh/kWp values — exists in the Fronius export. No external data is required.

---

## Page 3: Environmental Impact

**Data:** Bissell Excel + Alberta emission factor (0.45 t CO₂e/MWh) + NRCan solar yield (1,100 kWh/kWp/year) + EPA equivalency factors.

- CO₂ avoided: `total_system_kwh` ÷ 1000 × 0.45 (Alberta grid emission factor from Gov. of Alberta TIER program, 2023).
- Equivalent trees: CO₂ tonnes ÷ 0.022 (US EPA estimate: one tree absorbs ~22 kg CO₂/year).
- Cars off road: CO₂ tonnes ÷ 4.6 (US EPA estimate: average car emits 4.6 t CO₂/year).
- Cumulative CO₂ chart: daily `total_system_kwh` converted to daily CO₂ avoided, then cumulatively summed.
- Projected annual impact (all 4 projects): total portfolio capacity (88.62 kWp) × 1,100 kWh/kWp/year (NRCan Edmonton average).

**Why:** Translating kWh into CO₂, trees, and cars requires published conversion factors so the numbers are credible and defensible to funders and policy makers. The Alberta-specific emission factor is used because SPICE operates in Alberta's grid.

---

## Page 4: Financial Analysis

**Data:** Bissell Excel + Alberta Regulated Rate Option ($0.18/kWh) + NRCan solar yield (1,100 kWh/kWp/year).

- Monthly savings: `total_system_kwh` grouped by month × user-selected electricity rate.
- 20-year Bissell projection: 30 kWp × 1,100 kWh/kWp/year × rate, compounded by user-selected annual escalation %.
- 20-year portfolio projection: 88.62 kWp × 1,100 kWh/kWp/year × rate, compounded similarly.

**Why:** Investors and community partners need to see dollar values. The $0.18/kWh default is Alberta's Regulated Rate Option — the most common benchmark. The sliders let users test sensitivity to rate and escalation assumptions, making the analysis transparent rather than locked to a single assumption.

---

## Page 5: Forecasting & Scenarios

**Data:** Bissell Excel + AESO wholesale pool prices + NRCan Edmonton irradiance & daylight data + Alberta emission factor.

- Seasonal decomposition: `total_system_kwh` from Aug 20 – Nov 30, decomposed with `statsmodels.seasonal_decompose` (additive, period=7).
- 30-day forecast: Holt-Winters exponential smoothing trained on the same Aug–Nov Bissell data. Confidence intervals from residual standard deviation.
- Revenue scenarios: forecast × three rates — RRO $0.18/kWh, micro-generation credit $0.12/kWh, AESO pool average ~$0.108/kWh.
- AESO prices table: monthly average pool prices Aug–Dec 2025 from aeso.ca.
- Edmonton solar profile chart: monthly irradiance (kWh/m²/day) and daylight hours from NRCan.
- Annual projection: actual monthly totals for Sep/Oct/Nov (Fronius), estimated for Aug (partial data scaled), projected for remaining months using a performance ratio derived from actual data vs theoretical output.
- 20-year portfolio outlook: 88.62 kWp × 1,100 kWh/kWp/year × three pricing scenarios with 3% escalation.

**Why:** Forecasting requires both historical production data (Bissell) and external context (AESO prices, Edmonton solar resource) to model realistic revenue scenarios. The three pricing tiers represent the actual ways solar energy is valued in Alberta — self-consumption savings (RRO), grid export credits (micro-gen), and wholesale market floor (AESO pool).

---

## Page 6: Weather & ML Insights

**Data:** SPG CSV (`spg (1) (1).csv`) — 4,213 rows of hourly weather + solar generation data.

- Scatter plot: any of 8 selectable weather features plotted against `generated_power_kw`.
- Correlation bar chart: Pearson correlation of all 20 numeric features with `generated_power_kw`.
- Cloud cover box plot: `total_cloud_cover_sfc` binned into Clear/Partly Cloudy/Overcast vs `generated_power_kw`.
- ML model summary table: hardcoded results from Lab 2 and Lab 4 model training (Linear Regression, Ridge, Lasso, Random Forest, Gradient Boosting).

**Why:** The Bissell Excel has no weather columns — only production totals. To analyze what weather factors drive solar generation, we need the SPG dataset, which pairs 20 weather features with power output. This was also the dataset used for our Lab 2 EDA, Lab 3 feature engineering, and Lab 4 model training, so this page connects the dashboard directly to our academic work.
