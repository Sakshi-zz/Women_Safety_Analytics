from fastapi import APIRouter
from utils.model_loader import district_data

router = APIRouter()


@router.get("/heatmap-data")
def heatmap_data(year: int = 2023):
    """
    Returns district-level data with coordinates for the heatmap.
    """
    year_data = district_data[district_data["year"] == year].copy()

    # Only keep districts with coordinates
    year_data = year_data[year_data["latitude"].notna()]

    year_data = year_data.sort_values("severity_score", ascending=False)

    return {
        "year": year,
        "count": len(year_data),
        "districts": year_data[[
            "district_name", "state_name", "state_code",
            "district_code", "total_crimes", "severity_score",
            "latitude", "longitude",
        ]].to_dict(orient="records")
    }