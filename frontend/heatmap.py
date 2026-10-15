import streamlit as st
import pandas as pd
import plotly.express as px
import requests

API_URL = "http://localhost:8000"

GEOJSON_URL = "https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson"


@st.cache_data(ttl=3600)
def load_geojson():
    """Download and cache the India district GeoJSON."""
    return requests.get(GEOJSON_URL).json()


def render_heatmap(year: int = 2023):
    st.markdown("### 🗺️ Risk Heatmap")
    st.caption(f"District-level crime severity across India ({year})")

    # Fetch data from the backend
    try:
        response = requests.get(f"{API_URL}/heatmap-data?year={year}", timeout=10)
        data = response.json()
        df = pd.DataFrame(data["districts"])
    except Exception as e:
        st.error(f"Could not load heatmap data: {e}")
        return

    if df.empty:
        st.warning("No district data available for this year.")
        return

    # Load GeoJSON
    try:
        geojson = load_geojson()
    except Exception as e:
        st.error(f"Could not load India GeoJSON: {e}")
        return

    # Plotly choropleth
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="district_name",
        featureidkey="properties.district",
        color="severity_score",
        color_continuous_scale=[
            [0.0, "#10B981"],   # green - low
            [0.4, "#F59E0B"],   # amber - medium
            [0.7, "#F97316"],   # orange - high
            [1.0, "#DC2626"],   # red - very high
        ],
        scope="asia",
        hover_name="district_name",
        hover_data={
            "state_name": True,
            "total_crimes": True,
            "severity_score": True,
        },
        labels={"severity_score": "Severity"},
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
        showcountries=True,
        countrycolor="#334155",
        showsubunits=True,
        subunitcolor="#1E293B",
    )

    fig.update_layout(
        height=550,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        coloraxis_colorbar=dict(
            title="Severity",
            tickfont=dict(color="#E2E8F0"),
            titlefont=dict(color="#E2E8F0"),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Top 5 high-risk districts
    st.markdown("#### Top 5 High-Risk Districts")
    top5 = df.nlargest(5, "severity_score")[["district_name", "state_name", "total_crimes", "severity_score"]]
    st.dataframe(top5, use_container_width=True, hide_index=True)