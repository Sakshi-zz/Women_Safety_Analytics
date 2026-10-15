from fastapi import APIRouter
from utils.model_loader import district_data, feature_cols

router = APIRouter()


@router.get("/categories")
def categories():
    category_totals = {}
    for col in feature_cols:
        category_totals[col] = int(district_data[col].sum())

    sorted_categories = dict(
        sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    )
    return {
        "categories": list(sorted_categories.keys()),
        "counts": list(sorted_categories.values()),
    }
