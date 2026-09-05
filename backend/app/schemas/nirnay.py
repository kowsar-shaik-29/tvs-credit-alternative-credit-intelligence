"""Pydantic schemas for the TVS Credit NIRNAY Alternative Credit Intelligence platform."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.schemas.risk import RiskAssessmentRequest, RiskAssessmentDetails, AlternativeCreditIndicators, RiskFactor
from app.schemas.nirnay_enhancements import (
    FinancialHealthPassport,
    EvidenceConfidence,
    SecondChanceRecommendation,
    FinancialHealthTimelineResponse,
    ConsentIntelligenceResponse,
    CreditImprovementResponse
)


# ==========================================
# 1. CONSENT MANAGEMENT
# ==========================================

class ConsentItem(BaseModel):
    source_id: str = Field(..., description="Unique identifier for the data source")
    name: str = Field(..., description="Display name of the data source")
    category: str = Field(..., description="Category (Banking, Digital, Utilities, etc.)")
    purpose: str = Field(..., description="Clear explanation of why this data is needed")
    data_accessed: str = Field(..., description="Specific data attributes accessed")
    impact_description: str = Field(..., description="How this data affects the credit assessment")
    is_connected: bool = Field(True, description="Whether the source provider is connected")
    consent_granted: bool = Field(True, description="Whether user has granted explicit consent")
    status_label: str = Field("Consent Granted", description="Human-readable consent status")
    is_simulated: bool = Field(True, description="Flag indicating simulated/demo data")


class ConsentUpdateRequest(BaseModel):
    source_id: str
    consent_granted: bool


class ConsentStatusResponse(BaseModel):
    customer_id: str
    sources: List[ConsentItem]
    all_consents_granted: bool
    last_updated: str


# ==========================================
# 2. ALTERNATIVE DATA PROFILES & SCORES
# ==========================================

class BankCashFlowData(BaseModel):
    average_monthly_inflow: float
    average_monthly_outflow: float
    cash_flow_stability: float  # 0 - 100
    income_consistency: float   # 0 - 100
    minimum_monthly_balance: float
    recurring_expenses: float
    inflow_outflow_ratio: float
    months_of_observed_history: int
    is_simulated: bool = True


class UPIDigitalData(BaseModel):
    transaction_count_monthly: int
    average_transaction_amount: float
    monthly_transaction_volume: float
    payment_consistency: float  # 0 - 100
    failed_transaction_rate: float # percentage
    recurring_payment_consistency: float # 0 - 100
    digital_payment_discipline: float # 0 - 100
    is_simulated: bool = True


class UtilityHistoryData(BaseModel):
    bills_paid: int
    bills_on_time: int
    missed_payments: int
    average_bill_amount: float
    payment_consistency: float # 0 - 100
    utility_payment_discipline: float # 0 - 100
    months_of_history: int
    supported_utilities: List[str] = ["Electricity", "Water", "LPG Cylinder", "Broadband"]
    is_simulated: bool = True


class TelecomHistoryData(BaseModel):
    average_monthly_bill: float
    bills_paid_on_time: int
    missed_payments: int
    average_payment_delay_days: float
    payment_consistency: float # 0 - 100
    months_of_history: int
    is_simulated: bool = True


class GSTBusinessData(BaseModel):
    is_applicable: bool = True
    business_name: Optional[str] = None
    business_tenure_years: Optional[float] = None
    monthly_revenue_trend: Optional[str] = "Stable / Growing"
    gst_filing_consistency: Optional[float] = None # 0 - 100
    revenue_stability: Optional[float] = None # 0 - 100
    business_cash_flow_stability: Optional[float] = None # 0 - 100
    seasonal_volatility: Optional[str] = "Low"
    is_simulated: bool = True


class TVSRepaymentData(BaseModel):
    has_history: bool = False
    previous_loans_count: int = 0
    repayment_consistency: Optional[float] = None # 0 - 100
    on_time_payments: int = 0
    missed_payments: int = 0
    overdue_history: bool = False
    completed_loans: int = 0
    relationship_notes: str = "No previous TVS repayment history"
    is_simulated: bool = True


class AlternativeScores(BaseModel):
    payment_discipline: int = Field(..., ge=0, le=100, description="Overall payment timeliness")
    income_stability: int = Field(..., ge=0, le=100, description="Regularity of earnings")
    cash_flow_stability: int = Field(..., ge=0, le=100, description="Inflow vs outflow buffer")
    utility_discipline: int = Field(..., ge=0, le=100, description="Consistency on recurring utility bills")
    digital_payment_discipline: int = Field(..., ge=0, le=100, description="UPI regularity and failure rate")
    employment_stability: int = Field(..., ge=0, le=100, description="Job tenure and employer stability")
    business_stability: Optional[int] = Field(None, ge=0, le=100, description="GST / commercial continuity (if applicable)")
    debt_burden: int = Field(..., ge=0, le=100, description="Leverage and monthly obligation load")
    financial_resilience: int = Field(..., ge=0, le=100, description="Ability to withstand unexpected shocks")


class AlternativeDataProfile(BaseModel):
    customer_id: str
    customer_name: str
    archetype_name: str
    bank_cash_flow: Optional[BankCashFlowData] = None
    upi_digital: Optional[UPIDigitalData] = None
    utility_history: Optional[UtilityHistoryData] = None
    telecom_history: Optional[TelecomHistoryData] = None
    gst_business: Optional[GSTBusinessData] = None
    tvs_repayment: Optional[TVSRepaymentData] = None
    scores: AlternativeScores


# ==========================================
# 3. FINANCIAL DIGITAL TWIN
# ==========================================

class DigitalTwinDimension(BaseModel):
    dimension: str
    score: int = Field(..., ge=0, le=100)
    benchmark: int = 70
    status: str # "Strong", "Moderate", "Attention Needed"
    summary: str


class DigitalTwinResponse(BaseModel):
    customer_id: str
    dimensions: List[DigitalTwinDimension]
    twin_stability_index: int = Field(..., ge=0, le=100)
    ai_grounded_summary: str
    strengths: List[str]
    vulnerabilities: List[str]


# ==========================================
# 4. STRESS SIMULATION
# ==========================================

class StressScenarioResult(BaseModel):
    scenario_id: str
    scenario_name: str
    description: str
    stressed_income: float
    stressed_expenses: float
    stressed_affordability: str # "Comfortable", "Manageable", "Strained", "Critical"
    repayment_capacity: float   # 0.0 - 1.0
    resilience_score: int       # 0 - 100
    risk_level: str             # "Low", "Moderate", "High", "Critical"
    recommendation: str
    estimated_emi_buffer: float


class StressSimulationResponse(BaseModel):
    baseline_resilience: int
    baseline_risk: str
    baseline_capacity: float
    scenarios: List[StressScenarioResult]
    simulation_notes: str = "Simulated scenario for stress testing only. Does not predict future events."


# ==========================================
# 5. RESPONSIBLE LOAN RECOMMENDATION
# ==========================================

class LoanRecommendationResponse(BaseModel):
    requested_amount: float
    requested_loan_amount: Optional[float] = None
    recommended_loan: float
    max_comfortable_loan: float
    requested_tenure_months: Optional[int] = None
    recommended_tenure_months: int
    estimated_emi: float
    interest_rate: float
    affordability_status: str # "Comfortable", "Manageable", "Strained"
    risk_level: str           # "Low Risk", "Moderate Risk", "High Risk"
    approval_path: str        # "Automated Approval", "Assisted Manual Review", "Alternative Structuring"
    reasoning: str
    repayment_guardrail: str


# ==========================================
# 6. EXPLAINABILITY & CUSTOMER FACTORS
# ==========================================

class CustomerFriendlyFactor(BaseModel):
    category: str # "Positive", "Risk", "Neutral"
    factor_name: str
    score_display: str
    impact: str   # "Positive", "Negative", "Neutral"
    plain_explanation: str


# ==========================================
# 7. CONTINUOUS MONITORING
# ==========================================

class EarlyWarningAlert(BaseModel):
    severity: str # "Info", "Watch", "Early Warning", "High Risk"
    title: str
    description: str
    metric_changed: str
    observed_trend: str
    recommended_intervention: str


class FinancialHealthResponse(BaseModel):
    customer_id: str
    health_status: str # "Stable", "Watch", "Early Warning", "High Risk"
    last_evaluation_period: str
    stability_trend: str # "+4% over 90 days", etc.
    active_alerts: List[EarlyWarningAlert]
    monitoring_disclaimer: str = "Conceptual periodic health monitoring using simulated ongoing metrics."


# ==========================================
# 8. AUDIT TRAIL
# ==========================================

class AuditTrailRecord(BaseModel):
    application_id: str
    customer_id: str
    customer_name: str
    timestamp: str
    model_name: str = "Enhanced Random Forest"
    model_version: str = "1.0.0 (Production NIRNAY)"
    threshold: float = 0.47
    default_probability: float
    risk_classification: str
    recommended_action: str
    consented_sources: List[str]
    alternative_stability_score: int
    resilience_score: int
    analyst_action: str = "Pending Review"
    dealer_status: str = "Eligible - Verification Complete"


# ==========================================
# 9. NIRNAY FINANCIAL ASSISTANT
# ==========================================

class AssistantQueryRequest(BaseModel):
    question: str
    customer_id: Optional[str] = None
    application_data: Optional[RiskAssessmentRequest] = None


class AssistantQueryResponse(BaseModel):
    question: str
    answer: str
    key_metrics_referenced: Dict[str, Any]
    suggested_followups: List[str]


# ==========================================
# 10. UNIFIED FULL NIRNAY ASSESSMENT
# ==========================================

class FullNirnayAssessmentResponse(BaseModel):
    application_id: str
    customer_id: str
    customer_name: str
    archetype: str
    # Machine Learning Core
    risk_assessment: RiskAssessmentDetails
    traditional_indicators: AlternativeCreditIndicators
    raw_ml_factors: List[RiskFactor]
    # NIRNAY Extension Intelligence
    consent_status: List[ConsentItem]
    alternative_scores: AlternativeScores
    digital_twin: DigitalTwinResponse
    customer_friendly_factors: List[CustomerFriendlyFactor]
    stress_test: StressSimulationResponse
    loan_recommendation: LoanRecommendationResponse
    financial_health: FinancialHealthResponse
    audit_record: AuditTrailRecord
    # NIRNAY 2.5 Hackathon Enhancements
    passport: Optional[FinancialHealthPassport] = None
    evidence_confidence: Optional[EvidenceConfidence] = None
    second_chance: Optional[SecondChanceRecommendation] = None
    health_timeline: Optional[FinancialHealthTimelineResponse] = None
    consent_intelligence: Optional[ConsentIntelligenceResponse] = None
    credit_improvement: Optional[CreditImprovementResponse] = None
