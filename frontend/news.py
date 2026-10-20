import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Force load_dotenv to look in the current directory
load_dotenv(override=True) 

@st.cache_data(ttl=3600)
def fetch_live_news(district_name):
    api_key = os.getenv("GNEWS_API_KEY")
    
    # ADDED DEBUGGING: This will show if the key is actually loaded
    if not api_key:
        return [{"title": "API Key missing. Make sure .env is in the FRONTEND folder and restart Streamlit.", "url": "#"}]

    query = f'women safety OR crime "{district_name}" India' if district_name and district_name != "All India" else "women safety India crime"
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&country=in&max=4&apikey={api_key}"
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("articles", [])
        return [{"title": f"News API Error: {res.status_code}", "url": "#"}]
    except Exception:
        return [{"title": "Failed to load news.", "url": "#"}]

def render_news(district_name):
    st.markdown(f"### 📰 Live News: {district_name if district_name else 'All India'}")
    articles = fetch_live_news(district_name)
    
    if not articles:
        st.info("No recent news found.")
        return

    for article in articles:
        st.markdown(
            f"""
            <div style="border-bottom: 1px solid #334155; padding: 8px 0;">
                <a href="{article['url']}" target="_blank" style="color: #60A5FA; text-decoration: none; font-weight: 600; font-size: 0.9rem;">
                    {article['title']}
                </a>
            </div>
            """, unsafe_allow_html=True
        )