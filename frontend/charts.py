import streamlit as st
import plotly.graph_objects as go
import requests
import pandas as pd

API_URL = "http://localhost:8080"

SHORT_LABELS = {
    "cruelty_by_husband_or_his_relatives": "Domestic Cruelty",
    "assault_on_womenabove_18": "Assault",
    "kidnapping_and_abduction": "Kidnapping",
    "child_rape": "Child Rape",
    "rape_women_above_18": "Rape",
    "sexual_assault_of_children": "Child Sexual Assault",
    "kidnp_and_abductn_of_women_above_18_for_marrg": "Kidnap for Marriage",
    "dowry_prohibition": "Dowry",
    "rape_girls_below_18": "Child Rape (Girls)",
    "insult_to_the_modesty_of_women_above_18": "Modesty Insult",
}


def render_trends_chart(district_name: str = None):
    st.markdown("### 📈 Incident Trends")

    url = f"{API_URL}/trends"
    if district_name:
        url += f"?district_name={district_name}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception as e:
        st.error(f"Could not load trends: {e}")
        return

    if not data.get("years"):
        st.warning("No trend data available for this district.")
        return

    scope = data.get("scope", "All India")
    st.caption(f"Yearly trend — {scope} (2017–2023)")

    df = pd.DataFrame({
        "Year": data["years"],
        "Total Crimes": data["total_crimes"],
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Year"],
        y=df["Total Crimes"],
        mode="lines+markers",
        line=dict(color="#7C3AED", width=3),
        marker=dict(size=10, color="#A78BFA", line=dict(color="#F1F5F9", width=2)),
        fill="tozeroy",
        fillcolor="rgba(124, 58, 237, 0.2)",
        hovertemplate="<b>%{x}</b><br>Crimes: %{y:,}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        xaxis=dict(title="Year", gridcolor="#334155", tickfont=dict(color="#E2E8F0")),
        yaxis=dict(title="Total Crimes", gridcolor="#334155", tickfont=dict(color="#E2E8F0")),
        height=360,
        margin=dict(l=10, r=10, t=10, b=10),
    )

    st.plotly_chart(fig, use_container_width=True, key="trends_chart")

def render_donut(district_name: str = None):
    st.markdown("### 🍩 Incident Categories")

    url = f"{API_URL}/categories"
    if district_name:
        url += f"?district_name={district_name}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception as e:
        st.error(f"Could not load categories: {e}")
        return

    if not data.get("categories"):
        st.warning("No category data available for this district.")
        return

    scope = data.get("scope", "All India")
    st.caption(f"Crime types — {scope} (2017–2023)")

    categories = [SHORT_LABELS.get(c, c.replace("_", " ").title()) for c in data["categories"][:5]]
    counts = data["counts"][:5]
    total = sum(counts)

    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=counts,
        hole=0.65,
        marker=dict(colors=["#DC2626", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6"]),
        textinfo="percent",
        textfont=dict(color="#F1F5F9", size=12),
        hovertemplate="<b>%{label}</b><br>Cases: %{value:,}<br>%{percent}<extra></extra>",
    )])

    fig.update_layout(
        annotations=[dict(
            text=f"<b>{total:,}</b><br><span style='font-size:11px'>Total</span>",
            x=0.5, y=0.5,
            font=dict(size=16, color="#F1F5F9"),
            showarrow=False,
        )],
        showlegend=True,
        legend=dict(
            font=dict(color="#E2E8F0", size=11),
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        margin=dict(l=10, r=10, t=10, b=100),
    )

    st.plotly_chart(fig, use_container_width=True, key="donut_chart")