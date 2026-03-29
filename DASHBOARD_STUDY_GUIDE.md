# SPICE Energy Dashboard — Presentation Study Guide

**Course:** CMPT 3835 — Machine Learning in the Workplace II
**Team:** Group 7 / Team 11 — Sandesh Khanal, Farhan ur Rahman, Alma Soria
**Partner Organization:** SPICE (Solar Power Investment Cooperative of Edmonton)
**Key Contact:** Annette Dautel (SPICE business development contractor)

---

## Table of Contents

1. [About SPICE](#1-about-spice)
2. [Data Sources — What We Have and Where It Comes From](#2-data-sources)
3. [Constants & Assumptions Used in the Dashboard](#3-constants--assumptions)
4. [Page 1: Portfolio Overview](#4-page-1-portfolio-overview)
5. [Page 2: Bissell Thrift Store Deep Dive](#5-page-2-bissell-thrift-store-deep-dive)
6. [Page 3: Environmental Impact](#6-page-3-environmental-impact)
7. [Page 4: Financial Analysis](#7-page-4-financial-analysis)
8. [Page 5: Forecasting & Scenarios](#8-page-5-forecasting--scenarios)
9. [Page 6: Weather & ML Insights](#9-page-6-weather--ml-insights)
10. [Connection to Lab Work (Labs 2, 3, 4)](#10-connection-to-lab-work)
11. [Potential Questions & Answers](#11-potential-questions--answers)

---

## 1. About SPICE

SPICE is a **community-owned renewable energy investment cooperative** based in Edmonton, Alberta, founded in 2015. It has approximately 100 members and is run by a volunteer board plus one part-time paid contractor (Annette Dautel).

**How SPICE works:** Members invest money into the cooperative. SPICE uses those pooled funds to install solar panel systems on community buildings in Edmonton. The buildings benefit from reduced electricity costs, and SPICE earns revenue from the energy produced, which flows back to members as returns on investment.

**Four completed solar projects:**

| Project | Capacity | Location | Completed | Building Type |
|---------|----------|----------|-----------|---------------|
| Bissell Thrift Store | 30.0 kWp | 118 Avenue, Edmonton | 2023 | Community Thrift Store |
| Newo Yotina Land Trust | 17.4 kWp | Northeast Edmonton | October 2024 | Community Garden & Education |
| Idylwylde Community League | 16.0 kWp | Central Edmonton | November 2024 | Community League |
| St. Augustine's Anglican Church | 25.22 kWp | Near Capilano Mall, Edmonton | 2024 | Place of Worship |

**Total installed capacity:** 88.62 kWp across all four projects.

**What is kWp?** Kilowatt-peak — the maximum power output of a solar system under ideal conditions (standard test conditions: 1000 W/m² irradiance, 25°C cell temperature). It is the standard unit for comparing solar panel system sizes.

---

## 2. Data Sources

The dashboard uses **two distinct datasets** plus **hardcoded reference data**. It is critical to understand which data feeds each part of the dashboard.

### 2.1 Bissell Thrift Store Production Data (Primary Dataset)

- **File:** `data/bissell/Bissell_Thrift_118_Ave_01012025-01012026.xlsx`
- **Source:** Fronius Solar.web monitoring system — the online portal for Fronius inverters. Annette Dautel exported this data and provided it to the team.
- **Original location:** `Data From Annette Dautel/` folder (provided directly by SPICE)
- **What it contains:** Daily solar energy production from the Bissell Thrift Store rooftop system.
- **Date range:** August 20, 2025 to approximately December 15, 2025 (roughly 110–135 daily observations depending on how you count partial days)
- **Granularity:** One row per day
- **Date format in the file:** `dd.MM.yyyy` (European format, e.g., `20.08.2025`)

**Columns (after renaming in the dashboard code):**

| Column Name | What It Measures | Unit |
|-------------|-----------------|------|
| `date` | Calendar date of the observation | Date |
| `inverter_1_kwh` | Energy produced by Inverter 1 that day | kWh |
| `inverter_2_kwh` | Energy produced by Inverter 2 that day | kWh |
| `inverter_3_kwh` | Energy produced by Inverter 3 that day | kWh |
| `inverter_1_kwh_per_kwp` | Inverter 1 output normalized by its rated capacity | kWh/kWp |
| `inverter_2_kwh_per_kwp` | Inverter 2 output normalized by its rated capacity | kWh/kWp |
| `inverter_3_kwh_per_kwp` | Inverter 3 output normalized by its rated capacity | kWh/kWp |
| `total_system_kwh` | Combined energy from all 3 inverters | kWh |

**Hardware details:**
- 3 × Fronius Primo 7.6-1 208-240 inverters
- Total system capacity: 30 kWp
- Each inverter handles approximately 10 kWp of panels

**Key statistics from the data:**
- Total energy produced: approximately 6,236 kWh over the period
- Peak single-day production: approximately 153 kWh (late August)
- Average daily production (producing days only): approximately 60 kWh
- Production declines sharply from August to December due to Edmonton's seasonal solar decline

**Why this data matters:** This is the only dataset with real, measured SPICE production data. Everything else in the dashboard that references actual production comes from this file. The other three SPICE projects do not yet have production data available to the team.

### 2.2 SPG (Solar Power Generation) Weather Dataset

- **File:** `data/weather/spg (1) (1).csv`
- **Source:** A publicly available solar power generation dataset that combines weather observations with solar generation output. This was the dataset assigned for Lab 2 (EDA) and Lab 3 (Feature Engineering).
- **Original location:** `Lab2_EDA/spg (1) (1).csv`
- **What it contains:** 4,213 rows of hourly weather measurements paired with solar power generation.
- **Granularity:** Sub-daily (roughly 10 readings per day)
- **Important note:** This dataset has **no date/time column**. Rows are sequential hourly readings. Day boundaries were identified in Lab 4 using azimuth angle resets.

**Columns (21 features total, all numeric):**

| Column Name | What It Measures | Unit |
|-------------|-----------------|------|
| `temperature_2_m_above_gnd` | Air temperature at 2m height | °C |
| `relative_humidity_2_m_above_gnd` | Relative humidity at 2m | % |
| `mean_sea_level_pressure_MSL` | Atmospheric pressure at sea level | hPa |
| `total_precipitation_sfc` | Total precipitation | mm |
| `snowfall_amount_sfc` | Snowfall amount | mm |
| `total_cloud_cover_sfc` | Total cloud cover | % (0–100) |
| `high_cloud_cover_high_cld_lay` | High-altitude cloud cover | % |
| `medium_cloud_cover_mid_cld_lay` | Medium-altitude cloud cover | % |
| `low_cloud_cover_low_cld_lay` | Low-altitude cloud cover | % |
| `shortwave_radiation_backwards_sfc` | Incoming solar radiation at surface | W/m² |
| `wind_speed_10_m_above_gnd` | Wind speed at 10m height | m/s |
| `wind_direction_10_m_above_gnd` | Wind direction at 10m | degrees |
| `wind_speed_80_m_above_gnd` | Wind speed at 80m height | m/s |
| `wind_direction_80_m_above_gnd` | Wind direction at 80m | degrees |
| `wind_speed_900_mb` | Wind speed at 900 mb pressure level | m/s |
| `wind_direction_900_mb` | Wind direction at 900 mb | degrees |
| `wind_gust_10_m_above_gnd` | Maximum wind gust at 10m | m/s |
| `angle_of_incidence` | Angle at which sunlight hits the panel surface | degrees |
| `zenith` | Sun's zenith angle (0° = directly overhead, 90° = horizon) | degrees |
| `azimuth` | Sun's compass direction (0° = North, 180° = South) | degrees |
| `generated_power_kw` | **TARGET VARIABLE** — solar power generated | kW |

**Key statistics from Lab 2 EDA:**
- Temperature range: -5.35°C to 34.9°C
- Generated power range: 0.000595 kW to 3,056.79 kW
- Cloud cover range: 0% to 100%
- Shortwave radiation range: 0.0 to 952.3 W/m²
- No missing values in the dataset
- No duplicate rows after cleaning

**Why this data matters:** This dataset is used exclusively on Page 6 (Weather & ML Insights). It allows us to analyze the relationship between weather conditions and solar generation — something the Bissell dataset cannot do because it has no weather features. It was also the primary training data for the ML models in Lab 4.

### 2.3 Hardcoded Reference Data (in app.py)

The following values are coded directly into the dashboard. They are not read from files.

**SPICE Project Portfolio (lines 185–222):**
- All four project names, capacities, locations, completion dates, and statuses
- Source: SPICE documentation provided by Annette Dautel (PDFs in `Data From Annette Dautel/` folder)

**AESO Pool Prices (lines 823–826):**
- Monthly average wholesale electricity prices for Aug–Dec 2025
- Source: AESO (Alberta Electric System Operator) public market reporting (aeso.ca)
- Values: Aug $0.075/kWh, Sep $0.085/kWh, Oct $0.105/kWh, Nov $0.130/kWh, Dec $0.145/kWh
- These are approximate monthly averages used for scenario modeling

**Edmonton Solar Profile (lines 851–853):**
- Monthly average solar irradiance (kWh/m²/day) and daylight hours for Edmonton
- Source: Natural Resources Canada (NRCan) — Edmonton solar resource data
- Used to explain seasonal production patterns and project annual output

**Alberta Constants (lines 227–229):**
- Grid emission factor: 0.45 tonnes CO₂e per MWh — Source: Government of Alberta TIER program (2023)
- Electricity rate: $0.18/kWh — approximate Alberta blended residential rate (Regulated Rate Option)

**Revenue Scenario Rates (lines 821–822, 829–833):**
- Regulated Rate Option (RRO): $0.18/kWh — the rate charged to residential consumers who don't choose a retailer
- Micro-generation credit: $0.12/kWh — the rate Alberta utilities typically pay small solar producers for excess generation
- AESO pool average: ~$0.108/kWh — average of the 5-month pool price data above

---

## 3. Constants & Assumptions

These are important to know for the presentation because someone may ask "where did that number come from?"

| Constant | Value | Source | Used For |
|----------|-------|--------|----------|
| Alberta grid emission factor | 0.45 t CO₂e/MWh | Gov. of Alberta TIER, 2023 | CO₂ avoided calculations |
| Tree CO₂ absorption | 0.022 tonnes/year per tree | US EPA estimate | "Equivalent trees planted" metric |
| Average car CO₂ emissions | 4.6 tonnes/year | US EPA estimate | "Cars off road" equivalent |
| Edmonton solar yield | 1,100 kWh/kWp/year | NRCan PV potential for Edmonton | Annual production projections |
| Panel efficiency | ~15% | Standard crystalline silicon | Used in performance ratio calculations |
| Electricity rate escalation | 3%/year (default) | Historical Alberta trend | 20-year financial projections |
| Bissell system capacity | 30 kWp | Fronius/SPICE documentation | Normalizing production data |

**How CO₂ avoided is calculated:**
```
CO₂ avoided (tonnes) = Energy produced (kWh) ÷ 1000 × 0.45
```
This means: for every 1 MWh (1,000 kWh) of solar energy produced, 0.45 tonnes of CO₂ is avoided because that electricity displaces fossil-fuel-generated power from Alberta's grid (which is still heavily reliant on natural gas).

**How financial savings are calculated:**
```
Savings ($) = Energy produced (kWh) × Electricity rate ($/kWh)
```

---

## 4. Page 1: Portfolio Overview

**Purpose:** Give stakeholders a high-level view of SPICE's entire solar portfolio and a quick look at Bissell's live data.

### 4.1 Key Metrics (Top Row — 4 Cards)

| Metric | What It Shows | Data Source | Calculation |
|--------|--------------|-------------|-------------|
| Total Portfolio Capacity | 88.6 kWp | Hardcoded SPICE project data | Sum of all 4 projects: 30 + 17.4 + 16 + 25.22 |
| Energy Generated (Bissell) | ~6,236 kWh | Bissell Excel → `total_system_kwh` column | `df_bissell["total_system_kwh"].sum()` |
| CO₂ Avoided (Bissell) | ~2.81 tonnes | Calculated from Bissell total | 6,236 ÷ 1000 × 0.45 |
| Est. Savings (Bissell) | ~$1,122 CAD | Calculated from Bissell total | 6,236 × $0.18 |

**How to explain:** "These four numbers summarize SPICE's portfolio. The capacity is fixed — it's the size of the installed systems. The other three metrics are calculated from the actual production data we received from Fronius for the Bissell site."

### 4.2 Project Portfolio Cards

Four cards showing each SPICE project. Only Bissell has the "Live Data" badge because it is the only project for which we have production data. The other three are "Info Only" — we know their specs from SPICE's documentation but don't have their Fronius monitoring data.

**How to explain:** "We would love to show live data for all four projects, but only Bissell's monitoring data was shared with us. As SPICE connects the other three sites to their data pipeline, this dashboard could incorporate them."

### 4.3 Installed Capacity Bar Chart

- **Data:** Hardcoded project capacities
- **What it shows:** A comparison of how much solar capacity each project has
- **How to interpret:** Bissell is the largest at 30 kWp. St. Augustine's is second at 25.22 kWp. The chart helps stakeholders see how SPICE's investment is distributed across community buildings.

### 4.4 Bissell Daily Production Area Chart

- **Data:** Bissell Excel → `date` and `total_system_kwh` columns
- **What it shows:** An area chart of daily energy output over the entire data period (Aug 20 – Dec 15, 2025)
- **How to interpret:** The clear downward slope from left to right shows Edmonton's seasonal solar decline. Late August peaks around 120–153 kWh/day. By December, production drops to near zero. This is expected — Edmonton gets only ~7.5 hours of daylight in December vs ~15 hours in August, and the sun is much lower in the sky.

---

## 5. Page 2: Bissell Thrift Store Deep Dive

**Purpose:** Detailed analysis of Bissell's production data for stakeholders who want to understand system performance.

### 5.1 Summary Metrics (Top Row)

| Metric | What It Shows | Calculation |
|--------|--------------|-------------|
| Total Energy | Sum of all kWh produced | `df_bissell["total_system_kwh"].sum()` |
| Peak Day | Best single day of production | Row with max `total_system_kwh` — shows kWh and date |
| Producing Days | Days with meaningful output (>0.5 kWh) | Count of days where `total_system_kwh > 0.5` |
| Avg Daily Output | Average production on days that actually produced | Mean of `total_system_kwh` where value > 0.5 |

**Why >0.5 threshold?** On very cloudy days or in deep winter, the system might register a tiny fraction of a kWh. Filtering at 0.5 gives a more meaningful average of what the system produces when it is actually generating.

### 5.2 Daily Solar Production (Bar Chart + 7-Day Rolling Average)

- **Data:** Bissell Excel → `date` and `total_system_kwh`
- **Yellow bars:** Each bar is one day's total production in kWh
- **Dark dotted line:** 7-day rolling average — smooths out day-to-day weather noise to show the underlying trend
- **How to interpret:** The bars show individual daily variation (big dips = cloudy/rainy days). The rolling average line shows the steady seasonal decline. If someone asks "why the big dip on day X?" — it is almost certainly a cloudy or stormy day.
- **What the rolling average reveals:** The smooth curve shows the true seasonal pattern without weather noise. It starts around 100+ kWh/day in August and trends down to near zero by December.

### 5.3 Per-Inverter Breakdown (Two Tabs)

**Tab 1 — Stacked Area Chart:**
- Shows how each of the 3 inverters (color-coded yellow, orange, green) contributes to the daily total
- All three inverters should produce roughly equal amounts since each handles ~10 kWp
- **How to interpret:** If one color band is consistently thinner than the others, that inverter may have shading issues, panel degradation, or a hardware problem. In a healthy system, all three bands should be approximately equal height.

**Tab 2 — Individual Lines:**
- Same data as separate line traces for easier direct comparison
- **How to interpret:** Lines should track closely together. Any divergence warrants investigation.

### 5.4 Monthly Summary (Dual-Axis Chart)

- **Yellow bars (left Y-axis):** Total kWh produced that entire month
- **Dark line with markers (right Y-axis):** Average daily kWh for that month
- **Data:** Bissell Excel, grouped by month name (August through December)
- **How to interpret:**
  - **August and September** are the highest-producing months (more sun, longer days)
  - **November and December** are very low (short days, low sun angle, more cloud cover)
  - The bars show total volume; the line shows efficiency per day. A month might have high total volume simply because it has more days, so the daily average line gives a fairer comparison.

### 5.5 Inverter Performance Comparison (Box Plot, kWh/kWp)

- **Data:** Bissell Excel → `inverter_X_kwh_per_kwp` columns
- **What kWh/kWp means:** This normalizes output by each inverter's rated capacity. If Inverter 1 is connected to 10 kWp of panels and produces 50 kWh, that's 5.0 kWh/kWp. This makes different-sized inverters comparable.
- **How to read a box plot:**
  - The **box** spans the 25th to 75th percentile (middle 50% of daily values)
  - The **horizontal line inside the box** is the median (50th percentile)
  - The **whiskers** extend to 1.5× the interquartile range
  - **Dots beyond whiskers** are outliers (unusually high or low days)
- **How to interpret:** If all three boxes are at similar heights with similar medians, the inverters are performing equally. If one box is notably lower, that inverter or its connected panels may need inspection.

### 5.6 Raw Data Table (Expandable)

- Shows the actual daily numbers: date, each inverter's kWh, and total system kWh
- **Purpose:** Transparency — lets stakeholders verify the numbers themselves

---

## 6. Page 3: Environmental Impact

**Purpose:** Translate energy production into tangible environmental benefits that funders, policy makers, and the public can understand.

### 6.1 Big Impact Numbers (4 Cards)

| Metric | Calculation | How to Explain |
|--------|-------------|----------------|
| kWh Clean Energy Generated | `df_bissell["total_system_kwh"].sum()` | "This is the total clean electricity Bissell's solar panels produced." |
| Tonnes CO₂ Avoided | kWh ÷ 1000 × 0.45 | "Every kWh of solar displaces fossil fuel electricity. Alberta's grid still uses a lot of natural gas, so each MWh of solar avoids 0.45 tonnes of CO₂." |
| Equivalent Trees Planted | CO₂ tonnes ÷ 0.022 | "One mature tree absorbs about 22 kg (0.022 tonnes) of CO₂ per year. This is how many trees you'd need to plant to achieve the same carbon offset." |
| Cars Off Road (1 year) | CO₂ tonnes ÷ 4.6 | "The average car emits 4.6 tonnes of CO₂ per year. This tells you how many cars' worth of emissions were avoided." |

### 6.2 Cumulative CO₂ Avoided Over Time (Area Chart)

- **Data:** Bissell Excel → daily `total_system_kwh`, converted to daily CO₂ avoided in kg, then cumulatively summed
- **Calculation per day:** `daily_kwh ÷ 1000 × 0.45 × 1000` (converting tonnes to kg for readability)
- **How to interpret:** The line goes up over time as more energy is produced. The slope is steeper in August/September (high production) and nearly flat in December (minimal production). This visually demonstrates the compounding environmental benefit.
- **What it looks like:** A rising curve that starts steep and flattens — perfectly reflects the seasonal solar pattern.

### 6.3 Monthly Environmental Breakdown (Dual-Axis)

- **Green bars (left axis):** CO₂ avoided per month in tonnes
- **Dark line (right axis):** Equivalent trees per month
- **How to interpret:** Mirrors the production pattern exactly. August/September have the most environmental impact. This helps SPICE communicate to funders: "Our summer months deliver the bulk of our carbon offset."

### 6.4 Projected Annual Impact (All 4 Projects)

- **This is an ESTIMATE, not measured data**
- **Calculation:** Total portfolio capacity (88.62 kWp) × Edmonton's average solar yield (1,100 kWh/kWp/year)
- **Projected annual energy:** ~97,482 kWh
- **Projected annual CO₂ avoided:** ~43.9 tonnes
- **How to explain:** "We only have 5 months of data from one project. To estimate the full portfolio's annual impact, we use Natural Resources Canada's published solar yield figure for Edmonton: 1,100 kWh per kWp per year. This is a widely-used industry standard for Edmonton."
- **Important caveat:** Actual results will vary based on each site's roof orientation, tilt angle, shading, and local weather conditions.

---

## 7. Page 4: Financial Analysis

**Purpose:** Show the dollar value of solar production — critical for investors and community partners who want to understand the financial return.

### 7.1 Assumptions Sliders

- **Electricity Rate slider ($0.10–$0.30):** Default $0.18/kWh. This is approximately the Alberta Regulated Rate Option (RRO) blended rate. Users can adjust to see how different rates affect savings.
- **Annual Rate Escalation slider (0–8%):** Default 3%. Electricity prices historically increase. This slider models how savings grow over time as grid electricity gets more expensive but solar output stays the same (free fuel).

### 7.2 Savings Metrics

- **Total Energy Produced:** Sum from Bissell data
- **Electricity Savings:** Energy × selected rate. "If Bissell were buying this electricity from the grid, this is what they would have paid."
- **Avg Monthly Savings:** Total savings ÷ 5 (approximately 5 months of data)

### 7.3 Monthly Savings Bar Chart

- **Data:** Bissell monthly production totals × selected electricity rate
- **How to interpret:** Directly proportional to production. August/September save the most money. December saves almost nothing. This is important for SPICE to communicate to building partners: "Your biggest savings come in summer."

### 7.4 20-Year Savings Projection (Bissell Only)

- **Yellow bars (left axis):** Annual savings each year
- **Green line (right axis):** Cumulative savings over 20 years
- **Calculation:** Estimated annual production (30 kWp × 1,100 kWh/kWp = 33,000 kWh/year) × electricity rate, with the rate increasing by the escalation % each year
- **How to interpret:** The bars get taller each year because electricity prices are assumed to increase. The green cumulative line curves upward. Solar panels typically last 25+ years with minimal degradation, so this projection is conservative.
- **Key insight:** Even though solar production is flat year-to-year, rising electricity prices make solar MORE valuable over time.

### 7.5 Full Portfolio 20-Year Projection

- Same calculation but scaled to all 88.62 kWp
- Shows the total financial value of SPICE's entire solar portfolio over 20 years

---

## 8. Page 5: Forecasting & Scenarios

**Purpose:** Use time series modeling and external data to predict future production and revenue. This is the most analytically complex page and connects directly to Lab 4 work.

### 8.1 External Data Context — Left Panel: AESO Pool Prices

- **What AESO is:** Alberta Electric System Operator — runs Alberta's wholesale electricity market
- **Data shown:** Monthly average pool prices for Aug–Dec 2025 in both $/MWh and $/kWh
- **Source:** AESO public market reporting (aeso.ca)
- **Why it matters:** Pool prices set the market context for solar revenue. SPICE's actual revenue depends on their specific contract (PPA or micro-generation credit), but pool prices represent the wholesale market floor.

### 8.2 External Data Context — Right Panel: Edmonton Seasonal Solar Profile

- **Yellow bars:** Average daily solar irradiance per month (kWh/m²/day) — how much solar energy hits a square meter of surface each day
- **Dark line:** Average daylight hours per month
- **Orange shading:** Highlights Aug–Dec, the period covered by Bissell data
- **Source:** Natural Resources Canada (NRCan) — Edmonton solar resource data
- **How to interpret:** Edmonton gets peak solar in June (5.8 kWh/m²/day, 17 hours daylight) and minimum in December (0.9 kWh/m²/day, 7.5 hours daylight). This 6:1 ratio explains why Bissell's production drops so dramatically from summer to winter.
- **Key talking point:** "The Bissell data covers the steepest decline in Edmonton's solar resource. If we had summer data, the numbers would be much higher."

### 8.3 Seasonal Decomposition (4 Subplots)

**Method:** `statsmodels.tsa.seasonal.seasonal_decompose` with additive model and period=7 (weekly cycle)
**Data:** Bissell daily production, Aug 20 – Nov 30, 2025 (active production period only)

| Component | What It Shows | How to Interpret |
|-----------|--------------|------------------|
| **Observed** | Raw daily production (input data) | This is what actually happened each day |
| **Trend** | Underlying long-term direction after removing noise | Shows the clear seasonal decline from ~136 kWh/day (August) to near zero (November). This is driven by Edmonton's decreasing daylight and lower sun angle. |
| **Seasonal (7-day)** | Repeating weekly pattern | Shows a mild 7-day fluctuation (~10–15 kWh amplitude). This likely reflects weekly weather cycles rather than anything about the solar panels themselves. |
| **Residual** | What's left after removing trend and seasonal | Random day-to-day weather variability. Larger residuals = more unpredictable days. The standard deviation of residuals (~20 kWh) quantifies the "weather noise." |

**Metrics below the chart:**
- **Trend Start (Aug):** ~136 kWh/day average (first 7 days of trend)
- **Trend End (Nov):** Near zero kWh/day average (last 7 days of trend)
- **Residual Std:** ~20 kWh — this is the day-to-day weather noise that no seasonal model can predict

### 8.4 30-Day Production Forecast

**Method:** Holt-Winters Exponential Smoothing (Triple Exponential Smoothing)
- **Implementation:** `statsmodels.tsa.holtwinters.ExponentialSmoothing`
- **Parameters:** Damped additive trend + additive 7-day seasonality
- **Training data:** Bissell daily production, Aug 20 – Nov 30, 2025
- **Forecast period:** December 1–30, 2025 (30 days ahead)
- **Why Holt-Winters:** It captures both the downward trend (seasonal decline) and weekly patterns. The damped trend prevents the forecast from going negative unrealistically fast.

**Chart elements:**

| Element | Color/Style | What It Shows |
|---------|------------|---------------|
| Observed (Aug–Nov) | Dark solid line | The actual production data the model was trained on |
| Actual Dec (ground truth) | Green dots | Real December data points — used to validate the forecast |
| Forecast | Orange dashed line | The model's prediction for December |
| 95% Confidence Interval | Light orange shading | 95% probability the actual value falls within this range |
| 80% Confidence Interval | Yellow shading | 80% probability range (narrower) |
| Vertical dotted line | Gray | Marks where the forecast begins (Dec 1) |

**How confidence intervals are calculated:**
- Based on the standard deviation of the model's residuals (prediction errors during training)
- 80% CI: forecast ± 1.28 × residual_std
- 95% CI: forecast ± 1.96 × residual_std
- All lower bounds are clamped to zero (solar can't produce negative energy)

**How to interpret:** If the green dots (actual December values) fall within the shaded confidence bands, the model is performing well. Wide bands = more uncertainty. The forecast is expected to show very low values for December because that's what Edmonton's seasonal pattern dictates.

**Metrics below the chart:**
- **Forecast Total (30 days):** Sum of all 30 forecasted daily values
- **95% CI Low:** Sum if every day hit the low end of the confidence interval
- **95% CI High:** Sum if every day hit the high end

### 8.5 Revenue Scenarios (Two Panels)

Three pricing scenarios are compared. These represent different ways SPICE could monetize their solar output:

| Scenario | Rate | What It Represents |
|----------|------|--------------------|
| **Best Case (RRO $0.18/kWh)** | $0.18/kWh | If the building offsets its own consumption at the full regulated rate — highest value per kWh |
| **Base Case (Micro-gen $0.12/kWh)** | $0.12/kWh | Alberta micro-generation credit — what utilities typically pay small solar producers for excess electricity sent to the grid |
| **Worst Case (AESO Pool ~$0.108/kWh)** | ~$0.108/kWh | Average wholesale pool price — the market floor. This is the lowest price solar energy could be valued at. |

**Left Panel — Horizontal Bar Chart:**
- Each bar shows the expected 30-day revenue for that scenario
- Error bars show the 95% confidence interval range (from the production forecast uncertainty)
- **How to interpret:** The gap between best and worst case shows how important pricing is. Securing a favorable rate (RRO or PPA) has significant financial impact.

**Right Panel — Cumulative Revenue Lines:**
- Shows how revenue accumulates day-by-day over the 30-day forecast period
- Green shading around the best-case line shows the 95% CI
- **How to interpret:** Steeper lines = faster revenue accumulation. The gap between the three lines shows the revenue sensitivity to pricing.

### 8.6 Annual Projection & Portfolio Outlook

**Left Chart — Monthly Production Bar Chart:**
Projects Bissell's output for a full 12 months using Edmonton's seasonal irradiance profile.

- **Green bars:** Months with actual Fronius data (September, October, November) — these are MEASURED values
- **Yellow bar:** August — estimated from partial data (only 12 days of August were in the dataset, scaled to 31 days)
- **Dark bars:** All other months — projected using a performance ratio calculated from the actual months

**Performance ratio calculation:**
```
For each actual month (Sep, Oct, Nov):
  Theoretical output = Irradiance × 30 kWp × days_in_month × 0.15 (panel efficiency)
  Performance ratio = Actual output ÷ Theoretical output
Average performance ratio = mean of the three months' ratios
Projected months = Theoretical output × Average performance ratio
```

**Right Chart — Annual Revenue Scenarios:**
Total annual kWh × each of the three pricing rates, shown as horizontal bars.

### 8.7 20-Year Portfolio Strategic Outlook (Two Panels)

**Left Panel — Cumulative Revenue:**
- Three lines (one per pricing scenario) showing cumulative revenue over 20 years
- Assumes 3% annual electricity price escalation
- Scaled to full portfolio (88.62 kWp × 1,100 kWh/kWp/year)
- **How to interpret:** The upward-curving lines show the compounding effect of rising electricity prices. Best case (green) is significantly higher than worst case (orange).

**Right Panel — Cumulative Environmental Impact:**
- Green bars: Cumulative CO₂ avoided (tonnes) = annual CO₂ × number of years
- Dark line: Equivalent trees planted (cumulative CO₂ ÷ 0.022)
- **How to interpret:** These grow linearly because we assume constant annual production. By year 20, the portfolio would have avoided approximately 877 tonnes of CO₂.

---

## 9. Page 6: Weather & ML Insights

**Purpose:** Explore what weather factors drive solar generation, using the SPG dataset. This page connects to Lab 2 (EDA) and Lab 3 (Feature Engineering) work.

**Important:** This page uses the **SPG dataset**, NOT the Bissell data. The SPG dataset has weather features; Bissell does not.

### 9.1 Dataset Overview

- Shows record count (4,213), number of features (21)
- Three metrics: average generation, max generation, average temperature
- **Data:** SPG CSV

### 9.2 Weather vs Solar Generation (Interactive Scatter Plot)

- **Dropdown selector:** Choose any weather feature to plot against `generated_power_kw`
- **Points colored by:** Generation intensity (dark blue = low, yellow = medium, orange = high)
- **Data:** Random sample of 1,000 rows from SPG (for performance)

**Key features to demo and what they show:**

| Feature | Expected Pattern | Why |
|---------|-----------------|-----|
| `shortwave_radiation_backwards_sfc` | Strong positive trend (up and to the right) | More incoming solar radiation = more power generated. This is the #1 predictor. |
| `zenith` | Strong negative trend | Higher zenith = sun is lower in sky = less direct radiation hitting panels. Zenith 0° = sun directly overhead (best). Zenith 90° = sunrise/sunset (worst). |
| `total_cloud_cover_sfc` | Negative trend, clustered | More clouds = less solar radiation reaching panels = less power |
| `temperature_2_m_above_gnd` | Weak/moderate positive | Warmer days tend to be sunnier, but extremely hot days can actually reduce panel efficiency. The correlation is indirect (through solar radiation). |
| `relative_humidity_2_m_above_gnd` | Weak negative | Higher humidity often correlates with cloud cover |

### 9.3 Feature Correlation Bar Chart

- **Data:** Pearson correlation of every numeric SPG column with `generated_power_kw`
- **Green bars:** Positive correlation (feature increases → power increases)
- **Orange bars:** Negative correlation (feature increases → power decreases)
- **How to interpret:** The longest bars are the most important predictors.

**Expected strongest correlations (from Lab 2 findings):**
- **Strongest positive:** `shortwave_radiation_backwards_sfc` — solar radiation is the primary driver
- **Strong negative:** `zenith` — higher sun angle means less power
- **Moderate positive:** `angle_of_incidence` — affects how directly sunlight hits panels
- **Negative:** Cloud cover variables reduce power output
- **Weak:** Wind speed, humidity, pressure — minor effects

### 9.4 Solar Generation by Cloud Cover (Box Plot)

- **Data:** SPG dataset, with cloud cover binned into three categories:
  - Clear (0–30% cloud cover)
  - Partly Cloudy (30–70%)
  - Overcast (70–100%)
- **How to interpret:**
  - **Clear skies:** Highest median, widest range (high output but variable)
  - **Partly Cloudy:** Medium output
  - **Overcast:** Compressed near zero — clouds dramatically reduce generation
- **Key insight:** This visually proves that cloud cover is one of the most important factors in solar production.

### 9.5 ML Model Performance Summary (Table)

- **Data:** Hardcoded summary from Lab 2/Lab 4 model training results
- Shows 5 models tested: Linear Regression, Ridge, Lasso, Random Forest, Gradient Boosting

| Model | Type | Best For |
|-------|------|----------|
| Linear Regression | Baseline linear | Interpretability — simple, easy to explain |
| Ridge | L2 regularized linear | Handling multicollinearity (correlated features) |
| Lasso | L1 regularized linear | Feature selection (drives unimportant features to zero) |
| Random Forest | Ensemble of 300 decision trees | Capturing non-linear patterns |
| Gradient Boosting | Sequential boosted trees | Best overall accuracy |

**Key insight displayed:** "Shortwave radiation, zenith angle, and cloud cover are the strongest predictors. Tree-based models outperform linear models because the weather-energy relationship is non-linear."

---

## 10. Connection to Lab Work

### Lab 2: EDA (Exploratory Data Analysis)
- **What we did:** Loaded SPG dataset (4,213 rows), cleaned column names, checked for duplicates and missing values, generated descriptive statistics, created visualizations (histograms, box plots, scatter plots, correlation heatmap), identified key feature relationships.
- **Also did EDA on Bissell data:** Loaded the Excel file, renamed columns, parsed dates, analyzed production patterns, created time series plots, monthly aggregations, per-inverter comparisons.
- **Key findings that feed into the dashboard:**
  - Shortwave radiation is the strongest predictor of solar power
  - Cloud cover significantly reduces generation
  - Zenith angle is crucial (sun position matters)
  - Temperature has moderate positive correlation (indirect — warmer = sunnier)
  - Bissell production shows clear seasonal decline Aug → Dec

### Lab 3: Feature Engineering
- Created categorical features (cloud_level: Low/Medium/High; power_category: Low/Medium/High/Very High)
- Engineered interaction features and polynomial features
- Applied feature selection techniques
- These engineered features informed the dashboard's cloud cover analysis on Page 6

### Lab 4: Modeling & Optimization
- **Feature engineering for time series:** Aggregated SPG hourly data to daily, tested stationarity (ADF test), applied Box-Cox transformation, performed seasonal decomposition, ran ACF/PACF analysis, created lag features (1, 2, 3, 7 days), rolling window features (3, 7, 14 days), difference features.
- **Four models trained:**
  1. ARIMA — statistical, multiple (p,d,q) orders tested, best selected by AIC
  2. SARIMA — adds seasonal component (period=7 for weekly patterns)
  3. Random Forest — 200 trees, TimeSeriesSplit CV with 5 folds
  4. XGBoost/GradientBoosting — 200 estimators, sequential error correction
- **Evaluation metrics:** MAE, RMSE, MAPE, R² — all calculated on chronological test set (80/20 split)
- **Cross-validation:** TimeSeriesSplit (not random shuffle) to prevent data leakage
- **Also validated on Bissell data:** Applied ARIMA/SARIMA directly to the Bissell time series as independent validation

**Connection to dashboard forecasting page:** The dashboard's Holt-Winters forecast (Page 5) uses the same seasonal decomposition concepts from Lab 4 but is specifically tuned for the Bissell production data and focused on business-relevant 30-day predictions with confidence intervals and revenue scenarios.

---

## 11. Potential Questions & Answers

**Q: Why do you only have data from one project?**
A: Annette provided us with the Fronius monitoring data for Bissell Thrift Store. The other three projects are newer (completed late 2024) and their monitoring data wasn't available to us during this project. The dashboard is designed to easily incorporate additional project data as it becomes available.

**Q: Where does the weather data come from? Is it Edmonton-specific?**
A: The SPG dataset was assigned for our lab work and contains weather + solar generation data. It is a general solar power generation dataset, not specific to the Bissell site. We use it to understand the general relationship between weather conditions and solar output. The Edmonton-specific seasonal solar profile (irradiance, daylight hours) comes from Natural Resources Canada.

**Q: How accurate is the forecast?**
A: The Holt-Winters model captures the seasonal trend well. We provide 80% and 95% confidence intervals so stakeholders can see the range of uncertainty. The model's residual standard deviation (~20 kWh) represents day-to-day weather noise that is inherently unpredictable. If actual December data falls within our confidence bands, the model is performing as expected.

**Q: Why does production drop to near zero in December?**
A: Edmonton is at latitude 53.5°N. In December, the city gets only ~7.5 hours of daylight, the sun barely rises above the horizon (very low solar altitude), and average solar irradiance drops to 0.9 kWh/m²/day — about 6× less than summer. This is a well-known seasonal pattern for northern solar installations.

**Q: How reliable are the 20-year financial projections?**
A: They are estimates based on reasonable assumptions (1,100 kWh/kWp/year for Edmonton, 3% annual rate escalation). The slider on Page 4 lets users adjust these assumptions. Solar panels have 25-year warranties and typically degrade only ~0.5% per year, so the production assumption is conservative. The main uncertainty is future electricity prices.

**Q: What is the difference between RRO, micro-gen credit, and AESO pool?**
A: These represent three ways solar energy can be valued in Alberta:
- **RRO ($0.18/kWh):** If the building uses the solar electricity directly, they avoid buying it at the regulated rate — highest value.
- **Micro-gen credit ($0.12/kWh):** If excess solar is exported to the grid, Alberta's micro-generation regulation requires the utility to pay this credit.
- **AESO pool (~$0.108/kWh):** The wholesale market price — this is the absolute floor price for electricity in Alberta.

**Q: Why use Holt-Winters instead of ARIMA or ML models?**
A: For the dashboard's 30-day forecast, Holt-Winters is ideal because: (1) it naturally handles both trend and seasonality, (2) it works well with the ~100 days of training data we have, (3) it produces smooth, interpretable forecasts with confidence intervals, and (4) it runs fast enough for an interactive dashboard. Our Lab 4 work compared ARIMA, SARIMA, Random Forest, and XGBoost — these are shown in the forecasting notebook but Holt-Winters was chosen for the dashboard for simplicity and interpretability.

**Q: What is the emission factor and why 0.45?**
A: Alberta's grid emission factor is 0.45 tonnes CO₂ equivalent per MWh. This means that on average, producing 1 MWh of electricity in Alberta emits 0.45 tonnes of CO₂ (mostly from natural gas power plants). When solar produces 1 MWh, it displaces that fossil fuel generation, so we say 0.45 tonnes of CO₂ was "avoided." This figure comes from the Government of Alberta's TIER (Technology Innovation and Emissions Reduction) program, 2023 data.

---

*This study guide was prepared for the SPICE Energy Dashboard presentation. All data, calculations, and sources referenced in this document correspond to the actual code in `app.py` and the lab notebooks in the CMPT_3835_MLWI_II project folder.*
