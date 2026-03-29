# SPICE Energy Dashboard — Speaker Notes for Live Demo

**Presenter tips:** Walk through each page in order using the sidebar navigation. Hover over charts to show interactivity. Adjust sliders live to demonstrate responsiveness. Speak in plain language — the audience includes investors, community partners, and funders who may not be technical.

---

## Opening (Before Page 1)

> "Good [morning/afternoon]. Today we're going to walk you through the SPICE Energy Dashboard — a tool we built to help SPICE communicate the performance, financial value, and environmental impact of their community solar projects to stakeholders."
>
> "The dashboard is built in Streamlit using Python and Plotly for interactive visualizations. It pulls from two real datasets: daily solar production data from SPICE's Bissell Thrift Store, exported from the Fronius Solar.web monitoring system, and a weather-plus-solar-generation dataset we used for our machine learning analysis."
>
> "Let me walk you through each page."

---

## Page 1: Portfolio Overview

**What's on screen:** Hero header, 4 metric cards at the top, 4 project cards, a bar chart of installed capacity, and an area chart of Bissell's daily production.

### Top Metric Cards

> "At the top, you see four summary numbers for the entire SPICE portfolio."
>
> - **Total Portfolio Capacity: 88.6 kWp** — "This is the combined nameplate capacity of all four SPICE solar projects. Kilowatt-peak, or kWp, is the maximum output of a solar system under ideal laboratory conditions. It's the standard way to measure and compare solar system sizes."
>
> - **Energy Generated (Bissell): ~6,236 kWh** — "This is the total actual energy produced by the Bissell Thrift Store's rooftop solar system from August 20 to mid-December 2025. This number comes directly from the Fronius inverter monitoring data provided by Annette Dautel. It is measured data, not an estimate."
>
> - **CO₂ Avoided (Bissell): ~2.81 tonnes** — "This tells us how much carbon dioxide was prevented from entering the atmosphere because this solar energy displaced fossil-fuel-generated electricity from Alberta's grid. The calculation is: total kWh divided by 1,000, multiplied by 0.45 — that's Alberta's grid emission factor of 0.45 tonnes CO₂ per megawatt-hour, published by the Government of Alberta under the TIER program."
>
> - **Est. Savings (Bissell): ~$1,122 CAD** — "This is the estimated electricity cost savings. We multiply the total kWh produced by $0.18 per kWh, which is approximately the Alberta Regulated Rate Option — the default rate for consumers who haven't chosen a specific electricity retailer."

### Project Portfolio Cards

> "Below that, we have cards for each of SPICE's four completed solar projects."
>
> "Notice that only Bissell Thrift Store has the 'Live Data' badge. That's because it's the only project for which we received production monitoring data from the Fronius system. The other three projects — Newo Yotina Land Trust at 17.4 kWp, Idylwylde Community League at 16 kWp, and St. Augustine's Anglican Church at 25.22 kWp — are listed with their specifications from SPICE's project documentation, but we don't yet have their production data. The dashboard is designed to incorporate those datasets as they become available."

### Installed Capacity Bar Chart

> "This bar chart compares the system size of each project. Bissell is the largest at 30 kWp, followed by St. Augustine's at 25.22 kWp. Together, these four projects represent 88.6 kWp of community-owned solar in Edmonton."

**Data source:** Hardcoded from SPICE project documentation provided by Annette Dautel.

### Bissell Daily Production Area Chart

> "This area chart shows Bissell's daily energy output over the full data period — late August through mid-December 2025. The key pattern you can see is the clear seasonal decline: production starts high in late August, around 120 to 150 kWh per day, and gradually drops toward zero by December."
>
> "This is entirely expected for Edmonton. At latitude 53.5° North, we go from about 15 hours of daylight in August down to only 7.5 hours in December, and the sun sits much lower in the sky, reducing the intensity of solar radiation reaching the panels."

**Data source:** Bissell Excel file → `date` and `total_system_kwh` columns.

---

## Page 2: Bissell Thrift Store

**What's on screen:** Hero header with system specs, 4 metric cards, daily production bar chart with rolling average, per-inverter breakdown (two tabs), monthly summary dual-axis chart, inverter performance box plot, and expandable raw data table.

### Summary Metrics

