from fastapi import FastAPI
import uvicorn
from scanner import CostScanner

app = FastAPI()
scanner = CostScanner()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan")
def run_scan():
    scanner.run_scan()
    return {"status": "scan triggered"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
