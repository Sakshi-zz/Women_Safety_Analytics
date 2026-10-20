import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import requests
import pandas as pd

API_URL = "http://localhost:8000"


def get_user_location(df):
    st.markdown("#### 📍 Your Location")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write("Tap the button to use your current location, or select manually below.")
    with col2:
        if st.button("📍 Use My Location", key="use_location_btn"):
            try:
                from streamlit_js_eval import get_geolocation
                loc = get_geolocation()
                if loc and "coords" in loc:
                    st.session_state["user_lat"] = loc["coords"]["latitude"]
                    st.session_state["user_lon"] = loc["coords"]["longitude"]
                    st.session_state["user_district"] = "GPS Location"
                    st.success("Location detected!")
                else:
                    st.warning("GPS blocked by browser. Use manual entry below.")
            except ImportError:
                st.warning("streamlit-js-eval not installed. Use manual entry below.")

    with st.expander("Or select your district manually"):
        # We pass df in, so we can list the districts
        district_names = sorted(df["district_name"].dropna().unique())
        
        selected = st.selectbox(
            "Search for your district:", 
            options=["-- Select --"] + district_names
        )
        
        if selected != "-- Select --":
            row = df[df["district_name"] == selected].iloc[0]
            lat = row["latitude"]
            lon = row["longitude"]
            
            if pd.notna(lat) and pd.notna(lon):
                st.session_state["user_lat"] = lat
                st.session_state["user_lon"] = lon
                st.session_state["user_district"] = selected
                st.success(f"Selected: {selected}")
            else:
                st.warning(f"Coordinates missing for {selected}. Try another district.")

    return st.session_state.get("user_lat"), st.session_state.get("user_lon")


def render_heatmap(year: int = 2023):
    st.markdown("### 🗺️ Risk Heatmap")
    st.caption("Glowing hotspots = high severity. Red = Top 10% most dangerous districts.")

    # 1. FETCH DATA FIRST
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

    # 2. THEN GET LOCATION (using the loaded df)
    user_lat, user_lon = get_user_location(df)

    # 3. CALCULATE HEAT WEIGHTS (Strict Percentiles)
    p90 = df["severity_score"].quantile(0.90)
    p75 = df["severity_score"].quantile(0.75)
    p50 = df["severity_score"].quantile(0.50)

    def get_heat_weight(score):
        if score >= p90: return 1.0  # Red
        if score >= p75: return 0.7  # Orange
        if score >= p50: return 0.4  # Yellow
        return 0.1                   # Green/Blue
        
    df["weight"] = df["severity_score"].apply(get_heat_weight)

    # 4. SET MAP CENTER
    if user_lat and user_lon:
        center = [user_lat, user_lon]
        zoom = 8
    else:
        center = [22.0, 79.0]
        zoom = 5

    # 5. BUILD MAP
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="© OpenStreetMap contributors",
        control_scale=True,
    )

    # 6. ADD USER MARKER
    if user_lat and user_lon:
        folium.Marker(
            [user_lat, user_lon],
            popup="You are here",
            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
        ).add_to(m)
        folium.Circle(
            [user_lat, user_lon],
            radius=5000,
            color="#3B82F6",
            fill=True,
            fill_opacity=0.15,
        ).add_to(m)

    # 7. ADD HEATMAP LAYER
    heat_data = df[["latitude", "longitude", "weight"]].values.tolist()
    HeatMap(
        heat_data,
        radius=20,
        blur=15,
        min_opacity=0.5,
        max_zoom=6,
        gradient={
            "0.2": "#3B82F6", # Blue (Low)
            "0.4": "#10B981", # Green
            "0.6": "#F59E0B", # Yellow
            "0.8": "#F97316", # Orange
            "1.0": "#DC2626", # Red (High)
        },
    ).add_to(m)

    # 8. ADD CLUSTERED MARKERS
    marker_cluster = MarkerCluster(name="District Details").add_to(m)
    
    for _, row in df.iterrows():
        if row["weight"] == 1.0:
            color = "#DC2626"
        elif row["weight"] >= 0.7:
            color = "#F59E0B"
        else:
            color = "#10B981"
            
        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 150px;">
            <h4 style="margin:0; color:#333;">{row['district_name']}</h4>
            <p style="margin: 2px 0; color:#666; font-size:12px;">{row['state_name']}</p>
            <hr style="margin: 5px 0;">
            <b>Crimes:</b> {int(row['total_crimes']):,}<br>
            <b>Severity:</b> {int(row['severity_score']):,}
        </div>
        """
        
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            weight=1,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row["district_name"]
        ).add_to(marker_cluster)

    # 9. ADD CONTROLS & LEGEND
    folium.LayerControl().add_to(m)

    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; width: 160px;
                background-color: #1E293B; border: 1px solid #334155;
                border-radius: 8px; padding: 12px; z-index: 9999;
                font-size: 13px; color: #E2E8F0;">
        <b>Risk Level</b><br>
        <span style="color:#DC2626;">●</span> Critical (Top 10%)<br>
        <span style="color:#F97316;">●</span> High<br>
        <span style="color:#F59E0B;">●</span> Medium<br>
        <span style="color:#10B981;">●</span> Low
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

         # ... (Keep everything above this the same) ...

        # ... (Your map creation code above stays the same) ...

    # 10. DEFINE THE CALLBACK FUNCTION
    # This runs BEFORE the page redraws
    def handle_map_click():
        map_state = st.session_state.get("my_map")
        if map_state and map_state.get("last_object_clicked_tooltip"):
            clicked_district = map_state["last_object_clicked_tooltip"]
            st.session_state["user_district"] = clicked_district

    # 11. RENDER MAP
    st_folium(
        m, 
        width=None, 
        height=900, 
        key="my_map",               # <-- REQUIRED for callbacks
        on_select=handle_map_click, # <-- Runs the function immediately
        selection_mode="markers"
    )

    
  