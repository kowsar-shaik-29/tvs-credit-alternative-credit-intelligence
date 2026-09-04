"""Unit tests for /health and root status endpoints."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "docs" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "preprocessor_loaded" in data
    assert "threshold_loaded" in data
    assert isinstance(data["model_loaded"], bool)
    assert isinstance(data["preprocessor_loaded"], bool)
    assert isinstance(data["threshold_loaded"], bool)
