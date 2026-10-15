from fastapi import APIRouter
from utils.model_loader import district_data

router = APIRouter()


@router.get("/heatmap-data")
def heatmap_data(year: int = 2023):
    year_data = district_data[district_data["year"] == year].copy()
    year_data = year_data.sort_values("severity_score", ascending=False)

    return {
        "year": year,
        "districts": year_data[[
            "district_name", "state_name", "state_code",
            "district_code", "total_crimes", "severity_score"
        ]].to_dict(orient="records")
    }