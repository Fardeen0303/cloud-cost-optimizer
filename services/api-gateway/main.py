from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI(title="Cost Optimizer API")

def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

@app.get("/")
def root():
    return {"message": "Cloud Cost Optimizer API"}

@app.get("/resources")
def get_resources():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scanned_resources ORDER BY scanned_at DESC LIMIT 100")
    resources = cur.fetchall()
    cur.close()
    conn.close()
    return {"resources": resources}

@app.get("/recommendations")
def get_recommendations():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM recommendations WHERE status='pending'")
    recommendations = cur.fetchall()
    cur.close()
    conn.close()
    return {"recommendations": recommendations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
