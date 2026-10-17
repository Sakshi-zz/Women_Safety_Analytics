from fastapi import APIRouter
from utils.model_loader import district_data

router = APIRouter()

@router.get("/heatmap-data")
def heatmap_data(year: int = 2023):
    # Filter by year
    year_data = district_data[district_data["year"] == year].copy()

    # Drop rows missing coordinates
    if "latitude" in year_data.columns and "longitude" in year_data.columns:
        year_data = year_data.dropna(subset=["latitude", "longitude"])
    
    # Sort by severity
    year_data = year_data.sort_values("severity_score", ascending=False)

    # Convert NaN to None so JSON can serialize it properly
    year_data = year_data.where(year_data.notnull(), None)

    return {
        "year": year,
        "count": len(year_data),
        "districts": year_data[[
            "district_name", "state_name", "state_code",
            "district_code", "total_crimes", "severity_score",
            "latitude", "longitude",
        ]].to_dict(orient="records")
    }