> "This page dives deeper into the Bissell system. At the top:"
>
> - **Total Energy** — "The sum of all daily production readings from the Fronius data."
> - **Peak Day** — "The single best day of production — shows the kWh value and the date it occurred. This was in late August when Edmonton had peak summer sun."
> - **Producing Days** — "The number of days where the system generated more than 0.5 kWh. We use the 0.5 threshold to exclude days with negligible output, like deep-winter days where the system might log a tiny fraction of a kWh."
> - **Avg Daily Output** — "The average production on days that actually generated meaningful energy. This gives a more realistic picture than including zero-production winter days."

### Daily Solar Production (Bar Chart + 7-Day Rolling Average)

> "Each yellow bar represents one day's total energy production in kWh. You can hover over any bar to see the exact date and value."
>
> "The dark dotted line is a 7-day rolling average. This smooths out day-to-day weather fluctuations — a cloudy day will cause a big dip in the bars, but the rolling average shows the underlying seasonal trend. You can clearly see the steady decline from over 100 kWh per day in August down toward zero in December."
>
> "If you see a single bar that drops sharply compared to its neighbors, that's almost certainly a cloudy or stormy day — not a system problem."

**Data source:** Bissell Excel → `date` and `total_system_kwh`. Rolling average computed as `.rolling(7, min_periods=1).mean()`.

### Per-Inverter Breakdown

> "The Bissell system has three Fronius Primo 7.6-1 inverters, each connected to approximately 10 kWp of panels."
>
> "The **Stacked Area tab** shows all three inverters layered on top of each other — yellow for Inverter 1, orange for Inverter 2, green for Inverter 3. The total height at any point equals the total system output for that day. In a healthy system, all three color bands should be roughly equal thickness."
>
> "The **Individual Lines tab** shows the same data as separate lines so you can directly compare inverter performance. If one line consistently runs below the others, that could indicate shading issues, panel degradation, or a hardware problem with that inverter string."

**Data source:** Bissell Excel → `inverter_1_kwh`, `inverter_2_kwh`, `inverter_3_kwh`.

### Monthly Summary (Dual-Axis Chart)

> "The yellow bars show the total kWh produced in each calendar month — August through December. The dark line with markers shows the average daily production for each month."
>
> "August and September are the highest-producing months. The total bar might look smaller for August because we only have data starting August 20th — about 12 days — while September has a full 30 days. That's why the daily average line is more useful for a fair month-to-month comparison."
>
> "By November and December, both the total and average drop sharply due to Edmonton's seasonal solar decline."

**Data source:** Bissell Excel, grouped by `month_name`. Left axis = `sum(total_system_kwh)`. Right axis = `mean(total_system_kwh)`.

### Inverter Performance Comparison (Box Plot — kWh/kWp)

> "This box plot compares the three inverters using kWh per kWp — a normalized metric that accounts for each inverter's rated capacity. This is important because it lets us compare performance fairly even if the inverters are connected to slightly different numbers of panels."
>
> "The box spans the 25th to 75th percentile of daily values — the middle 50% of days. The line inside the box is the median. The whiskers extend to 1.5 times the interquartile range. Any dots beyond the whiskers are outliers — unusually high or low production days."
>
> "If all three boxes are at similar heights with similar medians, it confirms the system is balanced and all three inverter strings are performing equally."

**Data source:** Bissell Excel → `inverter_1_kwh_per_kwp`, `inverter_2_kwh_per_kwp`, `inverter_3_kwh_per_kwp`.

### Raw Data Table

> "At the bottom, there's an expandable section where you can view the actual raw data — every day's production for each inverter and the system total. This provides full transparency for anyone who wants to verify the numbers."

---

## Page 3: Environmental Impact

**What's on screen:** Hero header, 4 large impact numbers, cumulative CO₂ area chart, monthly environmental breakdown dual-axis chart, and projected annual impact for all 4 projects.

### Big Impact Numbers (4 Cards)

