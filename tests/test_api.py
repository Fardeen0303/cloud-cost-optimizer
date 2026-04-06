import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'api-gateway'))

# Mock psycopg2 before importing main
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()

import jwt as pyjwt
from main import app, create_token

client = TestClient(app)


def auth_headers():
    token = create_token("admin")
    return {"Authorization": f"Bearer {token}"}


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_login_invalid_credentials():
    res = client.post("/auth/login", json={"username": "wrong", "password": "wrong"})
    assert res.status_code == 401


def test_resources_requires_auth():
    res = client.get("/resources")
    assert res.status_code in (401, 403)


def test_recommendations_requires_auth():
    res = client.get("/recommendations")
    assert res.status_code in (401, 403)


@patch("main.get_db")
def test_get_resources_authenticated(mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_db.return_value = mock_conn

    res = client.get("/resources", headers=auth_headers())
    assert res.status_code == 200
    assert "resources" in res.json()
