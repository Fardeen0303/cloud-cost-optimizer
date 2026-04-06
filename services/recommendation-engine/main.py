from fastapi import FastAPI
import uvicorn
from engine import RecommendationEngine

app = FastAPI()
engine = RecommendationEngine()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def run_analysis():
    engine.analyze_resources()
    return {"status": "analysis triggered"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