> "This page translates the energy data into environmental metrics that are tangible for non-technical audiences — funders, policy makers, and the general public."
>
> - **kWh Clean Energy Generated** — "Same total as before — the measured Bissell production."
> - **Tonnes CO₂ Avoided** — "Calculated as total kWh ÷ 1,000 × 0.45. The 0.45 is Alberta's grid emission factor — it means that on average, every megawatt-hour of electricity produced in Alberta emits 0.45 tonnes of CO₂, mostly from natural gas power plants. When solar produces that same megawatt-hour, it displaces fossil fuel generation."
> - **Equivalent Trees Planted** — "We divide the CO₂ tonnes by 0.022 — that's the approximate amount of CO₂ one mature tree absorbs per year, according to US EPA estimates. It gives a relatable comparison."
> - **Cars Off Road (1 year equiv.)** — "We divide the CO₂ tonnes by 4.6 — the average annual CO₂ emissions of a passenger car, also from the US EPA. This makes the impact tangible: 'Our solar panels offset the equivalent of X cars' worth of emissions.'"

### Cumulative CO₂ Avoided Over Time (Area Chart)

> "This green area chart shows how the CO₂ offset accumulates day by day over the data period. Each day's solar production avoids a small amount of CO₂, and this chart plots the running total in kilograms."
>
> "Notice the slope is steep in August and September when production is high, and it flattens out toward December when production drops. The curve visually demonstrates the compounding environmental benefit over time."

**Data source:** Bissell Excel → `total_system_kwh`, converted daily to CO₂ avoided in kg (`kWh ÷ 1000 × 0.45 × 1000`), then cumulatively summed.

### Monthly Environmental Breakdown (Dual-Axis Chart)

> "The green bars show CO₂ avoided per month in tonnes. The dark line shows the equivalent number of trees for each month. This directly mirrors the production pattern — more solar in summer means more environmental impact."

**Data source:** Bissell Excel grouped by month. CO₂ = `monthly_kwh ÷ 1000 × 0.45`. Trees = `CO₂ tonnes ÷ 0.022`.

### Projected Annual Impact (All 4 Projects)

> "This section estimates the full portfolio's annual environmental impact by scaling up from Bissell's data. We use the Natural Resources Canada figure of 1,100 kWh per kWp per year for Edmonton's solar resource. Multiplied by the total portfolio capacity of 88.62 kWp, that gives us a projected annual output of approximately 97,482 kWh."
>
> "The projected CO₂ avoided is about 43.9 tonnes per year for the full portfolio. The methodology is clearly stated in the blue info box below the metrics."
>
> "Important caveat: these are estimates based on Edmonton averages. Actual results will vary by site depending on roof orientation, tilt angle, shading, and local weather."

---

## Page 4: Financial Analysis

**What's on screen:** Hero header, two interactive sliders, 3 savings metric cards, monthly savings bar chart, 20-year Bissell projection dual-axis chart, and full portfolio 20-year metric.

### Interactive Sliders

> "This page starts with two sliders that let the user adjust the financial assumptions in real time."
>
> - **Electricity Rate ($0.10–$0.30/kWh):** "Defaults to $0.18, which is approximately the Alberta Regulated Rate Option. You can slide this to see how savings change under different rate assumptions."
> - **Annual Rate Escalation (0–8%):** "Defaults to 3%. Electricity prices historically increase over time. This models how the value of solar grows as grid electricity gets more expensive while the solar panels produce power for free."
>
> *[Demo: Slide the rate up to $0.25 and show how all the numbers below update instantly.]*

### Savings Metrics

> - **Total Energy Produced** — "The measured Bissell total."
> - **Electricity Savings** — "Total kWh multiplied by the selected electricity rate. This represents what Bissell would have paid to buy that electricity from the grid."
> - **Avg Monthly Savings** — "Total savings divided by approximately 5 months of data."

### Monthly Savings Bar Chart

> "Each bar shows the dollar value of solar production for that month. It's directly proportional to production: more kWh in August and September means more savings. December saves almost nothing because production is near zero."
>
> "This is useful for SPICE to communicate to building partners: 'Your biggest electricity savings come during the summer months.'"

**Data source:** Bissell Excel grouped by month. Savings = `monthly_kwh × selected_rate`.

### 20-Year Savings Projection (Bissell Only)

> "Solar panels typically last 25 or more years with minimal degradation. This chart projects the financial value of Bissell's 30 kWp system over 20 years."
>
> "The yellow bars show annual savings each year — notice they get taller because we're assuming electricity prices increase by the escalation percentage you set. The green cumulative line curves upward, showing total accumulated savings over time."
>
> "The calculation is: 30 kWp × 1,100 kWh/kWp/year = 33,000 kWh per year, multiplied by the electricity rate, which compounds by 3% each year."
>
> "The key insight here: even though solar production stays roughly flat year-to-year, the financial value increases over time because grid electricity keeps getting more expensive."

