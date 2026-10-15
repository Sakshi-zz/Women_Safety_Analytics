from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import predict, trends, categories, heatmap

app = FastAPI(
    title="Women Safety Analytics API",
    description="Risk prediction and analytics for women's safety in India",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, tags=["Risk Prediction"])
app.include_router(trends.router, tags=["Trends"])
app.include_router(categories.router, tags=["Categories"])
app.include_router(heatmap.router, tags=["Heatmap"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "message": "Women Safety Analytics API is live",
        "docs": "Visit /docs for interactive API documentation",
    }