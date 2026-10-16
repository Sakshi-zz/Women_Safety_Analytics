from fastapi import APIRouter
from utils.model_loader import district_data, feature_cols

router = APIRouter()


@router.get("/categories")
def categories(district_name: str = None):
    """
    Returns crime type breakdown.
    If district_name is provided, returns only that district's totals.
    """
    df = district_data
    if district_name:
        df = df[df["district_name"].str.lower() == district_name.lower()]

    if df.empty:
        return {"categories": [], "counts": [], "scope": "unknown"}

    totals = {}
    for col in feature_cols:
        totals[col] = int(df[col].sum())

    sorted_categories = dict(
        sorted(totals.items(), key=lambda x: x[1], reverse=True)[:5]
    )
    return {
        "categories": list(sorted_categories.keys()),
        "counts": list(sorted_categories.values()),
        "scope": district_name or "All India",
    }