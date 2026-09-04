"""API integration tests verifying validation, error formats, and endpoints."""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.model_service import model_service

client = TestClient(app)


def test_missing_fields_validation_error():
    """Verify that omitting required fields returns 422 with clean structured JSON."""
    incomplete_payload = {
        "age": 30,
        "income": 50000
    }
    response = client.post("/api/v1/risk-assessment", json=incomplete_payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "loan_amount" in data["error"]["message"] or "Field required" in data["error"]["message"]


def test_negative_age_validation_error():
    """Verify that negative age is rejected by Pydantic gt=0."""
    invalid_payload = {
        "age": -5,
        "income": 50000,
        "loan_amount": 40000,
        "credit_score": 650,
        "months_employed": 36,
        "num_credit_lines": 3,
        "interest_rate": 10.0,
        "loan_term": 36,
        "dti_ratio": 0.30,
        "education": "Bachelor's",
        "employment_type": "Full-time",
        "marital_status": "Single",
        "has_mortgage": False,
        "has_dependents": False,
        "loan_purpose": "Home",
        "has_cosigner": False
    }
    response = client.post("/api/v1/risk-assessment", json=invalid_payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_zero_loan_amount_validation_error():
    """Verify that loan_amount <= 0 is rejected."""
    invalid_payload = {
        "age": 30,
        "income": 50000,
        "loan_amount": 0,
        "credit_score": 650,
        "months_employed": 36,
        "num_credit_lines": 3,
        "interest_rate": 10.0,
        "loan_term": 36,
        "dti_ratio": 0.30,
        "education": "Bachelor's",
        "employment_type": "Full-time",
        "marital_status": "Single",
        "has_mortgage": False,
        "has_dependents": False,
        "loan_purpose": "Home",
        "has_cosigner": False
    }
    response = client.post("/api/v1/risk-assessment", json=invalid_payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_boolean_fields_handling():
    """Verify booleans are parsed accurately without crashing."""
    valid_payload = {
        "age": 30,
        "income": 50000,
        "loan_amount": 40000,
        "credit_score": 650,
        "months_employed": 36,
        "num_credit_lines": 3,
        "interest_rate": 10.0,
        "loan_term": 36,
        "dti_ratio": 0.30,
        "education": "Bachelor's",
        "employment_type": "Full-time",
        "marital_status": "Single",
        "has_mortgage": True,
        "has_dependents": True,
        "loan_purpose": "Home",
        "has_cosigner": True
    }
    response = client.post("/api/v1/risk-assessment", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "risk_assessment" in data
    assert "alternative_credit_indicators" in data


def test_unknown_categorical_values():
    """Verify that unseen categorical values are handled gracefully via handle_unknown='ignore'."""
    unseen_cat_payload = {
        "age": 32,
        "income": 65000,
        "loan_amount": 30000,
        "credit_score": 710,
        "months_employed": 48,
        "num_credit_lines": 2,
        "interest_rate": 8.5,
        "loan_term": 24,
        "dti_ratio": 0.25,
        "education": "Post-Doctorate Unknown",
        "employment_type": "Freelance Consultant",
        "marital_status": "Domestic Partnership",
        "has_mortgage": False,
        "has_dependents": False,
        "loan_purpose": "Solar Panels",
        "has_cosigner": False
    }
    response = client.post("/api/v1/risk-assessment", json=unseen_cat_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "risk_assessment" in data
    assert 0.0 <= data["risk_assessment"]["default_probability"] <= 1.0


def test_model_info_endpoint():
    response = client.get("/api/v1/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "Enhanced Random Forest"
    assert data["status"] == "ready"


def test_explanation_endpoint():
    payload = {
        "age": 30,
        "income": 50000,
        "loan_amount": 40000,
        "credit_score": 650,
        "months_employed": 36,
        "num_credit_lines": 3,
        "interest_rate": 10.0,
        "loan_term": 36,
        "dti_ratio": 0.30,
        "education": "Bachelor's",
        "employment_type": "Full-time",
        "marital_status": "Single",
        "has_mortgage": False,
        "has_dependents": False,
        "loan_purpose": "Home",
        "has_cosigner": False
    }
    response = client.post("/api/v1/risk-assessment/explanation", json=payload)
    assert response.status_code == 200
    factors = response.json()
    assert isinstance(factors, list)
    if len(factors) > 0:
        assert "feature" in factors[0]
        assert "impact" in factors[0]
        assert "value" in factors[0]
