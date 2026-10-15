from fastapi import APIRouter
from utils.model_loader import yearly_trends

router = APIRouter()


@router.get("/trends")
def trends():
    data = yearly_trends.to_dict(orient="records")
    return {
        "years": [int(row["year"]) for row in data],
        "total_crimes": [int(row["total_crimes"]) for row in data],
        "severity_score": [int(row["severity_score"]) for row in data],
    }