from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI(
    title="Women Safety Analytics API",
    description="Risk prediction and analytics for women's safety in India",
    version="1.0"
)

# Allow the frontend to call this API from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Load models at startup ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

risk_model = joblib.load(os.path.join(MODELS_DIR, "risk_model.pkl"))
feature_cols = joblib.load(os.path.join(MODELS_DIR, "feature_cols.pkl"))
district_data = pd.read_csv(os.path.join(BASE_DIR, "..", "data", "processed", "/workspaces/Major_project/data/processed/district_level_data.csv.csv"))

print("✅ Models and data loaded")


# ---------- Request body for /predict ----------
class PredictionInput(BaseModel):
    year: int
    state_code: int
    district_code: int
    # Instead of asking the user for 42 crime columns, we'll pull them
    # from the most recent record of that district.


# ---------- Endpoints ----------
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Women Safety Analytics API is live",
        "docs": "Visit /docs for interactive API documentation"
    }


@app.post("/predict")
def predict(input_data: PredictionInput):
    # Find the district's latest crime profile
    district_rows = district_data[
        (district_data["state_code"] == input_data.state_code) &
        (district_data["district_code"] == input_data.district_code)
    ]

    if district_rows.empty:
        return {"error": "District not found in dataset"}

    # Use the most recent year's crime profile as the feature vector
    latest = district_rows.sort_values("year").iloc[-1]
    features = latest[feature_cols].values.reshape(1, -1)

    prediction = risk_model.predict(features)[0]
    probabilities = risk_model.predict_proba(features)[0]
    confidence = float(max(probabilities))

    return {
        "district": latest["district_name"],
        "state": latest["state_name"],
        "predicted_risk": prediction,
        "confidence": round(confidence, 3),
    }