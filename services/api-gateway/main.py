import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
import jwt as pyjwt
from passlib.context import CryptContext

sys.path.insert(0, '/app/notifier')
from notifier import alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cloud Cost Optimizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-me-in-production')
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


# --- DB ---

@contextmanager
def get_db():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    try:
        yield conn
    finally:
        conn.close()


# --- Auth ---

class LoginRequest(BaseModel):
    username: str
    password: str


USERS = {
    os.getenv('ADMIN_USER', 'admin'): pwd_context.hash(os.getenv('ADMIN_PASSWORD', 'changeme')[:72])
}


def create_token(username: str) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return pyjwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = pyjwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(body: LoginRequest):
    hashed = USERS.get(body.username)
    if not hashed or not pwd_context.verify(body.password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": create_token(body.username), "token_type": "bearer"}


@app.get("/resources")
def get_resources(user: str = Depends(verify_token)):
    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM scanned_resources ORDER BY scanned_at DESC LIMIT 100")
                resources = cur.fetchall()
        return {"resources": [dict(r) for r in resources]}
    except Exception as e:
        logger.error(f"Failed to fetch resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch resources")


@app.get("/recommendations")
def get_recommendations(user: str = Depends(verify_token)):
    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM recommendations WHERE status='pending'")
                recommendations = cur.fetchall()
        return {"recommendations": [dict(r) for r in recommendations]}
    except Exception as e:
        logger.error(f"Failed to fetch recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recommendations")


@app.post("/recommendations/{rec_id}/approve")
def approve_recommendation(rec_id: int, user: str = Depends(verify_token)):
    return _update_recommendation_status(rec_id, 'approved')


@app.post("/recommendations/{rec_id}/reject")
def reject_recommendation(rec_id: int, user: str = Depends(verify_token)):
    return _update_recommendation_status(rec_id, 'rejected')


def _update_recommendation_status(rec_id: int, new_status: str):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE recommendations SET status=%s WHERE id=%s RETURNING id, resource_id, potential_savings",
                    (new_status, rec_id)
                )
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Recommendation not found")
                row = cur.fetchone()
            conn.commit()

        resource_id, savings = row[1], row[2]
        if new_status == 'approved':
            alert(
                title="✅ Recommendation Approved",
                message=f"Recommendation #{rec_id} for resource `{resource_id}` approved. Expected savings: *${savings}/mo*",
                level="info"
            )
        elif new_status == 'rejected':
            alert(
                title="❌ Recommendation Rejected",
                message=f"Recommendation #{rec_id} for resource `{resource_id}` was rejected.",
                level="warning"
            )

        return {"id": rec_id, "status": new_status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update recommendation {int(rec_id)}: {str(e)!r}")
        raise HTTPException(status_code=500, detail="Failed to update recommendation")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
