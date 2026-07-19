"""
Basic smoke test for the /health endpoint. Run with:
    pytest tests/test_health.py

Note: requires DATABASE_URL to point at a reachable Postgres (or swap
to sqlite:///./test.db in .env for a quick local check without Docker).
"""
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "app" in body
