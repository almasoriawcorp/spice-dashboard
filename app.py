import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPICE Energy Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── SPICE Brand Colors ───────────────────────────────────────────────────────
SPICE_YELLOW = "#F2A900"
SPICE_DARK = "#1B2A4A"
SPICE_GREEN = "#4CAF50"
SPICE_LIGHT_BLUE = "#E8F4FD"
SPICE_ORANGE = "#FF6B35"
SPICE_WHITE = "#FFFFFF"

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .main { background-color: #f8fafc; }

    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 4px solid #F2A900;
    }

    .stMetric label { color: #64748b !important; font-size: 0.85rem !important; }
    .stMetric [data-testid="stMetricValue"] { color: #1B2A4A !important; font-weight: 700 !important; }

    h1, h2, h3 { color: #1B2A4A !important; font-family: 'Inter', sans-serif !important; }

    .hero-header {
        background: linear-gradient(135deg, #1B2A4A 0%, #2d4a7a 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .hero-header h1 { color: white !important; margin: 0; font-size: 2rem; }
    .hero-header p { color: #cbd5e1; margin: 0.5rem 0 0 0; font-size: 1.05rem; }
    .hero-header .accent { color: #F2A900; font-weight: 600; }

    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-top: 3px solid #F2A900;
    }
    .info-card h4 { color: #1B2A4A; margin-top: 0; }
    .info-card p { color: #475569; line-height: 1.6; }

    .project-badge {
        display: inline-block;
        background: #F2A900;
        color: #1B2A4A;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B2A4A 0%, #1e3461 100%);
    }
    div[data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stSidebar"] .stSelectbox label { color: #F2A900 !important; }

    .impact-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1B2A4A;
        line-height: 1;
    }
    .impact-label {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper utilities ──────────────────────────────────────────────────────────
def _resolve_path(*candidate_paths):
    """Return the first existing path from the provided candidates."""
    for path in candidate_paths:
        if path and os.path.exists(path):
            return path
    return None


# ─── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_bissell_data():
    """Load Bissell Thrift Store solar production data from Excel."""
    base_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(base_dir)
    data_dir = _resolve_path(
        os.path.join(base_dir, "data", "bissell"),
        os.path.join(project_root, "data_annette_dautel"),
        os.path.join(project_root, "Data From Annette Dautel"),
    )
    if data_dir is None:
        st.error("Could not locate the data directory (expected 'data_annette_dautel').")
        return None

    filepath = os.path.join(data_dir, "Bissell_Thrift_118_Ave_01012025-01012026.xlsx")

    if not os.path.exists(filepath):
        st.error(f"Data file not found: {filepath}")
        return None

    df = pd.read_excel(filepath, sheet_name="Production 2025", header=0, skiprows=[1])

    # Rename columns for clarity
    df.columns = [
        "date", "inverter_1_kwh", "inverter_2_kwh", "inverter_3_kwh",
        "inverter_1_kwh_per_kwp", "inverter_2_kwh_per_kwp", "inverter_3_kwh_per_kwp",
        "total_system_kwh",
    ]

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["date"])

    # Ensure numeric
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.sort_values("date").reset_index(drop=True)

    # Derived columns
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["day_of_week"] = df["date"].dt.day_name()
    df["week"] = df["date"].dt.isocalendar().week.astype(int)

    return df


@st.cache_data
def load_spg_data():
    """Load the SPG weather + solar generation dataset."""
    base_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(base_dir)
    data_dir = _resolve_path(
        os.path.join(base_dir, "data", "weather"),
        os.path.join(project_root, "lab2_eda"),
        os.path.join(project_root, "Lab2_EDA"),
    )
    if data_dir is None:
        return None

    filepath = os.path.join(data_dir, "spg (1) (1).csv")

    if not os.path.exists(filepath):
        return None

    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["generated_power_kw"] = pd.to_numeric(df["generated_power_kw"], errors="coerce")
    return df


# ─── SPICE Project Portfolio Data ─────────────────────────────────────────────
SPICE_PROJECTS = {
    "Bissell Thrift Store": {
        "capacity_kwp": 30.0,
        "location": "118 Avenue, Edmonton",
        "completed": "2023",
        "type": "Community Thrift Store",
        "inverters": 3,
        "inverter_model": "Fronius Primo 7.6-1 208-240",
        "status": "Active - Monitored",
    },
    "Newo Yotina Land Trust": {
        "capacity_kwp": 17.4,
        "location": "Northeast Edmonton",
        "completed": "October 2024",
        "type": "Community Garden & Education",
        "inverters": None,
        "inverter_model": None,
        "status": "Active",
    },
    "Idylwylde Community League": {
        "capacity_kwp": 16.0,
        "location": "Central Edmonton",
        "completed": "November 2024",
        "type": "Community League",
        "inverters": None,
        "inverter_model": None,
        "status": "Active",
    },
    "St. Augustine's Anglican Church": {
        "capacity_kwp": 25.22,
        "location": "Near Capilano Mall, Edmonton",
        "completed": "2024",
        "type": "Place of Worship",
        "inverters": None,
        "inverter_model": None,
        "status": "Active",
    },
}

TOTAL_CAPACITY_KWP = sum(p["capacity_kwp"] for p in SPICE_PROJECTS.values())

# Alberta grid emission factor (tonnes CO2e per MWh) — 2023 Alberta average
ALBERTA_EMISSION_FACTOR = 0.45  # tonnes CO2e / MWh
# Alberta electricity rate ($/kWh) — approximate blended rate
ALBERTA_ELECTRICITY_RATE = 0.18  # $/kWh


# ─── Helper Functions ──────────────────────────────────────────────────────────
def calculate_co2_avoided(kwh):
    """Calculate CO2 avoided in tonnes."""
    return kwh / 1000 * ALBERTA_EMISSION_FACTOR

def co2_to_trees(co2_tonnes):
    """Approximate trees needed to absorb equivalent CO2 (1 tree ~ 0.022 tonnes/year)."""
    return co2_tonnes / 0.022

def co2_to_cars(co2_tonnes):
    """Approximate cars off road equivalent (avg car ~ 4.6 tonnes CO2/year)."""
    return co2_tonnes / 4.6

def calculate_savings(kwh):
    """Calculate financial savings in CAD."""
    return kwh * ALBERTA_ELECTRICITY_RATE


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ☀️ SPICE Dashboard")
    st.markdown("**Solar Power Investment Cooperative of Edmonton**")
    st.markdown("---")

    page = st.selectbox(
        "📊 Navigate",
        ["Portfolio Overview", "Bissell Thrift Store", "Environmental Impact", "Financial Analysis", "Forecasting & Scenarios", "Weather & ML Insights"],
        index=0,
    )

    st.markdown("---")
    st.markdown("##### About SPICE")
    st.markdown(
        "SPICE is a community-owned renewable energy investment cooperative "
        "bringing solar power to Edmonton's community buildings since 2015."
    )
    st.markdown("[🌐 joinspice.ca](https://joinspice.ca)")
    st.markdown("---")
    st.markdown(
        "<small style='color:#94a3b8 !important;'>CMPT 3835 — Team 11 MVP Dashboard</small>",
        unsafe_allow_html=True,
    )


# ─── Load Data ─────────────────────────────────────────────────────────────────
df_bissell = load_bissell_data()
df_spg = load_spg_data()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: Portfolio Overview
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Portfolio Overview":
    st.markdown(
        """<div class="hero-header">
            <h1>☀️ SPICE Energy Dashboard</h1>
            <p>Real-time solar performance monitoring for the <span class="accent">Solar Power Investment Cooperative of Edmonton</span></p>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Key Metrics ──
    total_energy = df_bissell["total_system_kwh"].sum() if df_bissell is not None else 0
    co2_avoided = calculate_co2_avoided(total_energy)
    savings = calculate_savings(total_energy)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Portfolio Capacity", f"{TOTAL_CAPACITY_KWP:.1f} kWp", "4 Projects")
    col2.metric("Energy Generated (Bissell)", f"{total_energy:,.0f} kWh", "Aug–Dec 2025")
    col3.metric("CO₂ Avoided (Bissell)", f"{co2_avoided:,.2f} tonnes", f"≈ {co2_to_trees(co2_avoided):.0f} trees")
    col4.metric("Est. Savings (Bissell)", f"${savings:,.0f} CAD", f"@ ${ALBERTA_ELECTRICITY_RATE}/kWh")

    st.markdown("---")

    # ── Project Portfolio ──
    st.markdown("### 🏗️ Project Portfolio")

    cols = st.columns(2)
    for i, (name, info) in enumerate(SPICE_PROJECTS.items()):
        with cols[i % 2]:
            is_bissell = name == "Bissell Thrift Store"
            badge = "📊 Live Data" if is_bissell else "📋 Info Only"
            st.markdown(
                f"""<div class="info-card">
                    <span class="project-badge">{info['capacity_kwp']} kWp</span>
                    <span style="font-size:0.75rem; color:#64748b;">{badge}</span>
                    <h4 style="margin-top:0.75rem;">{name}</h4>
                    <p style="margin:0.25rem 0;"><strong>Location:</strong> {info['location']}<br>
                    <strong>Type:</strong> {info['type']}<br>
                    <strong>Completed:</strong> {info['completed']}<br>
                    <strong>Status:</strong> {info['status']}</p>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Capacity Breakdown ──
    st.markdown("### ⚡ Installed Capacity by Project")
    cap_df = pd.DataFrame([
        {"Project": k, "Capacity (kWp)": v["capacity_kwp"]}
        for k, v in SPICE_PROJECTS.items()
    ])

    fig_cap = px.bar(
        cap_df, x="Project", y="Capacity (kWp)",
        color="Capacity (kWp)",
        color_continuous_scale=["#F2A900", "#FF6B35"],
        text="Capacity (kWp)",
    )
    fig_cap.update_traces(texttemplate="%{text:.1f} kWp", textposition="outside")
    fig_cap.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), showlegend=False,
        coloraxis_showscale=False,
        yaxis_title="Capacity (kWp)", xaxis_title="",
        margin=dict(t=30, b=20),
    )
    st.plotly_chart(fig_cap, use_container_width=True)

    # ── Quick Production Chart ──
    if df_bissell is not None:
        st.markdown("### 📈 Bissell Thrift Store — Daily Production (Live Data)")
        fig_quick = px.area(
            df_bissell, x="date", y="total_system_kwh",
            labels={"date": "Date", "total_system_kwh": "Total Energy (kWh)"},
            color_discrete_sequence=[SPICE_YELLOW],
        )
        fig_quick.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter"),
            margin=dict(t=10, b=20),
            xaxis_title="", yaxis_title="Energy (kWh)",
        )
        fig_quick.update_traces(line=dict(width=2), fillcolor="rgba(242,169,0,0.15)")
        st.plotly_chart(fig_quick, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: Bissell Thrift Store Deep Dive
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Bissell Thrift Store":
    st.markdown(
        """<div class="hero-header">
            <h1>🏬 Bissell Thrift Store — 118 Avenue</h1>
            <p>30 kWp rooftop solar system with <span class="accent">3 Fronius Primo 7.6-1 inverters</span> — installed 2023</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if df_bissell is None:
        st.error("Could not load Bissell data.")
        st.stop()

    # ── Summary Metrics ──
    total = df_bissell["total_system_kwh"].sum()
    peak_day = df_bissell.loc[df_bissell["total_system_kwh"].idxmax()]
    producing_days = (df_bissell["total_system_kwh"] > 0.5).sum()
    avg_daily = df_bissell.loc[df_bissell["total_system_kwh"] > 0.5, "total_system_kwh"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Energy", f"{total:,.1f} kWh")
    c2.metric("Peak Day", f"{peak_day['total_system_kwh']:.1f} kWh", peak_day["date"].strftime("%b %d"))
    c3.metric("Producing Days", f"{producing_days}", f"of {len(df_bissell)} days")
    c4.metric("Avg Daily Output", f"{avg_daily:.1f} kWh", "when producing")

    st.markdown("---")

    # ── Daily Production ──
    st.markdown("### 📊 Daily Solar Production")
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Bar(
        x=df_bissell["date"], y=df_bissell["total_system_kwh"],
        name="Total System",
        marker_color=SPICE_YELLOW,
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Energy: %{y:.1f} kWh<extra></extra>",
    ))
    fig_daily.add_trace(go.Scatter(
        x=df_bissell["date"], y=df_bissell["total_system_kwh"].rolling(7, min_periods=1).mean(),
        name="7-Day Average",
        line=dict(color=SPICE_DARK, width=2.5, dash="dot"),
        hovertemplate="7-day avg: %{y:.1f} kWh<extra></extra>",
    ))
    fig_daily.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="", yaxis_title="Energy (kWh)",
        margin=dict(t=40, b=20),
        hovermode="x unified",
    )
    st.plotly_chart(fig_daily, use_container_width=True)

    # ── Per-Inverter Breakdown ──
    st.markdown("### 🔌 Per-Inverter Breakdown")
    tab1, tab2 = st.tabs(["Stacked Area", "Individual Lines"])

    with tab1:
        fig_stack = go.Figure()
        colors = [SPICE_YELLOW, SPICE_ORANGE, SPICE_GREEN]
        fill_colors = ["rgba(242,169,0,0.5)", "rgba(255,107,53,0.5)", "rgba(76,175,80,0.5)"]
        for i, (col, color, fc) in enumerate(zip(
            ["inverter_1_kwh", "inverter_2_kwh", "inverter_3_kwh"], colors, fill_colors
        )):
            fig_stack.add_trace(go.Scatter(
                x=df_bissell["date"], y=df_bissell[col],
                name=f"Inverter {i+1}",
                stackgroup="one",
                line=dict(color=color, width=0.5),
                fillcolor=fc,
            ))
        fig_stack.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter"),
            yaxis_title="Energy (kWh)", xaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=40, b=20),
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    with tab2:
        fig_lines = go.Figure()
        for i, (col, color) in enumerate(zip(
            ["inverter_1_kwh", "inverter_2_kwh", "inverter_3_kwh"], colors
        )):
            fig_lines.add_trace(go.Scatter(
                x=df_bissell["date"], y=df_bissell[col],
                name=f"Inverter {i+1}",
                line=dict(color=color, width=2),
            ))
        fig_lines.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter"),
            yaxis_title="Energy (kWh)", xaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=40, b=20),
        )
        st.plotly_chart(fig_lines, use_container_width=True)

    # ── Monthly Summary ──
    st.markdown("### 📅 Monthly Summary")
    monthly = df_bissell.groupby("month_name").agg(
        total_kwh=("total_system_kwh", "sum"),
        avg_daily_kwh=("total_system_kwh", "mean"),
        peak_kwh=("total_system_kwh", "max"),
        days=("total_system_kwh", "count"),
    ).reset_index()

    month_order = ["August", "September", "October", "November", "December"]
    monthly["month_name"] = pd.Categorical(monthly["month_name"], categories=month_order, ordered=True)
    monthly = monthly.sort_values("month_name")

    fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])
    fig_monthly.add_trace(
        go.Bar(x=monthly["month_name"], y=monthly["total_kwh"],
               name="Total (kWh)", marker_color=SPICE_YELLOW),
        secondary_y=False,
    )
    fig_monthly.add_trace(
        go.Scatter(x=monthly["month_name"], y=monthly["avg_daily_kwh"],
                   name="Avg Daily (kWh)", line=dict(color=SPICE_DARK, width=3),
                   mode="lines+markers"),
        secondary_y=True,
    )
    fig_monthly.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=20),
    )
    fig_monthly.update_yaxes(title_text="Total Energy (kWh)", secondary_y=False)
    fig_monthly.update_yaxes(title_text="Avg Daily (kWh)", secondary_y=True)
    st.plotly_chart(fig_monthly, use_container_width=True)

    # ── Inverter Performance Comparison ──
    st.markdown("### ⚖️ Inverter Performance Comparison (kWh/kWp)")
    inv_perf = df_bissell[["date", "inverter_1_kwh_per_kwp", "inverter_2_kwh_per_kwp", "inverter_3_kwh_per_kwp"]].copy()
    inv_perf_melted = inv_perf.melt(id_vars="date", var_name="Inverter", value_name="kWh/kWp")
    inv_perf_melted["Inverter"] = inv_perf_melted["Inverter"].map({
        "inverter_1_kwh_per_kwp": "Inverter 1",
        "inverter_2_kwh_per_kwp": "Inverter 2",
        "inverter_3_kwh_per_kwp": "Inverter 3",
    })

    fig_perf = px.box(
        inv_perf_melted, x="Inverter", y="kWh/kWp",
        color="Inverter",
        color_discrete_sequence=[SPICE_YELLOW, SPICE_ORANGE, SPICE_GREEN],
    )
    fig_perf.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), showlegend=False,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_perf, use_container_width=True)

    # ── Raw Data ──
    with st.expander("📋 View Raw Data"):
        st.dataframe(
            df_bissell[["date", "inverter_1_kwh", "inverter_2_kwh", "inverter_3_kwh", "total_system_kwh"]]
            .style.format({"inverter_1_kwh": "{:.2f}", "inverter_2_kwh": "{:.2f}",
                           "inverter_3_kwh": "{:.2f}", "total_system_kwh": "{:.2f}"}),
            use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: Environmental Impact
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Environmental Impact":
    st.markdown(
        """<div class="hero-header">
            <h1>🌍 Environmental Impact</h1>
            <p>Measuring the <span class="accent">real environmental benefits</span> of SPICE's community solar projects</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if df_bissell is None:
        st.error("Could not load data.")
        st.stop()

    total_kwh = df_bissell["total_system_kwh"].sum()
    co2 = calculate_co2_avoided(total_kwh)
    trees = co2_to_trees(co2)
    cars = co2_to_cars(co2)

    # ── Big Impact Numbers ──
    st.markdown("### Bissell Thrift Store Impact (Aug–Dec 2025)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""<div class="info-card" style="text-align:center;">
            <div class="impact-number" style="color:{SPICE_YELLOW};">{total_kwh:,.0f}</div>
            <div class="impact-label">kWh Clean Energy Generated</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div class="info-card" style="text-align:center;">
            <div class="impact-number" style="color:{SPICE_GREEN};">{co2:,.2f}</div>
            <div class="impact-label">Tonnes CO₂ Avoided</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""<div class="info-card" style="text-align:center;">
            <div class="impact-number" style="color:{SPICE_GREEN};">{trees:,.0f}</div>
            <div class="impact-label">Equivalent Trees Planted</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""<div class="info-card" style="text-align:center;">
            <div class="impact-number" style="color:{SPICE_ORANGE};">{cars:,.2f}</div>
            <div class="impact-label">Cars Off Road (1 year equiv.)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Cumulative CO2 Avoided ──
    st.markdown("### 📈 Cumulative CO₂ Avoided Over Time")
    df_env = df_bissell[["date", "total_system_kwh"]].copy()
    df_env["co2_avoided_kg"] = df_env["total_system_kwh"] / 1000 * ALBERTA_EMISSION_FACTOR * 1000
    df_env["cumulative_co2_kg"] = df_env["co2_avoided_kg"].cumsum()

    fig_co2 = go.Figure()
    fig_co2.add_trace(go.Scatter(
        x=df_env["date"], y=df_env["cumulative_co2_kg"],
        fill="tozeroy",
        line=dict(color=SPICE_GREEN, width=3),
        fillcolor="rgba(76,175,80,0.15)",
        hovertemplate="<b>%{x|%b %d}</b><br>Cumulative CO₂ avoided: %{y:.1f} kg<extra></extra>",
    ))
    fig_co2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"),
        yaxis_title="Cumulative CO₂ Avoided (kg)",
        xaxis_title="",
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_co2, use_container_width=True)

    # ── Monthly Environmental Impact ──
    st.markdown("### 🗓️ Monthly Environmental Breakdown")
    monthly_env = df_bissell.groupby("month_name")["total_system_kwh"].sum().reset_index()
    month_order = ["August", "September", "October", "November", "December"]
    monthly_env["month_name"] = pd.Categorical(monthly_env["month_name"], categories=month_order, ordered=True)
    monthly_env = monthly_env.sort_values("month_name")
    monthly_env["co2_tonnes"] = monthly_env["total_system_kwh"] / 1000 * ALBERTA_EMISSION_FACTOR
    monthly_env["trees_equiv"] = monthly_env["co2_tonnes"] / 0.022

    fig_env_monthly = make_subplots(specs=[[{"secondary_y": True}]])
    fig_env_monthly.add_trace(
        go.Bar(x=monthly_env["month_name"], y=monthly_env["co2_tonnes"],
               name="CO₂ Avoided (tonnes)", marker_color=SPICE_GREEN),
        secondary_y=False,
    )
    fig_env_monthly.add_trace(
        go.Scatter(x=monthly_env["month_name"], y=monthly_env["trees_equiv"],
                   name="Trees Equivalent", line=dict(color=SPICE_DARK, width=3),
                   mode="lines+markers"),
        secondary_y=True,
    )
    fig_env_monthly.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=20),
    )
    fig_env_monthly.update_yaxes(title_text="CO₂ Avoided (tonnes)", secondary_y=False)
    fig_env_monthly.update_yaxes(title_text="Trees Equivalent", secondary_y=True)
    st.plotly_chart(fig_env_monthly, use_container_width=True)

    # ── Projected Annual Impact ──
    st.markdown("### 🔮 Projected Annual Impact (All 4 Projects)")
    st.markdown(
        "Based on Bissell's measured performance, scaled to the full portfolio capacity."
    )

    # Scale from Bissell's 30 kWp to total 88.62 kWp
    scale_factor = TOTAL_CAPACITY_KWP / 30.0
    # Annualize: Bissell data covers ~4 months of varying production
    # Use measured data to estimate annual (Edmonton avg ~1,100 kWh/kWp/year for solar)
    annual_kwh_per_kwp = 1100  # Edmonton average
    projected_annual_kwh = TOTAL_CAPACITY_KWP * annual_kwh_per_kwp
    proj_co2 = calculate_co2_avoided(projected_annual_kwh)
    proj_trees = co2_to_trees(proj_co2)
    proj_cars = co2_to_cars(proj_co2)
    proj_savings = calculate_savings(projected_annual_kwh)

    pc1, pc2, pc3, pc4 = st.columns(4)
    pc1.metric("Projected Annual Energy", f"{projected_annual_kwh:,.0f} kWh")
    pc2.metric("Projected CO₂ Avoided", f"{proj_co2:,.1f} tonnes/year")
    pc3.metric("Equivalent Trees", f"{proj_trees:,.0f} trees")
    pc4.metric("Projected Savings", f"${proj_savings:,.0f} CAD/year")

    st.info(
        f"**Methodology:** Projected using Edmonton's average solar yield of ~{annual_kwh_per_kwp} kWh/kWp/year "
        f"across all {TOTAL_CAPACITY_KWP:.1f} kWp of installed capacity. "
        f"Alberta grid emission factor: {ALBERTA_EMISSION_FACTOR} tonnes CO₂e/MWh."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: Financial Analysis
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Financial Analysis":
    st.markdown(
        """<div class="hero-header">
            <h1>💰 Financial Analysis</h1>
            <p>Electricity cost savings and <span class="accent">financial value</span> for community partners and investors</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if df_bissell is None:
        st.error("Could not load data.")
        st.stop()

    # ── Rate Selector ──
    st.markdown("### ⚙️ Assumptions")
    col_rate, col_esc, _ = st.columns([1, 1, 2])
    with col_rate:
        rate = st.slider("Electricity Rate ($/kWh)", 0.10, 0.30, 0.18, 0.01)
    with col_esc:
        escalation = st.slider("Annual Rate Escalation (%)", 0.0, 8.0, 3.0, 0.5)

    total_kwh = df_bissell["total_system_kwh"].sum()
    total_savings = total_kwh * rate

    st.markdown("---")

    # ── Savings Metrics ──
    st.markdown("### 💵 Bissell Thrift Store Savings (Aug–Dec 2025)")
    s1, s2, s3 = st.columns(3)
    s1.metric("Total Energy Produced", f"{total_kwh:,.0f} kWh")
    s2.metric("Electricity Savings", f"${total_savings:,.2f} CAD")
    s3.metric("Avg Monthly Savings", f"${total_savings / 5:,.2f} CAD", "over ~5 months")

    st.markdown("---")

    # ── Monthly Savings ──
    st.markdown("### 📊 Monthly Savings Breakdown")
    monthly_fin = df_bissell.groupby("month_name")["total_system_kwh"].sum().reset_index()
    month_order = ["August", "September", "October", "November", "December"]
    monthly_fin["month_name"] = pd.Categorical(monthly_fin["month_name"], categories=month_order, ordered=True)
    monthly_fin = monthly_fin.sort_values("month_name")
    monthly_fin["savings"] = monthly_fin["total_system_kwh"] * rate

    fig_savings = go.Figure()
    fig_savings.add_trace(go.Bar(
        x=monthly_fin["month_name"], y=monthly_fin["savings"],
        marker_color=SPICE_YELLOW,
        text=[f"${v:,.0f}" for v in monthly_fin["savings"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Savings: $%{y:,.2f}<extra></extra>",
    ))
    fig_savings.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"),
        yaxis_title="Savings (CAD)", xaxis_title="",
        margin=dict(t=40, b=20),
    )
    st.plotly_chart(fig_savings, use_container_width=True)

    # ── 20-Year Projection ──
    st.markdown("### 📈 20-Year Savings Projection (Bissell Thrift Store)")
    st.markdown("Solar panels typically last 25+ years. Here's the projected cumulative savings.")

    annual_kwh_estimate = 30 * 1100  # 30 kWp * 1100 kWh/kWp/year
    years = list(range(1, 21))
    annual_savings = []
    cumulative = []
    running_total = 0
    current_rate = rate

    for y in years:
        s = annual_kwh_estimate * current_rate
        running_total += s
        annual_savings.append(s)
        cumulative.append(running_total)
        current_rate *= (1 + escalation / 100)

    proj_df = pd.DataFrame({"Year": years, "Annual Savings": annual_savings, "Cumulative Savings": cumulative})

    fig_proj = make_subplots(specs=[[{"secondary_y": True}]])
    fig_proj.add_trace(
        go.Bar(x=proj_df["Year"], y=proj_df["Annual Savings"],
               name="Annual Savings", marker_color=SPICE_YELLOW, opacity=0.7),
        secondary_y=False,
    )
    fig_proj.add_trace(
        go.Scatter(x=proj_df["Year"], y=proj_df["Cumulative Savings"],
                   name="Cumulative Savings", line=dict(color=SPICE_GREEN, width=3),
                   mode="lines+markers"),
        secondary_y=True,
    )
    fig_proj.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=20),
        xaxis_title="Year",
    )
    fig_proj.update_yaxes(title_text="Annual Savings (CAD)", secondary_y=False)
    fig_proj.update_yaxes(title_text="Cumulative Savings (CAD)", secondary_y=True)
    st.plotly_chart(fig_proj, use_container_width=True)

    st.success(
        f"**Over 20 years**, the Bissell Thrift Store solar system is projected to save "
        f"**${cumulative[-1]:,.0f} CAD** in electricity costs "
        f"(assuming {escalation}% annual rate escalation from ${rate}/kWh)."
    )

    # ── Full Portfolio Projection ──
    st.markdown("### 🏢 Full Portfolio 20-Year Projection")
    portfolio_annual = TOTAL_CAPACITY_KWP * 1100
    port_cumulative = []
    running = 0
    current_rate = rate
    for y in years:
        s = portfolio_annual * current_rate
        running += s
        port_cumulative.append(running)
        current_rate *= (1 + escalation / 100)

    st.metric("Projected 20-Year Portfolio Savings", f"${port_cumulative[-1]:,.0f} CAD")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: Forecasting & Scenarios
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Forecasting & Scenarios":
    st.markdown(
        """<div class="hero-header">
            <h1>🔮 Forecasting & Strategic Scenario Modeling</h1>
            <p>Predicting short-term <span class="accent">production and revenue</span> under uncertainty</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if df_bissell is None:
        st.warning("Bissell data not found.")
        st.stop()

    # ── Prepare time series ──
    ts_fc = df_bissell[["date", "total_system_kwh"]].copy()
    ts_fc = ts_fc.set_index("date").asfreq("D").fillna(0)
    ts_active = ts_fc.loc["2025-08-20":"2025-11-30"]

    # ── AESO price data ──
    REGULATED_RATE = 0.18
    MICRO_GEN_CREDIT = 0.12
    aeso_prices = pd.DataFrame({
        "month": pd.to_datetime(["2025-08-01", "2025-09-01", "2025-10-01", "2025-11-01", "2025-12-01"]),
        "pool_price_kwh": [0.075, 0.085, 0.105, 0.130, 0.145],
    })
    AESO_AVG = aeso_prices["pool_price_kwh"].mean()

    scenarios = {
        "Best Case (RRO $0.18/kWh)": REGULATED_RATE,
        "Base Case (Micro-gen $0.12/kWh)": MICRO_GEN_CREDIT,
        "Worst Case (AESO Pool ~$0.108/kWh)": AESO_AVG,
    }
    scenario_colors = [SPICE_GREEN, SPICE_YELLOW, SPICE_ORANGE]

    # ── External Data Context ──
    st.markdown("### 📡 External Data Context")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**AESO Monthly Pool Prices (2025)**")
        aeso_display = aeso_prices.copy()
        aeso_display["month"] = aeso_display["month"].dt.strftime("%B %Y")
        aeso_display["$/MWh"] = (aeso_display["pool_price_kwh"] * 1000).map("${:,.0f}".format)
        aeso_display["$/kWh"] = aeso_display["pool_price_kwh"].map("${:,.3f}".format)
        st.dataframe(aeso_display[["month", "$/MWh", "$/kWh"]], use_container_width=True, hide_index=True)
        st.caption("Source: AESO — Alberta Electric System Operator")

    with col_b:
        st.markdown("**Edmonton Seasonal Solar Profile**")
        months_lbl = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        irradiance = [1.2, 2.1, 3.4, 4.6, 5.5, 5.8, 5.6, 4.7, 3.3, 2.1, 1.2, 0.9]
        daylight = [8.1, 9.8, 11.8, 13.9, 15.7, 17.0, 16.5, 14.8, 12.7, 10.6, 8.7, 7.5]

        fig_solar = make_subplots(specs=[[{"secondary_y": True}]])
        fig_solar.add_trace(go.Bar(
            x=months_lbl, y=irradiance, name="Irradiance (kWh/m²/day)",
            marker_color=SPICE_YELLOW, opacity=0.8,
        ), secondary_y=False)
        fig_solar.add_trace(go.Scatter(
            x=months_lbl, y=daylight, name="Daylight (hrs)",
            line=dict(color=SPICE_DARK, width=3), mode="lines+markers",
        ), secondary_y=True)
        # Highlight Bissell period
        for m in ["Aug", "Sep", "Oct", "Nov", "Dec"]:
            fig_solar.add_vrect(
                x0=months_lbl.index(m) - 0.4, x1=months_lbl.index(m) + 0.4,
                fillcolor=SPICE_ORANGE, opacity=0.08, line_width=0,
            )
        fig_solar.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter"), height=320, margin=dict(t=30, b=30),
            legend=dict(orientation="h", y=-0.2),
        )
        fig_solar.update_yaxes(title_text="kWh/m²/day", secondary_y=False)
        fig_solar.update_yaxes(title_text="Daylight hrs", secondary_y=True)
        st.plotly_chart(fig_solar, use_container_width=True)
        st.caption("Source: Natural Resources Canada — Edmonton. Orange = Bissell data period.")

    st.markdown("---")

    # ── Seasonal Decomposition ──
    st.markdown("### 📊 Seasonal Decomposition")
    st.markdown("Decomposing Bissell daily production into **trend**, **weekly seasonal**, and **residual** components.")

    decomp = seasonal_decompose(ts_active["total_system_kwh"], model="additive", period=7)

    fig_decomp = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                                subplot_titles=["Observed (kWh)", "Trend", "Seasonal (7-day)", "Residual"])

    fig_decomp.add_trace(go.Scatter(
        x=decomp.observed.index, y=decomp.observed.values,
        line=dict(color=SPICE_DARK, width=1.2), name="Observed",
    ), row=1, col=1)
    fig_decomp.add_trace(go.Scatter(
        x=decomp.trend.index, y=decomp.trend.values,
        line=dict(color=SPICE_ORANGE, width=2.5), name="Trend",
        fill="tozeroy", fillcolor="rgba(255,107,53,0.15)",
    ), row=2, col=1)
    fig_decomp.add_trace(go.Scatter(
        x=decomp.seasonal.index, y=decomp.seasonal.values,
        line=dict(color=SPICE_GREEN, width=1.2), name="Seasonal",
    ), row=3, col=1)
    fig_decomp.add_trace(go.Scatter(
        x=decomp.resid.dropna().index, y=decomp.resid.dropna().values,
        mode="markers", marker=dict(color=SPICE_YELLOW, size=4), name="Residual",
    ), row=4, col=1)

    fig_decomp.update_layout(
        height=700, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), showlegend=False, margin=dict(t=40, b=20),
    )
    st.plotly_chart(fig_decomp, use_container_width=True)

    trend_vals = decomp.trend.dropna()
    c1, c2, c3 = st.columns(3)
    c1.metric("Trend Start (Aug)", f"{trend_vals.iloc[:7].mean():.0f} kWh/day")
    c2.metric("Trend End (Nov)", f"{trend_vals.iloc[-7:].mean():.0f} kWh/day")
    c3.metric("Residual Std", f"{decomp.resid.dropna().std():.1f} kWh", "day-to-day weather noise")

    st.markdown("---")

    # ── 30-Day Production Forecast ──
    st.markdown("### 🔮 30-Day Production Forecast")
    st.markdown("Using **Holt-Winters** exponential smoothing (damped additive trend + 7-day seasonality).")

    hw_model = ExponentialSmoothing(
        ts_active["total_system_kwh"],
        trend="add", seasonal="add", seasonal_periods=7, damped_trend=True,
    ).fit(optimized=True)

    forecast_steps = 30
    forecast = hw_model.forecast(forecast_steps)
    forecast.index = pd.date_range(start="2025-12-01", periods=forecast_steps, freq="D")
    forecast = forecast.clip(lower=0)

    resid_std = hw_model.resid.dropna().std()
    ci_80_lo = (forecast - 1.28 * resid_std).clip(lower=0)
    ci_80_hi = forecast + 1.28 * resid_std
    ci_95_lo = (forecast - 1.96 * resid_std).clip(lower=0)
    ci_95_hi = forecast + 1.96 * resid_std

    ts_dec = ts_fc.loc["2025-12-01":"2025-12-31"]

    fig_fc = go.Figure()
    # Historical
    fig_fc.add_trace(go.Scatter(
        x=ts_active.index, y=ts_active["total_system_kwh"],
        line=dict(color=SPICE_DARK, width=1.2), name="Observed (Aug–Nov)",
    ))
    # Actual December
    if len(ts_dec) > 0:
        fig_fc.add_trace(go.Scatter(
            x=ts_dec.index, y=ts_dec["total_system_kwh"],
            mode="markers", marker=dict(color=SPICE_GREEN, size=7), name="Actual Dec (ground truth)",
        ))
    # Forecast line
    fig_fc.add_trace(go.Scatter(
        x=forecast.index, y=forecast.values,
        line=dict(color=SPICE_ORANGE, width=3, dash="dash"), name="Forecast (Holt-Winters)",
    ))
    # 95% CI
    fig_fc.add_trace(go.Scatter(
        x=list(forecast.index) + list(forecast.index[::-1]),
        y=list(ci_95_hi.values) + list(ci_95_lo.values[::-1]),
        fill="toself", fillcolor="rgba(255,107,53,0.12)",
        line=dict(width=0), name="95% Confidence Interval",
    ))
    # 80% CI
    fig_fc.add_trace(go.Scatter(
        x=list(forecast.index) + list(forecast.index[::-1]),
        y=list(ci_80_hi.values) + list(ci_80_lo.values[::-1]),
        fill="toself", fillcolor="rgba(242,169,0,0.25)",
        line=dict(width=0), name="80% Confidence Interval",
    ))
    fig_fc.add_shape(type="line", x0="2025-12-01", x1="2025-12-01", y0=0, y1=1, yref="paper",
                      line=dict(color="gray", width=1, dash="dot"))
    fig_fc.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Inter"),
        height=450, margin=dict(t=30, b=30),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_fc, use_container_width=True)

    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Forecast Total (30 days)", f"{forecast.sum():.1f} kWh")
    fc2.metric("95% CI Low", f"{ci_95_lo.sum():.1f} kWh")
    fc3.metric("95% CI High", f"{ci_95_hi.sum():.1f} kWh")

    if len(ts_dec) > 0 and ts_dec["total_system_kwh"].sum() > 0:
        actual_dec = ts_dec["total_system_kwh"].sum()
        st.info(f"**Validation:** Actual December total = {actual_dec:.1f} kWh vs forecast = {forecast.sum():.1f} kWh")

    st.markdown("---")

    # ── Revenue Scenarios ──
    st.markdown("### 💰 Best / Worst-Case Revenue Scenarios")
    st.markdown(
        "Combining the production forecast with three pricing models: "
        "**RRO** (regulated rate), **Micro-generation credit**, and **AESO wholesale pool**."
    )

    fig_rev = make_subplots(rows=1, cols=2, subplot_titles=[
        "30-Day Revenue Estimate (with 95% CI)", "Cumulative Revenue Over 30 Days"
    ])

    # Left: horizontal bar with CI error bars
    for i, ((name, rate), color) in enumerate(zip(scenarios.items(), scenario_colors)):
        rev_exp = forecast.sum() * rate
        rev_lo = ci_95_lo.sum() * rate
        rev_hi = ci_95_hi.sum() * rate
        fig_rev.add_trace(go.Bar(
            y=[name], x=[rev_exp], orientation="h",
            marker_color=color, name=name, showlegend=False,
            text=[f"${rev_exp:.2f}"], textposition="outside",
            error_x=dict(type="data", symmetric=False,
                         array=[rev_hi - rev_exp], arrayminus=[rev_exp - rev_lo]),
        ), row=1, col=1)

    # Right: cumulative revenue lines
    for (name, rate), color in zip(scenarios.items(), scenario_colors):
        cum_rev = (forecast * rate).cumsum()
        fig_rev.add_trace(go.Scatter(
            x=forecast.index, y=cum_rev.values,
            line=dict(color=color, width=2.5), name=name,
        ), row=1, col=2)

    # Add 95% CI shading for best case
    best_rate = REGULATED_RATE
    fig_rev.add_trace(go.Scatter(
        x=list(forecast.index) + list(forecast.index[::-1]),
        y=list((ci_95_hi * best_rate).cumsum().values) + list((ci_95_lo * best_rate).cumsum().values[::-1]),
        fill="toself", fillcolor="rgba(76,175,80,0.1)",
        line=dict(width=0), name="Best Case 95% CI", showlegend=False,
    ), row=1, col=2)

    fig_rev.update_layout(
        height=420, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), margin=dict(t=40, b=20),
        legend=dict(orientation="h", y=-0.2),
    )
    fig_rev.update_xaxes(title_text="Revenue (CAD)", row=1, col=1)
    fig_rev.update_xaxes(title_text="Date", row=1, col=2)
    fig_rev.update_yaxes(title_text="Cumulative Revenue (CAD)", row=1, col=2)
    st.plotly_chart(fig_rev, use_container_width=True)

    st.markdown("---")

    # ── Annual & Portfolio Projections ──
    st.markdown("### 📈 Annual Projection & Portfolio Outlook")

    irradiance_by_month = {1:1.2,2:2.1,3:3.4,4:4.6,5:5.5,6:5.8,7:5.6,8:4.7,9:3.3,10:2.1,11:1.2,12:0.9}
    days_in_month = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    actual_monthly = {9: 2148.97, 10: 1784.19, 11: 662.24}

    pr_vals = []
    for m in [9, 10, 11]:
        theo = irradiance_by_month[m] * 30.0 * days_in_month[m] * 0.15
        if theo > 0:
            pr_vals.append(actual_monthly[m] / theo)
    avg_pr = np.mean(pr_vals)

    proj_rows = []
    for m in range(1, 13):
        theo = irradiance_by_month[m] * 30.0 * days_in_month[m] * 0.15
        proj = theo * avg_pr
        if m in actual_monthly:
            kwh, src = actual_monthly[m], "Actual"
        elif m == 8:
            kwh, src = 1631.98 / 12 * 31, "Estimated"
        else:
            kwh, src = proj, "Projected"
        proj_rows.append({"month": m, "name": pd.Timestamp(f"2025-{m:02d}-01").strftime("%b"), "kwh": kwh, "source": src})

    proj_df = pd.DataFrame(proj_rows)
    annual_kwh = proj_df["kwh"].sum()

    p_col1, p_col2 = st.columns(2)

    with p_col1:
        bar_colors_proj = [SPICE_GREEN if r["source"] == "Actual" else
                           SPICE_YELLOW if r["source"] == "Estimated" else SPICE_DARK
                           for _, r in proj_df.iterrows()]
        fig_annual = go.Figure()
        fig_annual.add_trace(go.Bar(
            x=proj_df["name"], y=proj_df["kwh"], marker_color=bar_colors_proj,
            text=[f'{v:,.0f}' for v in proj_df["kwh"]], textposition="outside",
        ))
        fig_annual.update_layout(
            title="Projected Monthly Production — Bissell 30 kWp",
            plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Inter"),
            height=400, margin=dict(t=40, b=30), yaxis_title="kWh",
        )
        st.plotly_chart(fig_annual, use_container_width=True)
        st.caption("🟢 Actual (Fronius)  🟡 Estimated (partial data)  ⬛ Projected (seasonal model)")

    with p_col2:
        fig_rev_annual = go.Figure()
        for (name, rate), color in zip(scenarios.items(), scenario_colors):
            fig_rev_annual.add_trace(go.Bar(
                y=[name], x=[annual_kwh * rate], orientation="h",
                marker_color=color, text=[f"${annual_kwh * rate:,.0f}"],
                textposition="outside", showlegend=False,
            ))
        fig_rev_annual.update_layout(
            title="Annual Revenue Scenarios — Bissell 30 kWp",
            plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Inter"),
            height=400, margin=dict(t=40, b=30, l=220), xaxis_title="Revenue (CAD)",
        )
        st.plotly_chart(fig_rev_annual, use_container_width=True)

    st.markdown("---")

    # ── 20-Year Portfolio Outlook ──
    st.markdown("### 🏢 20-Year Portfolio Strategic Outlook")
    st.markdown(f"Scaling to SPICE's full **{TOTAL_CAPACITY_KWP:.1f} kWp** portfolio with **3% annual price escalation**.")

    portfolio_annual = TOTAL_CAPACITY_KWP * 1100  # Edmonton yield
    years_range = np.arange(1, 21)
    rate_esc = 0.03

    fig_20 = make_subplots(rows=1, cols=2, subplot_titles=[
        "Cumulative Revenue (20 Years)", "Cumulative Environmental Impact"
    ])

    for (name, rate), color in zip(scenarios.items(), scenario_colors):
        cum = np.cumsum([portfolio_annual * rate * (1 + rate_esc) ** y for y in range(20)])
        fig_20.add_trace(go.Scatter(
            x=years_range, y=cum / 1000, line=dict(color=color, width=2.5),
            mode="lines+markers", marker=dict(size=4), name=name,
        ), row=1, col=1)

    co2_cum = portfolio_annual / 1000 * ALBERTA_EMISSION_FACTOR * years_range
    trees_cum = co2_cum / 0.022

    fig_20.add_trace(go.Bar(
        x=years_range, y=co2_cum, marker_color=SPICE_GREEN, opacity=0.7,
        name="CO₂ Avoided (tonnes)",
    ), row=1, col=2)
    fig_20.add_trace(go.Scatter(
        x=years_range, y=trees_cum, line=dict(color=SPICE_DARK, width=2.5),
        mode="lines+markers", marker=dict(size=4), name="Trees Equivalent",
        yaxis="y4",
    ), row=1, col=2)

    fig_20.update_layout(
        height=450, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), margin=dict(t=40, b=20),
        legend=dict(orientation="h", y=-0.2),
    )
    fig_20.update_yaxes(title_text="Cumulative Revenue ($K CAD)", row=1, col=1)
    fig_20.update_yaxes(title_text="CO₂ Avoided (tonnes)", row=1, col=2)
    fig_20.update_xaxes(title_text="Year", row=1, col=1)
    fig_20.update_xaxes(title_text="Year", row=1, col=2)
    st.plotly_chart(fig_20, use_container_width=True)

    # Summary metrics
    s1, s2, s3 = st.columns(3)
    s1.metric("Portfolio Annual Production", f"{portfolio_annual:,.0f} kWh")
    s2.metric("20-Year CO₂ Avoided", f"{co2_cum[-1]:,.0f} tonnes")
    s3.metric("20-Year Revenue (Best)", f"${np.cumsum([portfolio_annual * REGULATED_RATE * (1 + rate_esc) ** y for y in range(20)])[-1]:,.0f}")

    st.info(
        "**Data Sources:** Production data from Fronius Solar.web (Bissell Thrift Store). "
        "AESO pool prices from aeso.ca. Edmonton solar resource from Natural Resources Canada. "
        "Alberta emission factor: 0.45 t CO₂e/MWh (Gov. of Alberta TIER, 2023)."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6: Weather & ML Insights
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Weather & ML Insights":
    st.markdown(
        """<div class="hero-header">
            <h1>🤖 Weather & ML Insights</h1>
            <p>Exploring the relationship between <span class="accent">weather conditions and solar generation</span></p>
        </div>""",
        unsafe_allow_html=True,
    )

    if df_spg is None:
        st.warning("SPG dataset not found. Please ensure `spg (1) (1).csv` is in the Lab2_EDA folder.")
        st.stop()

    st.markdown("### 📊 Dataset Overview")
    st.markdown(f"**{len(df_spg):,} records** with {len(df_spg.columns)} features")

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Generation", f"{df_spg['generated_power_kw'].mean():,.1f} kW")
    c2.metric("Max Generation", f"{df_spg['generated_power_kw'].max():,.1f} kW")
    c3.metric("Avg Temperature", f"{df_spg['temperature_2_m_above_gnd'].mean():.1f}°C")

    st.markdown("---")

    # ── Key Weather Correlations ──
    st.markdown("### 🌤️ Weather vs Solar Generation")

    weather_col = st.selectbox(
        "Select weather feature to explore:",
        [
            "shortwave_radiation_backwards_sfc",
            "temperature_2_m_above_gnd",
            "total_cloud_cover_sfc",
            "relative_humidity_2_m_above_gnd",
            "wind_speed_10_m_above_gnd",
            "zenith",
            "azimuth",
            "angle_of_incidence",
        ],
        format_func=lambda x: x.replace("_", " ").title(),
    )

    fig_scatter = px.scatter(
        df_spg.sample(min(1000, len(df_spg)), random_state=42),
        x=weather_col, y="generated_power_kw",
        color="generated_power_kw",
        color_continuous_scale=["#1B2A4A", "#F2A900", "#FF6B35"],
        opacity=0.6,
        labels={weather_col: weather_col.replace("_", " ").title(),
                "generated_power_kw": "Generated Power (kW)"},
    )
    fig_scatter.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"),
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Correlation Heatmap ──
    st.markdown("### 🔥 Feature Correlation with Solar Generation")
    num_cols = df_spg.select_dtypes(include=[np.number]).columns
    corr_with_target = df_spg[num_cols].corr()["generated_power_kw"].drop("generated_power_kw").sort_values()

    fig_corr = go.Figure()
    colors = [SPICE_GREEN if v > 0 else SPICE_ORANGE for v in corr_with_target.values]
    fig_corr.add_trace(go.Bar(
        x=corr_with_target.values,
        y=[c.replace("_", " ").title()[:35] for c in corr_with_target.index],
        orientation="h",
        marker_color=colors,
    ))
    fig_corr.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter", size=11),
        xaxis_title="Correlation with Generated Power",
        margin=dict(t=20, b=20, l=200),
        height=500,
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # ── Cloud Cover Analysis ──
    st.markdown("### ☁️ Solar Generation by Cloud Cover Level")
    df_cloud = df_spg.copy()
    df_cloud["cloud_level"] = pd.cut(
        df_cloud["total_cloud_cover_sfc"],
        bins=[0, 30, 70, 100],
        labels=["Clear (0-30%)", "Partly Cloudy (30-70%)", "Overcast (70-100%)"],
        include_lowest=True,
    )
    df_cloud = df_cloud.dropna(subset=["cloud_level"])

    fig_cloud = px.box(
        df_cloud, x="cloud_level", y="generated_power_kw",
        color="cloud_level",
        color_discrete_sequence=[SPICE_YELLOW, SPICE_ORANGE, SPICE_DARK],
        labels={"cloud_level": "Cloud Cover", "generated_power_kw": "Generated Power (kW)"},
    )
    fig_cloud.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), showlegend=False,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_cloud, use_container_width=True)

    # ── ML Model Results Summary ──
    st.markdown("### 🧠 ML Model Performance Summary")
    st.markdown(
        "From our team's model training (Lab 2), we tested 5 regression models "
        "to predict solar power generation from weather features."
    )

    model_results = pd.DataFrame({
        "Model": ["Linear Regression", "Ridge", "Lasso", "Random Forest", "Gradient Boosting"],
        "Description": [
            "Baseline linear model",
            "L2 regularized linear model",
            "L1 regularized (sparse) model",
            "Ensemble of 300 decision trees",
            "Sequential boosted trees",
        ],
        "Best For": [
            "Interpretability",
            "Handling multicollinearity",
            "Feature selection",
            "Non-linear patterns",
            "Best overall accuracy",
        ],
    })
    st.dataframe(model_results, use_container_width=True, hide_index=True)

    st.info(
        "**Key Insight:** Shortwave radiation, zenith angle, and cloud cover are the strongest "
        "predictors of solar generation. Tree-based models (Random Forest, Gradient Boosting) "
        "typically outperform linear models for this type of non-linear weather-energy relationship."
    )


# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.85rem;'>"
    "☀️ SPICE Energy Dashboard — CMPT 3835 Team 11 MVP | "
    "Data source: Fronius Solar.web monitoring system | "
    "<a href='https://joinspice.ca' style='color:#F2A900;'>joinspice.ca</a>"
    "</div>",
    unsafe_allow_html=True,
)
