"""Unit tests for risk evaluation logic and model inference behavior."""

import pytest
from app.services.risk_service import risk_service
from app.services.model_service import model_service


def test_risk_evaluation_eligible():
    res = risk_service.evaluate_risk(probability=0.20, threshold=0.47)
    assert res.prediction == 0
    assert res.risk_classification == "LOW RISK"
    assert res.recommended_action == "ELIGIBLE"
    assert res.default_probability == 0.20


def test_risk_evaluation_manual_review():
    res = risk_service.evaluate_risk(probability=0.3928, threshold=0.47)
    assert res.prediction == 0
    assert res.risk_classification == "LOW RISK"
    assert res.recommended_action == "MANUAL REVIEW"
    assert res.default_probability == 0.3928


def test_risk_evaluation_high_risk_at_threshold():
    res = risk_service.evaluate_risk(probability=0.47, threshold=0.47)
    assert res.prediction == 1
    assert res.risk_classification == "HIGH RISK"
    assert res.recommended_action == "HIGH RISK - FURTHER REVIEW"


def test_risk_evaluation_high_risk_above_threshold():
    res = risk_service.evaluate_risk(probability=0.75, threshold=0.47)
    assert res.prediction == 1
    assert res.risk_classification == "HIGH RISK"
    assert res.recommended_action == "HIGH RISK - FURTHER REVIEW"


def test_model_service_state():
    """Verify model service exposes is_ready and default threshold."""
    assert hasattr(model_service, "is_ready")
    assert hasattr(model_service, "threshold")
    assert isinstance(model_service.threshold, (int, float))
