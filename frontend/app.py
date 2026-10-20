import streamlit as st
import requests
import pandas as pd
from charts import render_trends_chart, render_donut
from insights import render_insights
from news import render_news

# ---------- Page config (MUST BE FIRST) ----------
st.set_page_config(
    page_title="Women Safety Analytics",
    page_icon="🛡️",
    layout="wide",
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    /* Basic styling for dark mode */
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #334155; }
    [data-testid="stSidebar"] .stRadio label { color: #E2E8F0; font-size: 1rem; padding: 8px 0; }
    h1, h2, h3 { color: #F1F5F9; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 95%; }
</style>
""", unsafe_allow_html=True)

# ---------- Constants ----------
API_URL = "http://localhost:8000"

# ---------- Sidebar ----------
st.sidebar.title("🛡️ Women Safety")
st.sidebar.markdown("Analytics & Risk Prediction System")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🔮 Risk Prediction", "📈 Trends", "🚨 SOS"]
)

# ---------- Page: Dashboard ----------
if page == "🏠 Dashboard":
    st.title("🛡️ Women Safety Analytics Dashboard")
    st.caption("Safer Communities | Smarter Decisions | Empowered Women")

    # Fetch data
    @st.cache_data(ttl=600)
    def get_dashboard_data():
        try:
            res = requests.get(f"{API_URL}/heatmap-data?year=2023", timeout=10).json()
            return pd.DataFrame(res["districts"])
        except Exception:
            return pd.DataFrame()

    df = get_dashboard_data()
    current_district = st.session_state.get("user_district", "All India")
    chart_district = None if current_district in ["All India", "GPS Location"] else current_district

        # ==========================================
    # 1. TOP METRIC CARDS
    # ==========================================
    if not df.empty:
        total_incidents = int(df["total_crimes"].sum())
        total_districts = len(df)
        avg_severity = df["severity_score"].mean()
        high_threshold = df["severity_score"].quantile(0.75)
        high_risk_count = (df["severity_score"] >= high_threshold).sum()

        if avg_severity >= df["severity_score"].quantile(0.75):
            avg_risk_label, avg_risk_color = "High", "#EF4444"
        elif avg_severity >= df["severity_score"].quantile(0.25):
            avg_risk_label, avg_risk_color = "Moderate", "#F59E0B"
        else:
            avg_risk_label, avg_risk_color = "Low", "#10B981"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%); border-left:4px solid #7C3AED; border-radius:12px; padding:18px;">
                <div style="color:#94A3B8; font-size:0.85rem;">TOTAL INCIDENTS</div>
                <div style="color:#F1F5F9; font-size:2rem; font-weight:700;">{total_incidents:,}</div>
                <div style="color:#10B981; font-size:0.85rem;">across {total_districts} districts (2023)</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%); border-left:4px solid #EF4444; border-radius:12px; padding:18px;">
                <div style="color:#94A3B8; font-size:0.85rem;">HIGH RISK AREAS</div>
                <div style="color:#F1F5F9; font-size:2rem; font-weight:700;">{int(high_risk_count)}</div>
                <div style="color:#EF4444; font-size:0.85rem;">out of {total_districts} total areas</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%); border-left:4px solid {avg_risk_color}; border-radius:12px; padding:18px;">
                <div style="color:#94A3B8; font-size:0.85rem;">AVERAGE RISK LEVEL</div>
                <div style="color:{avg_risk_color}; font-size:2rem; font-weight:700;">{avg_risk_label}</div>
                <div style="color:#94A3B8; font-size:0.85rem;">(Overall India — 2023)</div></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

        # ==========================================
    # 2. MAIN GRID: Map (Left) vs Insight/Critical/Summary (Right)
    # ==========================================
    col_left, col_right = st.columns([1.8, 1], gap="medium")

    with col_left:
        # MAP (Only the map is here now)
        with st.container(border=True):
            from heatmap import render_heatmap
            render_heatmap(year=2023)

    with col_right:
        @st.fragment
        def right_panel():
            dist = st.session_state.get("user_district", "All India")
            
            with st.container(border=True):
                render_insights(df, dist)
                
            with st.container(border=True):
                st.markdown("### 🚨 Top Critical")
                if not df.empty:
                    top5 = df.nlargest(5, "severity_score")[["district_name", "severity_score"]]
                    st.dataframe(top5, hide_index=True, use_container_width=True)

            with st.container(border=True):
                st.markdown("### 📊 Summary")
                if not df.empty:
                    st.metric("Total Crimes", f"{int(df['total_crimes'].sum()):,}")
                    st.metric("Critical Zones", len(df[df['severity_score'] >= df['severity_score'].quantile(0.9)]))
        
        right_panel()

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 3. FULL-WIDTH NEWS SECTION
    # ==========================================
    # Because this is outside the columns, it takes the full width of the page.
    with st.container(border=True):
        @st.fragment
        def news_fragment():
            dist = st.session_state.get("user_district", "All India")
            render_news(dist)
        
        news_fragment()

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 4. BOTTOM ROW: Trend + Donut
    # ==========================================
    col_trend, col_donut = st.columns([1.8, 1], gap="medium")

    with col_trend:
        with st.container(border=True):
            @st.fragment
            def trend_frag():
                dist = st.session_state.get("user_district")
                chart_d = None if dist in ["All India", "GPS Location"] else dist
                render_trends_chart(district_name=chart_d)
            trend_frag()

    with col_donut:
        with st.container(border=True):
            @st.fragment
            def donut_frag():
                dist = st.session_state.get("user_district")
                chart_d = None if dist in ["All India", "GPS Location"] else dist
                render_donut(district_name=chart_d)
            donut_frag()


# ==========================================
# PAGE: RISK PREDICTION
# ==========================================
elif page == "🔮 Risk Prediction":
    st.title("🔮 Risk Prediction")
    st.caption("Select a district to estimate its risk level for the next year.")

    @st.cache_data(ttl=600)
    def get_districts():
        try:
            res = requests.get(f"{API_URL}/heatmap-data?year=2023", timeout=10).json()
            return pd.DataFrame(res["districts"])
        except Exception:
            return pd.DataFrame()

    df_districts = get_districts()

    if df_districts.empty:
        st.error("Could not load district data from the API. Is the backend running?")
    else:
        with st.form("risk_prediction_form"):
            col1, col2 = st.columns(2)
            with col1:
                year = st.number_input("Historical Year", min_value=2017, max_value=2023, value=2023, step=1)
                states = sorted(df_districts["state_name"].unique())
                selected_state = st.selectbox("Select State", states)
            with col2:
                filtered_districts = df_districts[df_districts["state_name"] == selected_state]
                districts = sorted(filtered_districts["district_name"].unique())
                selected_district = st.selectbox("Select District", districts)
                
                district_row = filtered_districts[filtered_districts["district_name"] == selected_district].iloc[0]
                state_code = int(district_row["state_code"])
                district_code = int(district_row["district_code"])

            submitted = st.form_submit_button("🔍 Predict Risk", use_container_width=True)

        if submitted:
            payload = {"year": int(year), "state_code": state_code, "district_code": district_code}
            try:
                with st.spinner("Analyzing historical data..."):
                    response = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
                
                result = response.json()
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    risk = result.get("predicted_risk", "Unknown")
                    confidence = result.get("confidence", 0.0)
                    
                    st.divider()
                    if risk == "High":
                        st.error(f"🚨 **{risk} Risk** for {selected_district} in {year+1}")
                    elif risk == "Medium":
                        st.warning(f"⚠️ **{risk} Risk** for {selected_district} in {year+1}")
                    else:
                        st.success(f"🛡️ **{risk} Risk** for {selected_district} in {year+1}")
                        
                    st.metric("Model Confidence", f"{confidence * 100:.1f}%")
                    with st.expander("View complete API response"):
                        st.json(result)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# ==========================================
# PAGE: TRENDS
# ==========================================
elif page == "📈 Trends":
    st.title("📈 Incident Trends")
    st.caption("Yearly crime trends across India (2017–2023)")
    try:
        trends = requests.get(f"{API_URL}/trends", timeout=5).json()
        df = pd.DataFrame({
            "Year": trends["years"],
            "Total Crimes": trends["total_crimes"],
            "Severity Score": trends["severity_score"],
        })
        st.line_chart(df.set_index("Year"))
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"API error: {e}")

# ==========================================
# PAGE: SOS
# ==========================================
elif page == "🚨 SOS":
    st.title("🚨 Emergency SOS")
    if st.button("🚨 SEND SOS ALERT", type="primary", use_container_width=True):
        st.error("✅ SOS Alert Sent! (Demo mode)")