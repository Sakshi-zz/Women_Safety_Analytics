# 🛡️ Women Safety Analytics & Risk Prediction System

An **end-to-end machine learning system** that predicts women's safety risk across Indian districts and visualizes crime hotspots on an interactive map.

Built as a final-year CSE (AI/ML) project using real NCRB crime data (2017–2023).

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Dataset](#-dataset)
- [Machine Learning Models](#-machine-learning-models)
- [Installation & Setup](#-installation--setup)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Future Scope](#-future-scope)
- [Author](#-author)

---

## 🎯 Overview

Women in India often lack accessible, data-driven tools to assess the safety of different areas. Crime statistics exist in government reports but are buried in PDFs and not actionable for everyday decisions.

This project bridges that gap by providing:

- A **district-level heatmap** showing crime severity across India.
- A **risk prediction model** that classifies districts as High / Medium / Low risk.
- **Interactive charts** showing crime trends and category breakdowns.
- An **emergency SOS feature** for logging alerts with location.
- **Geolocation-aware** features to find nearby high-risk zones.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗺️ **Interactive Heatmap** | Folium-based map with red/yellow/green hotspots over high-crime districts |
| 🔮 **Risk Prediction** | Random Forest model (88.6% F1) predicts next year's risk level |
| 📈 **Incident Trends** | Time-series visualization of yearly crime patterns (2017–2023) |
| 🍩 **Category Breakdown** | Donut chart of the top 5 crime types per district |
| 📍 **District Search** | User selects their district by name — no need to know lat/lon |
| 🚨 **SOS Alerts** | Logs emergency alerts with timestamp + GPS to a JSON store |
| 🌐 **GPS Location** | Optional browser geolocation for personal risk view |
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
│  /predict  /trends  /categories  /heatmap-data  /sos     │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  FRONTEND (Streamlit + Folium + Plotly)                  │
│  Dashboard  |  Charts  |  Heatmap  |  SOS                │
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
- **Performance:**
  - **Accuracy:** 88.56%
  - **F1 Score (weighted):** 88.60%
  - **Precision:** 0.85 – 0.94
  - **Recall:** 0.87 – 0.89

### 2. Prophet — Time-Series Forecasting

- **Target:** Yearly severity score (2017–2023).
- **Forecast:** 2024, 2025.
- **Output:** ~2.9M → 3.0M (rising trend).
- **Visualization:** [View Prophet Forecast Chart](reports/prophet_forecast.png)

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- pip

### Step 1: Clone the repo
```bash
git clone https://github.com/Sakshi-zz/Major_project.git
cd Major_project
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the backend
```bash
cd backend
uvicorn app:app --reload --port 8000
```
Backend will be live at `http://localhost:8000`.
Interactive API docs: `http://localhost:8000/docs`

### Step 4: Run the frontend
In a new terminal:
```bash
cd frontend
streamlit run app.py --server.port 8501
```
Frontend will be live at `http://localhost:8501`.

---

## 📁 Project Structure & Code Links

Click the links below to view the code directly:

```text
Major_project/
├── backend/
│   ├── app.py                    # [FastAPI Entry Point](backend/app.py)
│   ├── routes/                   # [API Endpoints Folder](backend/routes/)
│   │   ├── predict.py            # Risk prediction endpoint
│   │   ├── heatmap.py            # Heatmap data endpoint
│   │   ├── trends.py             # Trend data endpoint
│   │   └── sos.py                # SOS alert endpoint
│   └── utils/
│       └── model_loader.py       # Loads .pkl models
├── frontend/
│   ├── app.py                    # [Main Streamlit App](frontend/app.py)
│   ├── heatmap.py                # [Folium Heatmap Component](frontend/heatmap.py)
│   └── charts.py                 # [Plotly Charts Component](frontend/charts.py)
├── data/
│   ├── raw/                      # Original NCRB CSV
│   └── processed/                # Cleaned CSV with lat/lng
├── models/                       # Saved .pkl models
├── notebooks/
│   ├── 01_data_exploration.ipynb # [Data Cleaning Notebook](notebooks/01_data_exploration.ipynb)
│   └── 02_model_training.ipynb   # [ML Training Notebook](notebooks/02_model_training.ipynb)
├── scripts/
│   └── geocode_districts.py      # Geocoding script
├── reports/                      # Forecast charts
├── .streamlit/
│   └── config.toml               # Dark theme config
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
| `POST` | `/sos` | Log an emergency alert with location |

---

## 🚧 Future Scope

- **Real SMS/WhatsApp alerts** via Twilio when SOS is triggered.
- **React frontend** to match the design mockup more closely.
- **Live crime news feed** scraped from local news sources.
- **Mobile app** (React Native) with background GPS tracking.
- **District-level street lighting data** for contextual risk scoring.

---

## 👤 Author

**Sakshi**
Final-Year CSE (AI/ML) Project
- GitHub: [@Sakshi-zz](https://github.com/Sakshi-zz)
