"""
Backend API tests using FastAPI TestClient with an isolated in-memory
SQLite database — does NOT touch your real backend/geoai.db.

Run with: pytest tests/test_backend_api.py -v
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
import models
import main

# --- Isolated in-memory test database ---
# StaticPool forces a single shared connection, otherwise each new
# connection to ":memory:" gets its own empty database.
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


main.app.dependency_overrides[database.get_db] = override_get_db
client = TestClient(main.app)


def test_root_returns_ok():
    """Sanity check: the API is alive and responds."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_add_source_returns_created_source():
    """POSTing a valid source should return it back with an assigned id."""
    response = client.post("/sources", json={
        "name": "Test Source",
        "source_type": "citizen_report",
        "raw_content": "Heavy flooding reported",
        "latitude": 22.5726,
        "longitude": 88.3639,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Source"
    assert "id" in data


def test_get_nonexistent_source_returns_404():
    """Fetching a source ID that doesn't exist should return 404, not crash."""
    response = client.get("/sources/999999")
    assert response.status_code == 404


def test_generate_insight_from_valid_source():
    """Creating a source then generating an insight from it should return real AI scores."""
    source_res = client.post("/sources", json={
        "name": "Flood Report",
        "source_type": "citizen_report",
        "raw_content": "Water rising near the embankment",
        "latitude": 22.57,
        "longitude": 88.36,
    })
    source_id = source_res.json()["id"]

    insight_res = client.post(
        "/insights/generate",
        params={"title": "Test Insight", "summary": "Test summary"},
        json=[source_id],
    )
    assert insight_res.status_code == 200
    data = insight_res.json()
    assert "confidence_score" in data
    assert "explanation" in data
    assert data["title"] == "Test Insight"


def test_generate_insight_with_no_matching_sources_returns_404():
    """Requesting an insight for source IDs that don't exist should 404, not crash."""
    response = client.post(
        "/insights/generate",
        params={"title": "Bad Insight", "summary": "Should fail"},
        json=[999999],
    )
    assert response.status_code == 404


def test_low_confidence_insight_creates_alert():
    """A low-confidence insight (single weak source) should auto-generate a warning alert."""
    source_res = client.post("/sources", json={
        "name": "Weak Report",
        "source_type": "user_report",
        "raw_content": "possible flooding",
        "latitude": 22.6,
        "longitude": 88.4,
    })
    source_id = source_res.json()["id"]

    client.post(
        "/insights/generate",
        params={"title": "Weak Insight", "summary": "Should trigger alert"},
        json=[source_id],
    )

    alerts_res = client.get("/alerts")
    assert alerts_res.status_code == 200
    assert len(alerts_res.json()) >= 1


def test_health_ai_endpoint_reports_ai_module_status():
    """The /health/ai endpoint should confirm whether the real AI module is wired in."""
    response = client.get("/health/ai")
    assert response.status_code == 200
    assert "ai_module_connected" in response.json()