**Data source:** Calculated in code. Annual kWh estimate = 30 × 1,100 = 33,000 kWh. Rate compounds by escalation % each year.

### Full Portfolio 20-Year Projection

> "Scaling the same calculation to all 88.62 kWp gives the projected 20-year savings for SPICE's entire portfolio. The green success box at the bottom shows the total."
>
> *[Demo: Adjust the escalation slider to show how sensitive the long-term projection is to rate assumptions.]*

---

## Page 5: Forecasting & Scenarios

**What's on screen:** Hero header, external data context (AESO prices table + Edmonton solar profile chart), seasonal decomposition (4 subplots), 30-day forecast chart, revenue scenario side-by-side charts, annual projection and portfolio outlook, 20-year strategic outlook.

> "This is the most analytically rich page. It connects to our Lab 4 time series analysis work and combines production forecasting with external economic data."

### External Data Context — AESO Pool Prices (Left)

> "On the left, we show monthly average wholesale electricity pool prices from AESO — the Alberta Electric System Operator, which runs Alberta's electricity market. These are the actual wholesale market prices for August through December 2025, sourced from aeso.ca."
>
> "Pool prices range from $75/MWh in August to $145/MWh in December. We show both $/MWh and $/kWh for clarity. These prices represent the wholesale market floor for electricity — the minimum value that solar energy could be worth."

**Data source:** Hardcoded from AESO public reporting. Values: Aug $0.075, Sep $0.085, Oct $0.105, Nov $0.130, Dec $0.145 per kWh.

### External Data Context — Edmonton Solar Profile (Right)

> "On the right, this chart shows Edmonton's monthly solar resource. The yellow bars are average daily solar irradiance in kWh per square meter per day — how much solar energy reaches the ground. The dark line shows average daylight hours."
>
> "The orange-shaded months — August through December — highlight the period covered by our Bissell data. Notice that our data covers the steepest decline in Edmonton's solar resource. June has 5.8 kWh/m²/day and 17 hours of daylight; December has only 0.9 kWh/m²/day and 7.5 hours. That's about a 6-to-1 ratio, which explains the dramatic production decline we see in the Bissell data."

**Data source:** Natural Resources Canada (NRCan) — Edmonton solar resource data. Hardcoded values.

### Seasonal Decomposition (4 Subplots)

> "Here we decompose the Bissell daily production into three components using the statsmodels seasonal decomposition with an additive model and a 7-day period."
>
> - **Observed** — "The raw daily production data from August 20 to November 30. This is what the Fronius system actually recorded."
> - **Trend** — "The underlying long-term direction after removing noise. It shows the smooth seasonal decline from about 136 kWh per day in August down toward zero by late November. This is driven entirely by Edmonton's decreasing daylight and lower sun angle."
> - **Seasonal (7-day)** — "A repeating weekly pattern with roughly 10 to 15 kWh amplitude. This likely reflects weekly weather cycles — weather patterns often have multi-day persistence — rather than anything about the solar hardware."
> - **Residual** — "What's left after removing trend and seasonal components. These are random, unpredictable weather-driven fluctuations. The standard deviation of the residuals — shown below as 'Residual Std' — represents the day-to-day weather noise that no model can predict."

**Data source:** Bissell Excel → `total_system_kwh`, Aug 20 – Nov 30. Method: `seasonal_decompose(model='additive', period=7)`.

### 30-Day Production Forecast

> "Using Holt-Winters exponential smoothing — also called triple exponential smoothing — we forecast Bissell's production for December 2025, 30 days ahead."
>
> "The model uses a damped additive trend and additive 7-day seasonality. 'Damped' means the downward trend gradually levels off rather than going negative, which is physically realistic — solar production can't go below zero."
>
> - **Dark solid line** — "Historical observed data from August to November that the model was trained on."
> - **Green dots** — "Actual December production from the Fronius data — this is our ground truth for validating the forecast."
> - **Orange dashed line** — "The model's prediction for December."
> - **Light orange shading** — "95% confidence interval — there's a 95% probability the actual value falls within this band."
> - **Yellow shading** — "80% confidence interval — narrower, with 80% probability."
> - **Gray vertical dotted line** — "Marks December 1st, where the forecast begins."
>
> "The confidence intervals are calculated from the standard deviation of the model's prediction errors during training. The 80% band is ±1.28 standard deviations, and the 95% band is ±1.96 standard deviations. All lower bounds are clamped to zero because solar panels can't produce negative energy."
>
> "Below the chart, we show the forecast total for 30 days, plus the low and high ends of the 95% confidence interval. If actual December data is available, a validation message compares the actual total to the forecast."

