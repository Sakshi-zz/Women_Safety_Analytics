# 🛡️ Women Safety Analytics & Risk Prediction System

An **end-to-end machine learning and analytics system** that predicts women's safety risk across Indian districts, visualizes crime hotspots on an interactive map, and provides instant data-driven insights and emergency SOS capabilities.

Built as a final-year CSE (AI/ML) project using real NCRB crime data (2017–2023).

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#️-architecture)
- [Tech Stack](#️-tech-stack)
- [Dataset](#-dataset)
- [Machine Learning Models](#-machine-learning-models)
- [Installation & Setup](#️-installation--setup)
- [Project Structure](#-project-structure--code-links)
- [API Endpoints](#-api-endpoints)
- [Future Scope](#-future-scope)
- [Author](#-author)

---

## 🎯 Overview

Women in India often lack accessible, data-driven tools to assess the safety of different areas. Crime statistics exist in government reports but are buried in PDFs and not actionable for everyday decisions.

This project bridges that gap by providing a unified dashboard with:
- A **district-level heatmap** showing crime severity across India.
- **Instant analytical insights** generated via Pandas to assess the selected district.
- **Live news feeds** related to women's safety for the selected region.
- A **risk prediction model** that classifies districts as High / Medium / Low risk.
- An **emergency SOS feature** that sends real SMS alerts with live GPS locations.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗺️ **Interactive Heatmap** | Folium-based map with red/yellow/green hotspots over high-crime districts |
| 🧠 **Instant Data Insights** | Real-time Pandas data analysis generating risk assessments and safety suggestions |
| 📰 **Live News Feed** | Integrated GNews API fetching the latest safety news for the selected district |
| 🔮 **Risk Prediction** | Random Forest model (88.6% F1) predicts next year's risk level |
| 📈 **Incident Trends** | Time-series visualization of yearly crime patterns (2017–2023) |
| 🍩 **Category Breakdown** | Donut chart of the top 5 crime types per district |
| 📍 **District Search** | User selects their district by clicking the map or using the dropdown |
| 🚨 **SOS Alerts (Real SMS)** | Sends real-time SMS alerts with Google Maps links via TextBee API |
| 💾 **Saved Contacts** | Saves emergency contacts in the session for quick access |
| 🎨 **Dark UI** | Custom Streamlit theme styled to match the design mockup |

---

## 🏗️ Architecture

```text
┌──────────────────────────────────────────────────────────┐
│  DATA LAYER                                              │
│  NCRB CSV  →  Cleaning  →  Severity Scoring  →  GeoJSON  │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  ML LAYER                                                │
│  Random Forest (Risk)  |  Prophet (Trends)               │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                       │
│  /predict  /trends  /heatmap-data                        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  FRONTEND (Streamlit + Folium + Plotly)                  │
│  Dashboard | Heatmap | Insights | Live News | SOS        │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| **Language** | Python 3.10+ |
| **Data** | pandas, numpy |
| **ML** | scikit-learn (Random Forest), Prophet (forecasting) |
| **Backend** | FastAPI, Uvicorn |
| **Frontend** | Streamlit |
| **Mapping** | Folium, streamlit-folium |
| **Charts** | Plotly |
| **External APIs** | GNews (for live news), TextBee (for SOS SMS) |
| **Geocoding** | geopy, Nominatim (OpenStreetMap) |

---

## 📊 Dataset

**Source:** National Crime Records Bureau (NCRB) via [India Data Portal](https://ckan.indiadataportal.com/dataset/crime-statistics)

| Property | Value |
|----------|-------|
| **Records** | 6,281 rows → 5,104 after aggregation |
| **Districts** | 771 |
| **States/UTs** | 36 |
| **Years** | 2017–2023 |
| **Crime Categories** | 42 (rape, kidnapping, assault, dowry, cyber, POCSO, etc.) |

**Preprocessing:**
1. Fill missing values with 0.
2. Standardize district names.
3. Aggregate registration circles → district level.
4. Compute **severity score** (weighted sum where violent crimes = weight 5, lower crimes = weight 1).
5. Geocode district centers via Nominatim (97% coverage).

---

## 🤖 Machine Learning Models

### 1. Random Forest Classifier — Risk Prediction
- **Target:** Next year's risk level (High / Medium / Low).
- **Features:** 42 crime-type columns from the current year.
- **Approach:** Time-shift target (`severity_score.shift(-1)`) to avoid data leakage.
- **Performance:** Accuracy: 88.56% | F1 Score: 88.60%

### 2. Prophet — Time-Series Forecasting
- **Target:** Yearly severity score (2017–2023).
- **Forecast:** 2024, 2025.
- **Output:** ~2.9M → 3.0M (rising trend).

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- An Android phone (for the TextBee SMS Gateway)
- API Keys for GNews and TextBee

### Step 1: Clone the repo
```bash
git clone https://github.com/Sakshi-zz/Women_Safety_Analytics.git
cd Women_Safety_Analytics
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Get your API Keys
**GNews API (for Live News):**
1. Sign up at [gnews.io](https://gnews.io).
2. Copy your API key.

**TextBee API (for SOS SMS):**
1. Sign up at [textbee.dev](https://textbee.dev).
2. Download the **TextBee Android app** on your phone and register it (this turns your phone into an SMS gateway).
3. In the TextBee Dashboard, go to **API Keys** and generate a new key.
4. Copy this key.

### Step 4: Environment Variables
Create a `.env` file in the `frontend/` folder and add both keys:
```env
GNEWS_API_KEY=your_gnews_api_key
TEXTBEE_API_KEY=your_textbee_api_key
```
*(Note: If you hardcoded the TextBee key directly into `sos.py`, you can skip adding `TEXTBEE_API_KEY` to the `.env` file, but using environment variables is safer).*

### Step 5: The Quick Start Script (Recommended)
We have included a `start.sh` script to run both the backend and frontend simultaneously. Make it executable and run it:
```bash
chmod +x start.sh
./start.sh
```
The app will be live at `http://localhost:8501`.

*(Alternatively, you can run them manually in two separate terminals using `uvicorn app:app --port 8000` in the backend and `streamlit run app.py` in the frontend).*

---

## 📁 Project Structure & Code Links

```text
Women_Safety_Analytics/
├── start.sh                      # Bash script to run both servers
├── backend/
│   ├── app.py                    # FastAPI Entry Point
│   ├── routes/                   # API Endpoints
│   │   ├── predict.py            # Risk prediction
│   │   ├── heatmap.py            # Heatmap data
│   │   └── trends.py             # Trend data
│   └── utils/
│       └── model_loader.py       # Loads .pkl models
├── frontend/
│   ├── app.py                    # Main Streamlit App
│   ├── heatmap.py                # Folium Heatmap Component
│   ├── charts.py                 # Plotly Charts Component
│   ├── insights.py               # Instant Pandas data logic
│   ├── news.py                   # GNews API integration
│   └── sos.py                    # TextBee SMS logic
├── data/                         # Raw and Processed CSVs
├── models/                       # Saved .pkl models
├── notebooks/                    # Data exploration and training
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/predict` | Predict risk level from `state_code` + `district_code` |
| `GET` | `/trends` | Yearly trends (optional `?district_name=Jaipur`) |
| `GET` | `/categories` | Crime type breakdown (optional `?district_name=Jaipur`) |
| `GET` | `/heatmap-data` | District-wise data with lat/lng for the map |

---

## 🚧 Future Scope

- **WhatsApp Alerts:** Add WhatsApp integration for SOS alongside SMS.
- **React Frontend:** Migrate from Streamlit to React for a more native mobile feel.
- **Database Storage:** Move from session-state to PostgreSQL to permanently save user profiles and emergency contacts.
- **Street Lighting Data:** Integrate municipal data to score risk based on infrastructure.

---

## 👤 Author

**Sakshi**
Final-Year CSE (AI/ML) Project
GitHub: [@Sakshi-zz](https://github.com/Sakshi-zz)
