import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import requests
import pandas as pd

API_URL = "http://localhost:8000"


def get_user_location(df):
    """
    Let the user pick a district by name, or use browser GPS.
    Returns (lat, lon, district_name) or (None, None, None).
    """
    st.markdown("#### 📍 Choose Your Location")

    tab1, tab2 = st.tabs(["🔍 By District Name", "📱 Use My GPS"])

    # --- Tab 1: District name search ---
    with tab1:
        district_names = sorted(df["district_name"].dropna().unique().tolist())
        selected = st.selectbox(
            "Type or select your district:",
            options=["-- Select --"] + district_names,
            key="district_select",
        )

        if selected != "-- Select --":
            row = df[df["district_name"] == selected].iloc[0]
            lat = row["latitude"]
            lon = row["longitude"]
            if pd.notna(lat) and pd.notna(lon):
                st.session_state["user_lat"] = lat
                st.session_state["user_lon"] = lon
                st.session_state["user_district"] = selected
                st.success(f"Selected: {selected} ({lat:.3f}, {lon:.3f})")
            else:
                st.warning(f"No coordinates for {selected}. Try another district.")

    # --- Tab 2: Browser GPS ---
    with tab2:
        try:
            from streamlit_js_eval import get_geolocation
            if st.button("📍 Use My GPS Location", key="use_gps_btn"):
                loc = get_geolocation()
                if loc and "coords" in loc:
                    st.session_state["user_lat"] = loc["coords"]["latitude"]
                    st.session_state["user_lon"] = loc["coords"]["longitude"]
                    st.session_state["user_district"] = "Your Location"
                    st.success(
                        f"Detected: {loc['coords']['latitude']:.4f}, "
                        f"{loc['coords']['longitude']:.4f}"
                    )
        except ImportError:
            st.info("GPS unavailable. Use the district selector instead.")

    return (
        st.session_state.get("user_lat"),
        st.session_state.get("user_lon"),
        st.session_state.get("user_district"),
    )


def render_heatmap(year: int = 2023):
    st.markdown("### 🗺️ Risk Heatmap")
    st.caption("Select your district to see nearby risk zones.")

    # 1. Fetch data
    try:
        response = requests.get(f"{API_URL}/heatmap-data?year={year}", timeout=10)
        data = response.json()
        df = pd.DataFrame(data["districts"])
    except Exception as e:
        st.error(f"Could not load heatmap data: {e}")
        return

    if df.empty or "latitude" not in df.columns:
        st.warning("No coordinate data available.")
        return

    df = df.dropna(subset=["latitude", "longitude"])

    # 2. Location picker
    user_lat, user_lon, district_name = get_user_location(df)

    # 3. Map center
    if user_lat and user_lon:
        center = [user_lat, user_lon]
        zoom = 8
    else:
        center = [22.0, 79.0]
        zoom = 5

    # 4. Base map — OpenStreetMap (no API key)
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="© OpenStreetMap contributors",
        control_scale=True,
    )

    # 5. User marker
    if user_lat and user_lon:
        folium.Marker(
            [user_lat, user_lon],
            popup=district_name or "Selected",
            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
        ).add_to(m)
        folium.Circle(
            [user_lat, user_lon],
            radius=5000,
            color="#3B82F6",
            fill=True,
            fill_opacity=0.15,
        ).add_to(m)

    # 6. Add heatmap layer (glow)
    max_sev = df["severity_score"].max()
    df["weight"] = df["severity_score"] / max_sev if max_sev > 0 else 0.5

    heat_data = df[["latitude", "longitude", "weight"]].values.tolist()
    HeatMap(
        heat_data,
        radius=18,
        blur=20,
        min_opacity=0.35,
        max_zoom=6,
        gradient={
            "0.0": "#10B981",
            "0.4": "#F59E0B",
            "0.7": "#F97316",
            "1.0": "#DC2626",
        },
    ).add_to(m)

    # 7. Add circle markers for the top 20 districts (shows names)
    top20 = df.nlargest(20, "severity_score")
    for _, row in top20.iterrows():
        color = "#DC2626" if row["weight"] > 0.7 else (
            "#F59E0B" if row["weight"] > 0.4 else "#10B981"
        )
        folium.CircleMarker(
            [row["latitude"], row["longitude"]],
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.9,
            popup=f"<b>{row['district_name']}</b><br>"
                  f"{row['state_name']}<br>"
                  f"Severity: {int(row['severity_score'])}",
        ).add_to(m)

    # 8. Legend
    legend_html = """
    <div style="position: fixed;
                bottom: 30px; left: 30px; width: 150px; height: 100px;
                background-color: #1E293B; border: 1px solid #334155;
                border-radius: 8px; padding: 10px; z-index: 9999;
                font-size: 13px; color: #E2E8F0;">
        <b>Risk Level</b><br>
        <span style="color:#DC2626;">●</span> High<br>
        <span style="color:#F97316;">●</span> Medium<br>
        <span style="color:#10B981;">●</span> Low
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # 9. Render
    st_folium(m, width=None, height=520, returned_objects=[])

    # 10. Summary
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔴 Top 5 High-Risk Districts")
        top5 = df.nlargest(5, "severity_score")[
            ["district_name", "state_name", "total_crimes", "severity_score"]
        ]
        st.dataframe(top5, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### 📊 Summary")
        st.metric("Districts shown", f"{len(df)}")
        st.metric("Highest severity", f"{int(df['severity_score'].max()):,}")
        if user_lat and user_lon:
            st.metric("Selected district", district_name or "—")