**Data source:** Bissell Excel (training: Aug 20 – Nov 30). Method: `ExponentialSmoothing(trend='add', seasonal='add', seasonal_periods=7, damped_trend=True)`.

### Revenue Scenarios (Two Panels)

> "We combine the production forecast with three pricing models to estimate revenue."
>
> "The three scenarios are:"
> - **Best Case — RRO at $0.18/kWh** — "If the building uses the solar electricity directly, avoiding grid purchases at the full regulated rate. This is the highest value per kWh."
> - **Base Case — Micro-generation credit at $0.12/kWh** — "Alberta's micro-generation regulation requires utilities to pay this credit rate for excess solar sent back to the grid."
> - **Worst Case — AESO Pool average at ~$0.108/kWh** — "The average wholesale pool price across the five months — the absolute market floor."
>
> "The **left panel** shows each scenario's expected 30-day revenue as a horizontal bar. The error bars show the 95% confidence interval from the production forecast uncertainty. The gap between best and worst case demonstrates how important pricing is — securing a favorable rate has significant financial impact."
>
> "The **right panel** shows how revenue accumulates day by day over the 30-day forecast. The green shading around the best-case line represents the 95% confidence interval. Steeper lines mean faster revenue accumulation."

### Annual Projection & Portfolio Outlook

> "On the left, a bar chart projects Bissell's output for a full 12 months."
>
> "The colors tell you where each number comes from:"
> - **Green bars** — "Actual measured data from Fronius for September, October, and November."
> - **Yellow bar** — "August, estimated by scaling the partial 12 days of August data to a full month."
> - **Dark bars** — "All other months are projected using a performance ratio we calculated from the actual months. The performance ratio compares what the system actually produced versus what it theoretically should produce based on Edmonton's solar irradiance, the 30 kWp system size, and standard 15% panel efficiency."
>
> "On the right, the annual revenue scenarios show the total annual kWh multiplied by each pricing rate."

### 20-Year Portfolio Strategic Outlook

> "Finally, we scale everything to SPICE's full 88.62 kWp portfolio over 20 years with 3% annual price escalation."
>
> "The **left panel** shows cumulative revenue for all three pricing scenarios. The curves bend upward because rising electricity prices compound over time. Green is best case, yellow is base case, orange is worst case."
>
> "The **right panel** shows cumulative environmental impact — green bars for CO₂ avoided in tonnes, dark line for equivalent trees. These grow linearly because we assume constant annual production. By year 20, the portfolio would avoid approximately 877 tonnes of CO₂."
>
> "The data sources box at the bottom cites every external data source used on this page."

---

## Page 6: Weather & ML Insights

**What's on screen:** Hero header, dataset overview with 3 metrics, interactive scatter plot with dropdown, horizontal correlation bar chart, cloud cover box plot, and ML model summary table.

> "This final page explores what weather factors drive solar generation. It uses a different dataset — the SPG dataset — which has 4,213 hourly records of weather measurements paired with solar power output. This was the dataset assigned for our lab work in Labs 2, 3, and 4."

### Dataset Overview

> "We show three quick stats: average generation, maximum generation, and average temperature from the SPG dataset. This dataset has 21 features covering temperature, humidity, pressure, precipitation, cloud cover, wind, solar radiation, sun position angles, and the target variable — generated power in kilowatts."

**Data source:** SPG CSV (`spg (1) (1).csv`) — 4,213 rows, 21 columns.

### Weather vs Solar Generation (Interactive Scatter Plot)

