"""Unit and integration tests for NIRNAY 2.5 Hackathon-Grade Enhancement Features."""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.schemas.risk import RiskAssessmentRequest
from app.services.simulation_service import simulation_service
from app.services.passport_service import passport_service
from app.services.fairness_service import fairness_service
from app.services.alternative_data_service import alternative_data_service
from app.services.recommendation_service import recommendation_service
from app.services.monitoring_service import monitoring_service


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


@pytest.fixture
def stressed_request():
    return RiskAssessmentRequest(
        age=29,
        income=28000.0,
        loan_amount=65000.0,
        credit_score=420,
        months_employed=12,
        num_credit_lines=5,
        interest_rate=16.0,
        loan_term=36,
        dti_ratio=0.78,
        education="High School",
        employment_type="Part-time",
        marital_status="Single",
        has_mortgage=False,
        has_dependents=False,
        loan_purpose="Other",
        has_cosigner=False
    )


# 1. WHAT-IF LOAN SIMULATOR
def test_what_if_simulator_service(sample_request):
    alt_profile = alternative_data_service.generate_alternative_profile(sample_request)
    sim_resp = simulation_service.simulate_what_if(
        current_request=sample_request,
        simulated_loan_amount=25000.0,
        simulated_loan_term=24,
        simulated_interest_rate=9.5,
        alt_profile=alt_profile,
        default_prob=0.3928
    )
    assert sim_resp.current_option.loan_amount == 40000.0
    assert sim_resp.simulated_option.loan_amount == 25000.0
    assert sim_resp.simulated_option.loan_term == 24
    assert sim_resp.is_decision_support_only is True
    assert "Decision-support simulation" in sim_resp.disclaimer
    assert len(sim_resp.comparison_verdict) > 10


def test_what_if_simulator_endpoint(client, sample_request):
    payload = {
        "current_request": sample_request.model_dump(),
        "simulated_loan_amount": 30000.0,
        "simulated_loan_term": 24,
        "simulated_interest_rate": 10.0
    }
    resp = client.post("/api/v1/simulator/what-if", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "current_option" in data
    assert "simulated_option" in data
    assert "recommended_safer_option" in data
    assert data["simulated_option"]["loan_amount"] == 30000.0


# 2. SECOND CHANCE / RESPONSIBLE BORROWING
def test_second_chance_on_suitable_customer(sample_request):
    sample_request.loan_amount = 10000.0
    alt_profile = alternative_data_service.generate_alternative_profile(sample_request)
    rec = recommendation_service.recommend_loan(sample_request, alt_profile, 0.28)
    sc = recommendation_service.generate_second_chance(sample_request, alt_profile, 0.28, rec)
    assert sc.is_suitable_at_requested_terms is True
    assert "Suitable at requested terms" in sc.status_label


def test_second_chance_on_unsuitable_customer(stressed_request):
    alt_profile = alternative_data_service.generate_alternative_profile(stressed_request)
    rec = recommendation_service.recommend_loan(stressed_request, alt_profile, 0.65)
    sc = recommendation_service.generate_second_chance(stressed_request, alt_profile, 0.65, rec)
    assert sc.is_suitable_at_requested_terms is False
    assert "Not suitable at requested terms" in sc.status_label
    assert sc.recommended_amount < stressed_request.loan_amount
    assert len(sc.reason_for_recommendation) > 15
    assert len(sc.main_risk_factor) > 10
    assert len(sc.main_positive_factor) > 10


# 3. CREDIT IMPROVEMENT ROADMAP
def test_credit_improvement_endpoint(client, sample_request):
    resp = client.post("/api/v1/simulator/credit-improvement", json=sample_request.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert "improvement_levers" in data
    assert len(data["improvement_levers"]) >= 3
    assert 0 <= data["overall_readiness_score"] <= 100
    assert "Illustrative simulation" in data["illustrative_disclaimer"]


# 4. FINANCIAL HEALTH PASSPORT & EVIDENCE CONFIDENCE
def test_passport_and_evidence_confidence(client, sample_request):
    resp = client.post("/api/v1/nirnay/full-assessment", json=sample_request.model_dump())
    assert resp.status_code == 200
    data = resp.json()

    # Passport
    passport = data.get("passport")
    assert passport is not None
    assert passport["overall_health_status"] in ["HEALTHY", "STABLE", "WATCH"]
    assert 0 <= passport["income_stability_score"] <= 100
    assert 0 <= passport["payment_discipline_score"] <= 100
    assert 0 <= passport["repayment_capacity_score"] <= 100
    assert 0 <= passport["financial_resilience_score"] <= 100
    assert passport["data_minimization_verified"] is True

    # Evidence Confidence
    ev = data.get("evidence_confidence")
    assert ev is not None
    assert 0 <= ev["evidence_confidence_score"] <= 100
    assert ev["label"] == "NIRNAY Evidence Confidence"
    assert len(ev["strong_evidence"]) >= 1

    # Second Chance
    sc = data.get("second_chance")
    assert sc is not None

    # Health Timeline
    ht = data.get("health_timeline")
    assert ht is not None
    assert len(ht["milestones"]) == 4

    # Consent Intelligence
    ci = data.get("consent_intelligence")
    assert ci is not None
    assert len(ci["sources"]) == 7


# 5. FAIRNESS & RESPONSIBLE LENDING ANALYST METRICS
def test_fairness_metrics_endpoint(client):
    resp = client.get("/api/v1/analyst/fairness-metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_applications_evaluated"] > 1000
    assert 0 < data["approval_rate"] < 100
    assert 0 < data["first_time_borrower_inclusion_rate"] < 100
    assert "Raw sensitive bank/UPI information is never exposed" in data["disclaimer"]


# 6. HUMAN-IN-THE-LOOP REVIEW
def test_human_in_the_loop_review_override(client):
    review_payload = {
        "application_id": "TVS-APP-TEST01",
        "customer_id": "TVS-CUST-TEST01",
        "decision": "Approve",
        "override_reason": "Verified offline immovable asset and seasonal Kirana inventory",
        "analyst_role": "Senior Credit Officer",
        "analyst_notes": "Exception granted under TVS Rural Empowerment circular"
    }
    resp = client.post("/api/v1/analyst/human-review", json=review_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["analyst_decision"] == "Approve"
    assert data["override_reason"] == review_payload["override_reason"]
    assert data["is_override"] is True
    assert "Audit Trail Updated" in data["audit_status"]


# 7. AI FINANCIAL COACH
def test_financial_coach_query_endpoint(client, sample_request):
    coach_payload = {
        "question": "How can I improve my financial health?",
        "application_data": sample_request.model_dump()
    }
    resp = client.post("/api/v1/coach/query", json=coach_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["answer"]) > 30
    assert len(data["actionable_steps"]) >= 2
    assert "NIRNAY AI Financial Coach" in data["disclaimer"]


# 8. NIRNAY 7 SPECIALIZED AGENTS STATUS
def test_agent_system_status_endpoint(client):
    resp = client.get("/api/v1/agents/status")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["specialized_agents"]) == 7
    agent_names = [a["name"] for a in data["specialized_agents"]]
    assert "Credit Assessment Agent" in agent_names
    assert "Affordability Agent" in agent_names
    assert "Resilience Agent" in agent_names
    assert "Recommendation Agent" in agent_names
    assert "Financial Coach Agent" in agent_names
    assert "Monitoring Agent" in agent_names
    assert "Compliance & Audit Agent" in agent_names
