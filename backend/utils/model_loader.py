import os
import joblib
import pandas as pd

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "processed")

# ---------- Load once at import time ----------
risk_model = joblib.load(os.path.join(MODELS_DIR, "risk_model.pkl"))
feature_cols = joblib.load(os.path.join(MODELS_DIR, "feature_cols.pkl"))
district_data = pd.read_csv(os.path.join(DATA_DIR, "district_level_data.csv"))

# Precompute yearly trends
yearly_trends = district_data.groupby("year").agg({
    "total_crimes": "sum",
    "severity_score": "sum"
}).reset_index()

print("✅ All models and data loaded")