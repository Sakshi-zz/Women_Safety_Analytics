from fastapi import APIRouter
from pydantic import BaseModel
from utils.model_loader import risk_model, feature_cols, district_data

router = APIRouter()


class PredictionInput(BaseModel):
    year: int
    state_code: int
    district_code: int


@router.post("/predict")
def predict(input_data: PredictionInput):
    district_rows = district_data[
        (district_data["state_code"] == input_data.state_code) &
        (district_data["district_code"] == input_data.district_code)
    ]

    if district_rows.empty:
        return {"error": "District not found in dataset"}

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