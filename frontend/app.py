import streamlit as st
import requests
import pandas as pd
from charts import render_trends_chart, render_donut

# ---------- Custom CSS ----------
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #334155; }
    [data-testid="stSidebar"] .stRadio label { color: #E2E8F0; font-size: 1rem; padding: 8px 0; }
    .stButton > button[kind="primary"] {
        background-color: #DC2626; color: white; font-weight: bold;
        border-radius: 8px; padding: 14px 28px; font-size: 1.1rem; border: none;
    }
    h1, h2, h3 { color: #F1F5F9; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Page config ----------
st.set_page_config(
    page_title="Women Safety Analytics",
    page_icon="🛡️",
    layout="wide",
)

# ---------- Safe import of heatmap ----------
try:
    from heatmap import render_heatmap
    HEATMAP_AVAILABLE = True
except Exception as e:
    HEATMAP_AVAILABLE = False
    HEATMAP_ERROR = str(e)

# ---------- Constants ----------
API_URL = "http://localhost:8080"

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
    st.title("🛡️ Women Safety Analytics & Risk Prediction System")
    st.caption("Safer Communities | Smarter Decisions | Empowered Women")

    # ---------- Top metrics ----------
    try:
        hm = requests.get(f"{API_URL}/heatmap-data?year=2023", timeout=10).json()
        districts = pd.DataFrame(hm["districts"])

        total_incidents = int(districts["total_crimes"].sum())
        total_districts = len(districts)
        avg_severity = districts["severity_score"].mean()
        high_threshold = districts["severity_score"].quantile(0.75)
        high_risk_count = (districts["severity_score"] >= high_threshold).sum()

        if avg_severity >= districts["severity_score"].quantile(0.75):
            avg_risk_label, avg_risk_color = "High", "#EF4444"
        elif avg_severity >= districts["severity_score"].quantile(0.25):
            avg_risk_label, avg_risk_color = "Moderate", "#F59E0B"
        else:
            avg_risk_label, avg_risk_color = "Low", "#10B981"

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);
                        border-left:4px solid #7C3AED; border-radius:12px; padding:18px;">
                <div style="color:#94A3B8; font-size:0.85rem;">TOTAL INCIDENTS</div>
                <div style="color:#F1F5F9; font-size:2rem; font-weight:700;">{total_incidents:,}</div>
                <div style="color:#10B981; font-size:0.85rem;">across {total_districts} districts (2023)</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);
                        border-left:4px solid #EF4444; border-radius:12px; padding:18px;">
                <div style="color:#94A3B8; font-size:0.85rem;">HIGH RISK AREAS</div>
                <div style="color:#F1F5F9; font-size:2rem; font-weight:700;">{int(high_risk_count)}</div>
                <div style="color:#EF4444; font-size:0.85rem;">out of {total_districts} total areas</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);
                        border-left:4px solid {avg_risk_color}; border-radius:12px; padding:18px;">
                <div style="color:#94A3B8; font-size:0.85rem;">AVERAGE RISK LEVEL</div>
                <div style="color:{avg_risk_color}; font-size:2rem; font-weight:700;">{avg_risk_label}</div>
                <div style="color:#94A3B8; font-size:0.85rem;">(Overall India — 2023)</div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"⚠️ Could not compute metrics: {e}")

    # ---------- Heatmap (ONLY ONCE) ----------
    st.markdown("---")
    if HEATMAP_AVAILABLE:
        render_heatmap(year=2023)
    else:
        st.error(f"⚠️ Heatmap module failed to load: {HEATMAP_ERROR}")

    # ---------- Charts (ONLY ONCE) ----------
    st.markdown("---")
    selected_district = st.session_state.get("user_district")
    col1, col2 = st.columns([2, 1])
    with col1:
        render_trends_chart(district_name=selected_district)
    with col2:
        render_donut(district_name=selected_district)


# ---------- Page: Risk Prediction ----------
elif page == "🔮 Risk Prediction":
    st.title("🔮 Risk Prediction")
    st.caption("Select a district to estimate its risk level for the next year.")

    # 1. Fetch district list for the dropdowns
    @st.cache_data(ttl=600)  # Cache for 10 mins so it doesn't re-fetch every click
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
        # 2. Build the Cascading Dropdowns (State -> District)
        with st.form("risk_prediction_form"):
            col1, col2 = st.columns(2)

            with col1:
                year = st.number_input(
                    "Historical Year", 
                    min_value=2017, max_value=2023, value=2023, step=1,
                    help="The year of historical data to base the prediction on."
                )
                
                # State Dropdown
                states = sorted(df_districts["state_name"].unique())
                selected_state = st.selectbox("Select State", states)

            with col2:
                # Filter districts based on selected state
                filtered_districts = df_districts[df_districts["state_name"] == selected_state]
                districts = sorted(filtered_districts["district_name"].unique())
                selected_district = st.selectbox("Select District", districts)

                # We don't show this to the user, but we need it for the API
                # (Hidden logic to extract the code)
                district_row = filtered_districts[filtered_districts["district_name"] == selected_district].iloc[0]
                state_code = int(district_row["state_code"])
                district_code = int(district_row["district_code"])

            submitted = st.form_submit_button("🔍 Predict Risk", use_container_width=True)

        # 3. Handle Submission
        if submitted:
            payload = {
                "year": int(year),
                "state_code": state_code,
                "district_code": district_code
            }

            try:
                with st.spinner("Analyzing historical data..."):
                    response = requests.post(f"{API_URL}/predict", json=payload, timeout=30)

                if response.status_code != 200:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    st.stop()

                result = response.json()

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                    st,stop()

                # 4. Display the Result beautifully
                risk = result.get("predicted_risk", "Unknown")
                confidence = result.get("confidence", 0.0)
                predicted_year = year + 1

                st.divider()
                st.subheader("Prediction Result")

                if risk == "High":
                    st.error(f"🚨 **{risk} Risk** for {selected_district} in {predicted_year}")
                elif risk == "Medium":
                    st.warning(f"⚠️ **{risk} Risk** for {selected_district} in {predicted_year}")
                else:
                    st.success(f"🛡️ **{risk} Risk** for {selected_district} in {predicted_year}")

                # Show confidence metric
                st.metric("Model Confidence", f"{confidence * 100:.1f}%")

                st.caption(
                    "This prediction is based on the current year's crime profile "
                    "and historical trends. It is an estimate, not a guarantee of personal safety."
                )

                # Expander for nerds/examiners who want to see the raw JSON
                with st.expander("View complete API response"):
                    st.json(result)

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the FastAPI backend. Make sure uvicorn is running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    
# ---------- Page: Trends ----------
elif page == "📈 Trends":
    # ... (Keep as is) ...
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


# ---------- Page: SOS ----------
elif page == "🚨 SOS":
    # ... (Keep as is) ...
    st.title("🚨 Emergency SOS")
    st.caption("Tap the button below to send an emergency alert")
    if st.button("🚨 SEND SOS ALERT", type="primary", use_container_width=True):
        st.error("✅ SOS Alert Sent! (Demo mode — in production, this would notify your emergency contacts.)")
    st.markdown("---")
    st.subheader("Emergency Contacts")
    st.write("- National Emergency: **112**")
    st.write("- Women Helpline: **1091**")
    st.write("- Police: **100**")