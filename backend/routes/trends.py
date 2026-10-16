from fastapi import APIRouter
from utils.model_loader import district_data

router = APIRouter()


@router.get("/trends")
def trends(district_name: str = None):
    """
    Returns yearly trends.
    If district_name is provided, returns only that district's trend.
    Otherwise, returns nationwide.
    """
    df = district_data
    if district_name:
        df = df[df["district_name"].str.lower() == district_name.lower()]

    if df.empty:
        return {"years": [], "total_crimes": [], "severity_score": [], "scope": "unknown"}

    yearly = df.groupby("year").agg({
        "total_crimes": "sum",
        "severity_score": "sum",
    }).reset_index()

    return {
        "years": [int(row["year"]) for row in yearly.to_dict("records")],
        "total_crimes": [int(row["total_crimes"]) for row in yearly.to_dict("records")],
        "severity_score": [int(row["severity_score"]) for row in yearly.to_dict("records")],
        "scope": district_name or "All India",
    }