import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(page_title="Urban Mobility & Safety Dashboard", layout="wide")

# ── Data Loading & Cleaning ────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_excel("mobility_reports.xlsx")

    # Parse dates
    df["reported_at"] = pd.to_datetime(df["reported_at"], errors="coerce", utc=True).dt.tz_localize(None)
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce", utc=True).dt.tz_localize(None)

    # Deduplicate by report_id, keep latest
    df = df.sort_values("reported_at").drop_duplicates("report_id", keep="last")

    # Normalize issue_type
    df["issue_type"] = df["issue_type"].str.strip().str.lower()
    synonyms = {
        "pothole": "pothole near crossing",
        "broken light": "broken traffic light",
        "broken traffic lights": "broken traffic light",
        "missing signage": "missing sign",
        "unsafe crosswalk": "unsafe crossing",
        "bus stop broken": "bus stop damage",
        "blocked road": "blocked lane",
        "sidewalk blocked": "sidewalk obstruction",
    }
    df["issue_type"] = df["issue_type"].replace(synonyms)

    # Severity to numeric 1–5
    severity_map = {"low": 1, "medium": 3, "high": 5}
    df["severity"] = df["severity"].apply(lambda x: severity_map.get(str(x).strip().lower(), x))
    df["severity"] = pd.to_numeric(df["severity"], errors="coerce").clip(1, 5)

    # Clean estimated_impact_cost
    df["estimated_impact_cost"] = (
        df["estimated_impact_cost"]
        .astype(str)
        .str.replace(r"[\$,\s]", "", regex=True)
    )
    df["estimated_impact_cost"] = pd.to_numeric(df["estimated_impact_cost"], errors="coerce")

    # Validate coordinates
    valid = df["lat"].between(-90, 90) & df["lon"].between(-180, 180)
    df = df[valid].copy()

    # Feature engineering
    today = pd.Timestamp.today()
    df["resolution_days"] = (df["resolved_at"].fillna(today) - df["reported_at"]).dt.days
    df["is_unresolved"] = df["resolved_at"].isna()
    df["report_month"] = df["reported_at"].dt.to_period("M").astype(str)
    df["report_week"] = df["reported_at"].dt.to_period("W").astype(str)

    def severity_band(s):
        if pd.isna(s): return "unknown"
        if s <= 2: return "low"
        elif s <= 3: return "medium"
        else: return "high"

    df["severity_band"] = df["severity"].apply(severity_band)

    # Spatial join
    gdf = gpd.read_file("districts.geojson")
    points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326")
    joined = gpd.sjoin(points, gdf[["zone_name", "geometry"]], how="left", predicate="within")
    df["district"] = joined["zone_name"].values

    return df, gdf


df, gdf = load_data()

# ── Sidebar Filters ────────────────────────────────────────────────────────────

st.sidebar.title("🔍 Filters")

min_date = df["reported_at"].min().date()
max_date = df["reported_at"].max().date()
date_range = st.sidebar.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)

all_issues = sorted(df["issue_type"].dropna().unique().tolist())
selected_issues = st.sidebar.multiselect("Issue types", all_issues, default=all_issues)

all_districts = sorted(df["district"].dropna().unique().tolist())
selected_districts = st.sidebar.multiselect("Districts", all_districts, default=all_districts)

unresolved_only = st.sidebar.checkbox("Unresolved only", value=False)

all_bands = ["low", "medium", "high"]
selected_bands = st.sidebar.multiselect("Severity band", all_bands, default=all_bands)

generate = st.sidebar.button("Generate Dashboard", type="primary")

# ── Apply Filters ──────────────────────────────────────────────────────────────

