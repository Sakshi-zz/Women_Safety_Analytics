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
API_URL = "http://localhost:8000"

# ---------- Sidebar ----------
st.sidebar.title("🛡️ Women Safety")
st.sidebar.markdown("Analytics & Risk Prediction System")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🔮 Risk Prediction", "📈 Trends", "🚨 SOS"]
)

# Metric cards
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

        # Compute average severity to classify overall risk
        avg_severity = districts["severity_score"].mean()

        # High risk = districts above 75th percentile of severity
        high_threshold = districts["severity_score"].quantile(0.75)
        high_risk_count = (districts["severity_score"] >= high_threshold).sum()

        # Average risk label
        if avg_severity >= districts["severity_score"].quantile(0.75):
            avg_risk_label = "High"
            avg_risk_color = "#EF4444"
        elif avg_severity >= districts["severity_score"].quantile(0.25):
            avg_risk_label = "Moderate"
            avg_risk_color = "#F59E0B"
        else:
            avg_risk_label = "Low"
            avg_risk_color = "#10B981"

        # ---------- Cards ----------
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);
                        border-left:4px solid #7C3AED;
                        border-radius:12px; padding:18px;
                        box-shadow:0 4px 14px rgba(0,0,0,0.35);">
                <div style="color:#94A3B8; font-size:0.85rem; letter-spacing:0.5px;">
                    TOTAL INCIDENTS
                </div>
                <div style="color:#F1F5F9; font-size:2rem; font-weight:700; margin-top:6px;">
                    {total_incidents:,}
                </div>
                <div style="color:#10B981; font-size:0.85rem; margin-top:6px;">
                    across {total_districts} districts (2023)
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);
                        border-left:4px solid #EF4444;
                        border-radius:12px; padding:18px;
                        box-shadow:0 4px 14px rgba(0,0,0,0.35);">
                <div style="color:#94A3B8; font-size:0.85rem; letter-spacing:0.5px;">
                    HIGH RISK AREAS
                </div>
                <div style="color:#F1F5F9; font-size:2rem; font-weight:700; margin-top:6px;">
                    {int(high_risk_count)}
                </div>
                <div style="color:#EF4444; font-size:0.85rem; margin-top:6px;">
                    out of {total_districts} total areas
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);
                        border-left:4px solid {avg_risk_color};
                        border-radius:12px; padding:18px;
                        box-shadow:0 4px 14px rgba(0,0,0,0.35);">
                <div style="color:#94A3B8; font-size:0.85rem; letter-spacing:0.5px;">
                    AVERAGE RISK LEVEL
                </div>
                <div style="color:{avg_risk_color}; font-size:2rem; font-weight:700; margin-top:6px;">
                    {avg_risk_label}
                </div>
                <div style="color:#94A3B8; font-size:0.85rem; margin-top:6px;">
                    (Overall India — 2023)
                </div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"⚠️ Could not compute metrics: {e}")

    # ---------- Heatmap ----------
    st.markdown("---")
    if HEATMAP_AVAILABLE:
        render_heatmap(year=2023)
    else:
        st.error(f"⚠️ Heatmap module failed to load: {HEATMAP_ERROR}")

    # ---------- Charts ----------
    st.markdown("---")
    selected_district = st.session_state.get("user_district")
    col1, col2 = st.columns([2, 1])
    with col1:
        render_trends_chart(district_name=selected_district)
    with col2:
        render_donut(district_name=selected_district)

    # Heatmap
    st.markdown("---")
    if HEATMAP_AVAILABLE:
        render_heatmap(year=2023)
    else:
        st.error(f"⚠️ Heatmap module failed to load: {HEATMAP_ERROR}")

        # ---------- Charts ----------
    st.markdown("---")

    # Read the district the user picked in the heatmap
    selected_district = st.session_state.get("user_district")

    col1, col2 = st.columns([2, 1])
    with col1:
        render_trends_chart(district_name=selected_district)
    with col2:
        render_donut(district_name=selected_district)

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
                },
                timeout=10,
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
    st.title("🚨 Emergency SOS")
    st.caption("Tap the button below to send an emergency alert")

    if st.button("🚨 SEND SOS ALERT", type="primary", use_container_width=True):
        st.error("✅ SOS Alert Sent! (Demo mode — in production, this would notify your emergency contacts.)")

    st.markdown("---")
    st.subheader("Emergency Contacts")
    st.write("- National Emergency: **112**")
    st.write("- Women Helpline: **1091**")
    st.write("- Police: **100**")