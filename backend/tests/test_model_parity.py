"""Regression test verifying parity with the Kaggle notebook's known customer output."""

import pytest
from app.schemas.risk import RiskAssessmentRequest
from app.services.feature_engineering import feature_engineering_service
from app.services.model_service import model_service
from app.services.risk_service import risk_service


def test_regression_known_customer_parity():
    """Known test customer from Kaggle notebook cell 65 (LoanID: I38PQUQS96)."""
    if not model_service.is_ready:
        model_service.load_artifacts()

    customer_request = RiskAssessmentRequest(
        age=30,
        income=50000.0,
        loan_amount=40000.0,
        credit_score=650,
        months_employed=36,
        num_credit_lines=3,
        interest_rate=10.0,
        loan_term=36,
        dti_ratio=0.30,
        education="Bachelor's",
        employment_type="Full-time",
        marital_status="Single",
        has_mortgage=False,
        has_dependents=False,
        loan_purpose="Home",
        has_cosigner=False
    )

    # Known ground truth from notebook cells 66, 68, 69
    EXPECTED_PROBABILITY = 0.3928
    EXPECTED_THRESHOLD = 0.47
    EXPECTED_PREDICTION = 0
    EXPECTED_RISK_CLASS = "LOW RISK"
    EXPECTED_RECOMMENDATION = "MANUAL REVIEW"

    raw_df = feature_engineering_service.convert_api_to_dataframe(customer_request)
    df_featured, indicators = feature_engineering_service.engineer_features(raw_df)

    actual_probability = model_service.predict_default_probability(df_featured)
    evaluation = risk_service.evaluate_risk(actual_probability, model_service.threshold)

    # Probability match within 0.005
    assert abs(actual_probability - EXPECTED_PROBABILITY) < 0.005
    assert evaluation.prediction == EXPECTED_PREDICTION
    assert evaluation.risk_classification == EXPECTED_RISK_CLASS
    assert evaluation.recommended_action == EXPECTED_RECOMMENDATION
    assert abs(indicators.financial_stability_score - 0.4726) < 0.005
    assert abs(indicators.repayment_capacity - 0.8750) < 0.005
