import streamlit as st
import requests
import pandas as pd
from heatmap import render_heatmap
# ---------- Custom CSS (must be before set_page_config) ----------
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetricLabel"] { color: #94A3B8; font-size: 0.9rem; }
    [data-testid="stMetricValue"] { color: #E2E8F0; font-size: 2rem; font-weight: 700; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #334155; }
    [data-testid="stSidebar"] .stRadio label { color: #E2E8F0; font-size: 1rem; padding: 8px 0; }
    .stButton > button[kind="primary"] {
        background-color: #DC2626; color: white; font-weight: bold;
        border-radius: 8px; padding: 14px 28px; font-size: 1.1rem; border: none;
    }
    .stButton > button[kind="primary"]:hover { background-color: #B91C1C; box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); }
    .stButton > button { background-color: #7C3AED; color: white; border-radius: 8px; border: none; }
    h1, h2, h3 { color: #F1F5F9; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------- Page config (must be the FIRST st.* call) ----------
st.set_page_config(
    page_title="Women Safety Analytics",
    page_icon="🛡️",
    layout="wide",
)

# ---------- Constants ----------
API_URL = "http://localhost:8000"

# ---------- Sidebar (defines 'page') ----------
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

    st.markdown("### Welcome")
    st.write(
        "This dashboard provides real-time insights into women's safety "
        "across India using historical NCRB data (2017–2023)."
    )

    try:
        trends = requests.get(f"{API_URL}/trends").json()
        latest_year = trends["years"][-1]
        latest_crimes = trends["total_crimes"][-1]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Districts Analyzed", "771")
        col2.metric("Years Covered", "2017–2023")
        col3.metric(f"Crimes in {latest_year}", f"{latest_crimes:,}")
    except Exception as e:
        st.warning(f"⚠️ Could not reach the API. Make sure the backend is running. Error: {e}")

if page == "🏠 Dashboard":
    st.title("🛡️ Women Safety Analytics & Risk Prediction System")
    st.caption("Safer Communities | Smarter Decisions | Empowered Women")

    st.markdown("### Welcome")
    st.write(
        "This dashboard provides real-time insights into women's safety "
        "across India using historical NCRB data (2017–2023)."
    )

    try:
        trends = requests.get(f"{API_URL}/trends").json()
        latest_year = trends["years"][-1]
        latest_crimes = trends["total_crimes"][-1]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Districts Analyzed", "771")
        col2.metric("Years Covered", "2017–2023")
        col3.metric(f"Crimes in {latest_year}", f"{latest_crimes:,}")
    except Exception as e:
        st.warning(f"⚠️ Could not reach the API. Make sure the backend is running. Error: {e}")

# ---------- Page: Risk Prediction ----------
elif page == "🔮 Risk Prediction":
    st.title("🔮 Risk Prediction")
    st.caption("Enter a district to get its predicted risk level for the next year")

    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        year = col1.number_input("Year", min_value=2017, max_value=2030, value=2023)
        state_code = col2.number_input("State Code", min_value=1, max_value=40, value=8)

        col3, col4 = st.columns(2)
        district_code = col3.number_input("District Code", min_value=1, max_value=800, value=102)

        submitted = st.form_submit_button("Predict Risk")

    if submitted:
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={
                    "year": int(year),
                    "state_code": int(state_code),
                    "district_code": int(district_code),
                }
            )
            result = response.json()

            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                risk = result["predicted_risk"]
                confidence = result["confidence"]

                if risk == "High":
                    st.error(f"⚠️ **{risk} Risk** — Confidence: {confidence:.0%}")
                elif risk == "Medium":
                    st.warning(f"⚡ **{risk} Risk** — Confidence: {confidence:.0%}")
                else:
                    st.success(f"✅ **{risk} Risk** — Confidence: {confidence:.0%}")

                st.markdown(f"**District:** {result['district']}, {result['state']}")
        except Exception as e:
            st.error(f"API error: {e}")


# ---------- Page: Trends ----------
elif page == "📈 Trends":
    st.title("📈 Incident Trends")
    st.caption("Yearly crime trends across India (2017–2023)")

    try:
        trends = requests.get(f"{API_URL}/trends").json()
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
    st.title("🚨 Emergency SOS")
    st.caption("Tap the button below to send an emergency alert")

    if st.button("🚨 SEND SOS ALERT", type="primary", use_container_width=True):
        st.error("✅ SOS Alert Sent! (Demo mode — in production, this would notify your emergency contacts.)")

    st.markdown("---")
    st.subheader("Emergency Contacts")
    st.write("- National Emergency: **112**")
    st.write("- Women Helpline: **1091**")
    st.write("- Police: **100**")
        # ---------- Heatmap ----------
    st.markdown("---")
    render_heatmap(year=2023)