> "This scatter plot lets you select any weather feature from the dropdown and see how it relates to solar power generation. Each dot is one hourly observation, colored by generation intensity — dark blue is low, yellow is medium, orange is high. We sample 1,000 points for display performance."
>
> *[Demo: Walk through key features:]*
>
> - **Shortwave Radiation** — "The strongest predictor. You see a clear upward trend — more incoming solar radiation means more power generated. This is physically intuitive: radiation is the fuel for solar panels."
> - **Zenith** — "Strong negative relationship. Zenith is the angle of the sun from directly overhead — 0 degrees means the sun is straight above, 90 degrees means it's at the horizon. Lower zenith angles mean more direct sunlight and more power."
> - **Total Cloud Cover** — "Negative relationship — more clouds block solar radiation, reducing generation."
> - **Temperature** — "Moderate positive correlation. Warmer days tend to be sunnier, but the relationship is indirect — it's really about radiation, not temperature itself. Extremely hot temperatures can actually reduce panel efficiency slightly."

### Feature Correlation Bar Chart

> "This horizontal bar chart shows the Pearson correlation coefficient of every numeric feature in the dataset with generated power."
>
> "Green bars mean positive correlation — when that feature increases, power tends to increase. Orange bars mean negative correlation."
>
> "The longest green bar should be shortwave radiation — it's the primary driver of solar output. You'll also see zenith angle as a strong negative correlation. Cloud cover variables appear as negative. Wind speed, humidity, and pressure have weaker effects."
>
> "This directly informed our feature selection in Lab 3 and model training in Lab 4."

**Data source:** SPG CSV. Calculation: `df.corr()['generated_power_kw']` — Pearson correlation of each column with the target.

### Solar Generation by Cloud Cover (Box Plot)

> "We binned cloud cover into three categories: Clear at 0–30%, Partly Cloudy at 30–70%, and Overcast at 70–100%. The box plot shows the distribution of solar generation for each category."
>
> "Clear skies produce the highest and most variable output — the box is tall and high. Partly cloudy conditions produce moderate output. Overcast conditions compress generation toward zero — you can see the box is very flat and near the bottom."
>
> "This visually proves that cloud cover is one of the most important factors in solar production and supports our feature engineering decisions."

**Data source:** SPG CSV → `total_cloud_cover_sfc` binned into 3 categories, plotted against `generated_power_kw`.

### ML Model Performance Summary

> "This table summarizes the five regression models our team tested during our lab work to predict solar power from weather features: Linear Regression as a baseline, Ridge and Lasso for regularization, and Random Forest and Gradient Boosting as tree-based ensemble methods."
>
> "The key insight, shown in the blue info box, is that shortwave radiation, zenith angle, and cloud cover are the strongest predictors. Tree-based models — Random Forest and Gradient Boosting — outperform linear models because the relationship between weather and solar energy is non-linear."
>
> "In Lab 4, we also trained ARIMA and SARIMA time series models and validated them on both the SPG data and the actual Bissell production data."

**Data source:** Hardcoded summary from Lab 2 and Lab 4 model training results.

---

## Closing

> "That concludes our walkthrough of the SPICE Energy Dashboard. To summarize:"
>
> - "We used **real production data** from the Fronius monitoring system for the Bissell Thrift Store — the only SPICE project with available data."
> - "We supplemented that with a **weather-solar generation dataset** for ML analysis, **AESO wholesale electricity prices** for revenue modeling, and **NRCan Edmonton solar resource data** for annual projections."
> - "Every calculation is traceable: CO₂ uses Alberta's 0.45 t/MWh emission factor, savings use the $0.18/kWh regulated rate, and forecasting uses Holt-Winters exponential smoothing with confidence intervals."
> - "The dashboard is designed for SPICE's target audiences: **members and investors** who want to see returns, **community partners** who want to understand building-level impact, and **funders and policy makers** who need environmental metrics."
>
> "Are there any questions?"

---

## Quick Reference: Data Source per Page

| Page | Primary Data | External/Reference Data |
|------|-------------|------------------------|
| 1 — Portfolio Overview | Bissell Excel (production) | SPICE project specs (hardcoded) |
| 2 — Bissell Deep Dive | Bissell Excel (production + per-inverter) | — |
| 3 — Environmental Impact | Bissell Excel (production) | Alberta emission factor (0.45), NRCan yield (1,100 kWh/kWp/yr), EPA tree/car factors |
| 4 — Financial Analysis | Bissell Excel (production) | Alberta electricity rate ($0.18/kWh), NRCan yield |
| 5 — Forecasting & Scenarios | Bissell Excel (production) | AESO pool prices, NRCan irradiance/daylight, Alberta emission factor |
| 6 — Weather & ML Insights | SPG CSV (weather + generation) | Lab 2/4 model training results (hardcoded summary) |
