"""Pydantic schemas for TVS Credit NIRNAY Hackathon-Grade Enhancement Features."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.schemas.risk import RiskAssessmentRequest


# =========================================================================
# FEATURE 1: WHAT-IF LOAN SIMULATOR
# =========================================================================

class WhatIfSimulationRequest(BaseModel):
    current_request: RiskAssessmentRequest
    simulated_loan_amount: float = Field(..., ge=1000, le=500000)
    simulated_loan_term: int = Field(..., ge=6, le=120)
    simulated_interest_rate: float = Field(..., ge=1.0, le=40.0)


class LoanOptionSummary(BaseModel):
    loan_amount: float
    loan_term: int
    interest_rate: float
    estimated_emi: float
    affordability_status: str # "Comfortable", "Manageable", "Strained"
    monthly_free_cash_flow: float
    emi_to_income_ratio: float
    resilience_score: int # 0 - 100
    risk_indicator: str   # "Low", "Moderate", "High"
    default_probability: Optional[float] = None


class WhatIfSimulationResponse(BaseModel):
    current_option: LoanOptionSummary
    simulated_option: LoanOptionSummary
    recommended_safer_option: LoanOptionSummary
    emi_difference: float # positive means simulated saves money
    resilience_difference: int # positive means simulated has better resilience
    affordability_impact: str # "Significant Improvement", "Modest Improvement", "Increased Burden"
    comparison_verdict: str
    is_decision_support_only: bool = True
    disclaimer: str = (
        "Decision-support simulation — does not modify the underlying credit model. "
        "Illustrates cash flow sensitivity and repayment buffer changes."
    )


# =========================================================================
# FEATURE 2: SECOND CHANCE / RESPONSIBLE BORROWING
# =========================================================================

class SecondChanceRecommendation(BaseModel):
    is_suitable_at_requested_terms: bool
    status_label: str # "Suitable at requested terms" or "Not suitable at requested terms"
    headline: str
    requested_amount: float
    requested_term: int
    recommended_amount: float
    recommended_term: int
    recommended_emi: float
    reason_for_recommendation: str
    main_risk_factor: str
    main_positive_factor: str
    actionable_path: str
    responsible_lending_note: str = (
        "TVS Credit Responsible Lending Policy: We proactively restructure borrowing parameters "
        "to prevent over-indebtedness rather than issuing outright rejections."
    )


# =========================================================================
# FEATURE 3: CREDIT IMPROVEMENT SIMULATOR
# =========================================================================

class CreditImprovementItem(BaseModel):
    area_key: str
    area_name: str
    current_value_display: str
    target_recommendation: str
    timeframe_to_impact: str
    potential_impact_label: str
    action_steps: List[str]


class CreditImprovementResponse(BaseModel):
    customer_id: str
    overall_readiness_score: int # 0 - 100
    improvement_levers: List[CreditImprovementItem]
    potential_monthly_savings_est: float
    illustrative_disclaimer: str = (
        "Potential improvement — Illustrative simulation. Actual qualification is subject to "
        "underwriting verification and credit bureau refresh."
    )


# =========================================================================
# FEATURE 4: FINANCIAL HEALTH PASSPORT
# =========================================================================

class FinancialHealthPassport(BaseModel):
    customer_id: str
    customer_name: str
    passport_tier: str # "Gold Verified", "Silver Emerging", "Bronze Thin-File"
    income_stability_score: int = Field(..., ge=0, le=100)
    payment_discipline_score: int = Field(..., ge=0, le=100)
    repayment_capacity_score: int = Field(..., ge=0, le=100)
    debt_burden_score: int = Field(..., ge=0, le=100)
    employment_stability_score: int = Field(..., ge=0, le=100)
    financial_resilience_score: int = Field(..., ge=0, le=100)
    overall_health_status: str # "HEALTHY", "STABLE", "WATCH"
    badge_label: str
    validity_period: str = "Active 90-Day Evaluation"
    data_minimization_verified: bool = True


# =========================================================================
# FEATURE 5: ALTERNATIVE DATA EVIDENCE CONFIDENCE
# =========================================================================

class EvidenceConfidence(BaseModel):
    evidence_confidence_score: int = Field(..., ge=0, le=100)
    confidence_level: str # "High Evidence", "Moderate Evidence", "Emerging Evidence"
    consented_sources_count: int
    total_sources_count: int = 7
    data_completeness_pct: float
    strong_evidence: List[str]
    limited_evidence: List[str]
    label: str = "NIRNAY Evidence Confidence"
    disclaimer: str = (
        "Evidence Confidence reflects the breadth and completeness of consented alternative data signals, "
        "not statistical model certainty."
    )


# =========================================================================
# FEATURE 6: CONSENT INTELLIGENCE
# =========================================================================

class ConsentIntelligenceItem(BaseModel):
    source_id: str
    name: str
    used_for: str
    derived_signal: str
    raw_data_retention: str = "Not displayed / not retained in prototype"
    customer_control: str = "Grant | Review | Withdraw"
    consent_granted: bool
    status_label: str
    is_simulated: bool = True


class ConsentIntelligenceResponse(BaseModel):
    customer_id: str
    sources: List[ConsentIntelligenceItem]
    active_consents_count: int
    total_sources_count: int
    privacy_assurance: str = (
        "Alternative data shown in this prototype is synthetic/demo data. "
        "Assessment will dynamically use remaining consented signals."
    )


# =========================================================================
# FEATURE 7: FAIRNESS & RESPONSIBLE LENDING DASHBOARD
# =========================================================================

class FairnessMetricsResponse(BaseModel):
    total_applications_evaluated: int
    approval_rate: float
    manual_review_rate: float
    high_risk_rate: float
    first_time_borrower_inclusion_rate: float
    experienced_borrower_inclusion_rate: float
    alternative_data_coverage: float
    consent_authorization_rate: float
    avg_decision_latency_sec: float
    demographic_parity_ratio: float
    equal_opportunity_proxy: float
    sample_period: str = "Trailing 30-Day Simulated Cohort (N=1,248)"
    disclaimer: str = (
        "Demo / synthetic analytics for responsible lending compliance monitoring. "
        "Raw sensitive bank/UPI information is never exposed."
    )


# =========================================================================
# FEATURE 8: HUMAN-IN-THE-LOOP REVIEW
# =========================================================================

class HumanReviewRequest(BaseModel):
    application_id: str
    customer_id: str
    decision: str = Field(..., description="Approve, Reject, Request Additional Information, Continue Monitoring")
    override_reason: str
    analyst_role: str = "Senior Credit Officer"
    analyst_notes: Optional[str] = None


class HumanReviewResponse(BaseModel):
    application_id: str
    customer_id: str
    ai_decision: str
    ai_default_probability: float
    analyst_decision: str
    override_reason: str
    analyst_role: str
    analyst_notes: Optional[str]
    timestamp: str
    audit_status: str
    is_override: bool
    message: str


# =========================================================================
# FEATURE 9: FINANCIAL HEALTH TIMELINE
# =========================================================================

class HealthTimelineMilestone(BaseModel):
    period: str # "Month 1", "Month 2", "Month 3", "Month 4"
    health_status: str # "Stable", "Watch", "Early Warning"
    headline: str
    trigger_event: str
    financial_impact: str
    recommended_action: str
    is_projected: bool = True


class FinancialHealthTimelineResponse(BaseModel):
    customer_id: str
    current_period: str = "Month 1 (Disbursal)"
    milestones: List[HealthTimelineMilestone]
    proactive_guidance: str
    disclaimer: str = "Synthetic/demo post-disbursal financial health projection."


# =========================================================================
# FEATURE 10: AI FINANCIAL COACH
# =========================================================================

class FinancialCoachQueryRequest(BaseModel):
    question: str
    customer_id: Optional[str] = "TVS-CUST-10492"
    application_data: Optional[RiskAssessmentRequest] = None


class FinancialCoachQueryResponse(BaseModel):
    question: str
    coach_category: str # "Eligibility", "Affordability", "Resilience", "Tenure Strategy", "Improvement Roadmap"
    answer: str
    actionable_steps: List[str]
    suggested_questions: List[str]
    disclaimer: str = (
        "NIRNAY AI Financial Coach provides personalized educational guidance based on your alternative signals. "
        "Illustrative simulations do not constitute formal lending contracts."
    )


# =========================================================================
# AGENT ARCHITECTURE SUMMARY
# =========================================================================

class SpecializedAgentMetadata(BaseModel):
    agent_id: str
    name: str
    role_description: str
    key_signals_analyzed: List[str]
    active_status: str = "Active"


class NirnayAgentSystemStatus(BaseModel):
    platform_name: str = "TVS Credit NIRNAY"
    version: str = "2.5.0 (Hackathon Enterprise Edition)"
    specialized_agents: List[SpecializedAgentMetadata]
