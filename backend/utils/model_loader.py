import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "processed")

print("⏳ Loading models and data...")

try:
    risk_model = joblib.load(os.path.join(MODELS_DIR, "risk_model.pkl"))
    feature_cols = joblib.load(os.path.join(MODELS_DIR, "feature_cols.pkl"))
    district_data = pd.read_csv(os.path.join(DATA_DIR, "district_level_data.csv"))
    
    # Precompute yearly trends for fast API response
    yearly_trends = district_data.groupby("year").agg({
        "total_crimes": "sum",
        "severity_score": "sum"
    }).reset_index()

    print("✅ Models and data loaded successfully!")
    
    # Check coordinates
    if "latitude" not in district_data.columns:
        print("⚠️ WARNING: 'latitude' column missing from CSV! Heatmap will not work.")
    else:
        print(f"📍 Coordinates found: {district_data['latitude'].notna().sum()} rows have lat/lon.")

except Exception as e:
    print(f"❌ FATAL ERROR loading models/data: {e}")
    raise e