if generate or True:  # auto-generate on load too
    start_date, end_date = (date_range[0], date_range[1]) if len(date_range) == 2 else (min_date, max_date)

    fdf = df[
        (df["reported_at"].dt.date >= start_date) &
        (df["reported_at"].dt.date <= end_date) &
        (df["issue_type"].isin(selected_issues)) &
        (df["district"].isin(selected_districts)) &
        (df["severity_band"].isin(selected_bands))
    ].copy()

    if unresolved_only:
        fdf = fdf[fdf["is_unresolved"]]

    # ── Title ──────────────────────────────────────────────────────────────────

    st.title("🚦 Urban Mobility & Safety Dashboard")
    st.caption(f"Showing {len(fdf):,} reports · {start_date} to {end_date}")

    if fdf.empty:
        st.warning("No data matches the current filters. Please adjust your selection.")
        st.stop()

    # ── KPI Cards ──────────────────────────────────────────────────────────────

    total = len(fdf)
    pct_unresolved = fdf["is_unresolved"].mean() * 100
    median_days = fdf["resolution_days"].median()
    total_cost = fdf["estimated_impact_cost"].sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📋 Total Reports", f"{total:,}")
    k2.metric("⏳ % Unresolved", f"{pct_unresolved:.1f}%")
    k3.metric("📅 Median Resolution Days", f"{median_days:.0f}")
    k4.metric("💰 Total Impact Cost", f"${total_cost:,.0f}")

    st.divider()

    # ── District Summary Table (used in map + table) ───────────────────────────

    dist_summary = (
        fdf.groupby("district").agg(
            total_reports=("report_id", "count"),
            unresolved_count=("is_unresolved", "sum"),
            median_resolution_days=("resolution_days", "median"),
            avg_severity=("severity", "mean"),
        ).reset_index()
    )
    dist_summary["unresolved_%"] = (dist_summary["unresolved_count"] / dist_summary["total_reports"] * 100).round(1)

    # ── Map ────────────────────────────────────────────────────────────────────

    st.subheader("🗺️ District Choropleth")
    map_metric = st.selectbox("Choropleth metric", ["total_reports", "unresolved_%", "median_resolution_days"])

    geojson_data = json.loads(gdf.to_json())
    # Add zone_name as feature id
    for feature in geojson_data["features"]:
        feature["id"] = feature["properties"]["zone_name"]

    fig_map = px.choropleth_mapbox(
        dist_summary,
        geojson=geojson_data,
        locations="district",
        color=map_metric,
        mapbox_style="carto-positron",
        zoom=10,
        center={"lat": fdf["lat"].mean(), "lon": fdf["lon"].mean()},
        opacity=0.6,
        hover_data={"district": True, map_metric: True, "total_reports": True, "unresolved_%": True},
        color_continuous_scale="Reds",
        title=f"Districts by {map_metric.replace('_', ' ').title()}",
    )
    fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=450)
    st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # ── Charts ─────────────────────────────────────────────────────────────────

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Reports Over Time")
        time_group = st.radio("Group by", ["report_week", "report_month"], horizontal=True)
        time_series = fdf.groupby(time_group).size().reset_index(name="count")
        fig_time = px.line(time_series, x=time_group, y="count", markers=True,
                           labels={time_group: "Period", "count": "Reports"})
        fig_time.update_layout(height=350)
        st.plotly_chart(fig_time, use_container_width=True)

    with col2:
        st.subheader("📊 Top Issue Types")
        issue_counts = fdf["issue_type"].value_counts().head(10).reset_index()
        issue_counts.columns = ["issue_type", "count"]
        fig_bar = px.bar(issue_counts, x="count", y="issue_type", orientation="h",
                         labels={"count": "Reports", "issue_type": "Issue Type"},
                         color="count", color_continuous_scale="Blues")
        fig_bar.update_layout(height=350, showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("🏘️ District Comparison — Unresolved Rate")
    fig_dist = px.bar(
        dist_summary.sort_values("unresolved_%", ascending=False),
        x="district", y="unresolved_%",
        color="unresolved_%", color_continuous_scale="OrRd",
        labels={"unresolved_%": "Unresolved %", "district": "District"},
    )
    fig_dist.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_dist, use_container_width=True)

    st.divider()

    # ── Summary Table ──────────────────────────────────────────────────────────

    st.subheader("📋 District Summary Table")
    display_cols = ["district", "total_reports", "unresolved_%", "median_resolution_days", "avg_severity"]
    st.dataframe(
        dist_summary[display_cols].sort_values("total_reports", ascending=False).reset_index(drop=True),
        use_container_width=True,
    )

    st.divider()

    # ── Insight Panel ──────────────────────────────────────────────────────────

    st.subheader("💡 Key Insights")

    worst_unresolved = dist_summary.sort_values("unresolved_%", ascending=False).iloc[0]
    slowest_resolution = dist_summary.sort_values("median_resolution_days", ascending=False).iloc[0]

    # Fastest growing issue type (last month vs previous month)
    fdf_sorted = fdf.sort_values("reported_at")
    latest_month = fdf["report_month"].max()
    prev_month = fdf[fdf["report_month"] < latest_month]["report_month"].max()
    latest_counts = fdf[fdf["report_month"] == latest_month]["issue_type"].value_counts()
    prev_counts = fdf[fdf["report_month"] == prev_month]["issue_type"].value_counts()
    growth = (latest_counts - prev_counts).dropna().sort_values(ascending=False)
    top_growth_issue = growth.index[0] if not growth.empty else "N/A"
    top_growth_val = int(growth.iloc[0]) if not growth.empty else 0

    i1, i2, i3 = st.columns(3)
    i1.info(f"🔴 **{worst_unresolved['district']}** has the highest unresolved rate at **{worst_unresolved['unresolved_%']:.1f}%**.")
    i2.warning(f"🕐 **{slowest_resolution['district']}** has the longest median resolution time at **{slowest_resolution['median_resolution_days']:.0f} days**.")
    i3.success(f"📈 **'{top_growth_issue}'** increased the most in the latest month (+{top_growth_val} reports vs prior month).")

    st.divider()

    # ── Export ─────────────────────────────────────────────────────────────────

    st.subheader("⬇️ Export Cleaned Data")
    csv = fdf.drop(columns=["geometry"], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered CSV", csv, "cleaned_reports.csv", "text/csv")