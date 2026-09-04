"""Automated unit and integration tests for the TVS Credit NIRNAY extension layer."""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.schemas.risk import RiskAssessmentRequest
from app.services.alternative_data_service import alternative_data_service
from app.services.digital_twin_service import digital_twin_service
from app.services.stress_service import stress_service
from app.services.recommendation_service import recommendation_service
from app.services.resilience_service import resilience_service
from app.services.assistant_service import assistant_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_request():
    return RiskAssessmentRequest(
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


def test_default_consents_structure():
    """Verify standard 7 consent items are loaded with proper fields."""
    consents = alternative_data_service.get_default_consents()
    assert len(consents) == 7
    source_ids = [c.source_id for c in consents]
    assert "bank_cash_flow" in source_ids
    assert "upi_digital" in source_ids
    assert "utility_payments" in source_ids
    assert "mobile_bill" in source_ids
    assert "gst_business" in source_ids
    assert "tvs_repayment" in source_ids
    assert "uploaded_docs" in source_ids
    for c in consents:
        assert c.is_simulated is True
        assert len(c.purpose) > 10


def test_alternative_data_generation(sample_request):
    """Verify alternative data profile generation and score bounds."""
    profile = alternative_data_service.generate_alternative_profile(sample_request)
    assert profile.customer_id is not None
    assert profile.bank_cash_flow is not None
    assert profile.upi_digital is not None
    assert profile.utility_history is not None
    assert profile.telecom_history is not None

    scores = profile.scores
    for val in [
        scores.payment_discipline,
        scores.income_stability,
        scores.cash_flow_stability,
        scores.utility_discipline,
        scores.digital_payment_discipline,
        scores.employment_stability,
        scores.debt_burden,
        scores.financial_resilience
    ]:
        assert 0 <= val <= 100


def test_consent_withdrawal_masking(sample_request):
    """Verify that withdrawing consent masks corresponding data source."""
    consents = alternative_data_service.get_default_consents()
    # Withdraw bank_cash_flow
    for c in consents:
        if c.source_id == "bank_cash_flow":
            c.consent_granted = False

    profile = alternative_data_service.generate_alternative_profile(sample_request, consents=consents)
    assert profile.bank_cash_flow is None
    # other sources remain available
    assert profile.upi_digital is not None
    assert profile.utility_history is not None


def test_digital_twin_generation(sample_request):
    """Verify Financial Digital Twin dimension matrix and grounded narrative."""
    profile = alternative_data_service.generate_alternative_profile(sample_request)
    twin = digital_twin_service.build_digital_twin(sample_request, profile)

    assert len(twin.dimensions) >= 8
    assert 0 <= twin.twin_stability_index <= 100
    assert len(twin.ai_grounded_summary) > 20
    assert len(twin.strengths) >= 1
    assert len(twin.vulnerabilities) >= 1


def test_stress_testing_scenarios(sample_request):
    """Verify 7 stress testing shock scenarios."""
    profile = alternative_data_service.generate_alternative_profile(sample_request)
    stress = stress_service.run_stress_test(sample_request, profile)

    assert len(stress.scenarios) == 7
    scenario_ids = [s.scenario_id for s in stress.scenarios]
    assert "scenario_inc_minus_10" in scenario_ids
    assert "scenario_inc_minus_20" in scenario_ids
    assert "scenario_inc_minus_30" in scenario_ids
    assert "scenario_exp_plus_10" in scenario_ids
    assert "scenario_exp_plus_20" in scenario_ids
    assert "scenario_missed_payment" in scenario_ids
    assert "scenario_income_interruption" in scenario_ids

    # Severity ordering: -30% income must have lower resilience than -10% income
    s_minus_10 = next(s for s in stress.scenarios if s.scenario_id == "scenario_inc_minus_10")
    s_minus_30 = next(s for s in stress.scenarios if s.scenario_id == "scenario_inc_minus_30")
    assert s_minus_30.resilience_score < s_minus_10.resilience_score


def test_responsible_loan_recommendation(sample_request):
    """Verify responsible loan recommendation constraints."""
    profile = alternative_data_service.generate_alternative_profile(sample_request)
    rec = recommendation_service.recommend_loan(sample_request, profile, default_prob=0.3933)

    assert rec.recommended_loan > 0
    assert rec.max_comfortable_loan > 0
    assert rec.estimated_emi > 0
    assert rec.recommended_tenure_months in [12, 24, 36, 48, 60]
    assert rec.affordability_status in ["Comfortable", "Manageable", "Strained"]


def test_nirnay_financial_assistant_queries(sample_request):
    """Verify assistant answers the 5 core customer questions accurately."""
    profile = alternative_data_service.generate_alternative_profile(sample_request)
    rec = recommendation_service.recommend_loan(sample_request, profile, default_prob=0.3933)
    res = resilience_service.calculate_resilience(sample_request, profile.scores)

    questions = [
        "Why was my risk classified this way?",
        "How can I improve my eligibility?",
        "How much loan can I comfortably afford?",
        "What happens if my income decreases?",
        "Why is my recommended loan lower than requested?"
    ]

    for q in questions:
        resp = assistant_service.answer_query(
            question=q,
            request=sample_request,
            alt_profile=profile,
            default_prob=0.3933,
            recommended_loan=rec.recommended_loan,
            resilience_score=res
        )
        assert len(resp.answer) > 30
        assert len(resp.suggested_followups) >= 2


def test_full_nirnay_assessment_api_endpoint(client, sample_request):
    """Test unified /api/v1/nirnay/full-assessment composite endpoint."""
    response = client.post("/api/v1/nirnay/full-assessment", json=sample_request.model_dump())
    assert response.status_code == 200
    data = response.json()

    assert "application_id" in data
    assert "risk_assessment" in data
    assert "alternative_scores" in data
    assert "digital_twin" in data
    assert "customer_friendly_factors" in data
    assert "stress_test" in data
    assert "loan_recommendation" in data
    assert "financial_health" in data
    assert "audit_record" in data
    assert data["risk_assessment"]["risk_threshold"] == 0.47
