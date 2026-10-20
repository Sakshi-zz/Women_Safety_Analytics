import streamlit as st
import pandas as pd

def render_insights(df, selected_district):
    st.markdown("### 🧠 AI Insight")
    
    if df.empty:
        st.warning("No data available.")
        return

    if not selected_district or selected_district in ["GPS Location", "All India"]:
        total = df["total_crimes"].sum()
        avg_sev = df["severity_score"].mean()
        top = df.nlargest(1, "severity_score").iloc[0]
        
        # Using pure Markdown, NO HTML tags
        text = f"""
        **National Overview:** A total of **{total:,.0f}** incidents recorded. 
        Average severity is **{avg_sev:.1f}**. The most critical zone is **{top['district_name']}** 
        with a severity score of **{int(top['severity_score'])}**.
        
        **Recommendation:** Deploy rapid response units to the top 5 high-risk districts immediately.
        """
        st.info(text)
    
    else:
        row = df[df["district_name"].str.lower() == selected_district.lower()]
        if row.empty:
            st.write(f"No specific data found for {selected_district}.")
            return
        
        row = row.iloc[0]
        percentile = (df["severity_score"] < row["severity_score"]).mean() * 100
        
        if percentile > 90:
            status, action = "🔴 CRITICAL RISK", "Immediate police patrols and emergency response hubs are required."
        elif percentile > 75:
            status, action = "🟠 HIGH RISK", "Strengthen street lighting, CCTV, and local safety awareness campaigns."
        elif percentile > 50:
            status, action = "🟡 MODERATE RISK", "Maintain regular monitoring and community engagement programs."
        else:
            status, action = "🟢 LOW RISK", "Continue standard safety protocols and periodic reviews."

        text = f"""
        **{selected_district} Assessment:** This district is classified as **{status}** (Top {100-percentile:.0f}% nationally).
        
        It recorded **{int(row['total_crimes']):,}** incidents with a severity score of **{int(row['severity_score'])}**.
        
        **Actionable Suggestion:** {action}
        """
        st.warning(text)