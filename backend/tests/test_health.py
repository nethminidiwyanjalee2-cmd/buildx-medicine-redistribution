"""
Tests for GET /api/health endpoint.

Phase 0 — verifies the endpoint exists, returns HTTP 200, and the response
body contains all required fields with correct types and values.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200():
    """GET /api/health must return HTTP 200."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_response_is_json():
    """Response must be valid JSON."""
    response = client.get("/api/health")
    # TestClient raises if Content-Type is not JSON; this also validates parsing.
    data = response.json()
    assert isinstance(data, dict)


def test_health_status_is_ok():
    """'status' field must equal 'ok'."""
    data = client.get("/api/health").json()
    assert data["status"] == "ok"


def test_health_has_version():
    """'version' field must be a non-empty string."""
    data = client.get("/api/health").json()
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0


def test_health_has_phase():
    """'phase' field must be a non-negative integer."""
    data = client.get("/api/health").json()
    assert isinstance(data["phase"], int)
    assert data["phase"] >= 0


def test_health_has_db_mode():
    """'db_mode' field must be one of the recognised modes."""
    data = client.get("/api/health").json()
    assert data["db_mode"] in ("firestore", "json_fallback", "unavailable")


def test_health_has_disclaimer():
    """'disclaimer' field must contain the exact required text."""
    expected = "Decision-support prototype using simulated data. Not for clinical use."
    data = client.get("/api/health").json()
    assert data["disclaimer"] == expected


def test_health_phase0_db_mode_is_json_fallback():
    """In Phase 0 (no credentials configured) db_mode must be 'json_fallback'."""
    data = client.get("/api/health").json()
    assert data["db_mode"] == "json_fallback"
