"""Pydantic schemas for request validation and structured API responses."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class RiskAssessmentRequest(BaseModel):
    """Raw customer and loan application input schema with sensible validation."""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "age": 30,
                "income": 50000.0,
                "loan_amount": 40000.0,
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
        }
    )

    age: int = Field(..., gt=0, le=120, description="Applicant age in years")
    income: float = Field(..., ge=0, description="Annual gross income")
    loan_amount: float = Field(..., gt=0, description="Requested principal loan amount")
    credit_score: int = Field(..., gt=0, le=850, description="Credit score between 300 and 850")
    months_employed: int = Field(..., ge=0, description="Total months employed")
    num_credit_lines: int = Field(..., ge=0, description="Total active credit lines")
    interest_rate: float = Field(..., ge=0, description="Annual interest rate percentage")
    loan_term: int = Field(..., gt=0, description="Repayment term in months")
    dti_ratio: float = Field(..., ge=0, description="Debt-to-Income ratio (0.0 - 1.0+)")
    education: str = Field(..., description="Highest education level reached")
    employment_type: str = Field(..., description="Employment status: Full-time, Part-time, Self-employed, Unemployed")
    marital_status: str = Field(..., description="Marital status: Single, Married, Divorced")
    has_mortgage: bool = Field(..., description="Whether applicant holds an existing mortgage")
    has_dependents: bool = Field(..., description="Whether applicant has financial dependents")
    loan_purpose: str = Field(..., description="Purpose of loan: Auto, Business, Education, Home, Other")
    has_cosigner: bool = Field(..., description="Whether a co-signer guarantees the loan")


class RiskFactor(BaseModel):
    """Explainability contribution for a specific feature."""
    feature: str
    impact: str = Field(..., description="'Positive' (increases risk) or 'Negative' (decreases risk)")
    value: float


class RiskAssessmentDetails(BaseModel):
    """Model prediction, threshold, classification, and recommended action."""
    default_probability: float = Field(..., description="Predicted probability of default [0.0 - 1.0]")
    risk_threshold: float = Field(..., description="Operational risk threshold from risk_threshold.pkl")
    prediction: int = Field(..., description="0 = Low Risk, 1 = High Risk")
    risk_classification: str = Field(..., description="'LOW RISK' or 'HIGH RISK'")
    recommended_action: str = Field(..., description="'ELIGIBLE', 'MANUAL REVIEW', or 'HIGH RISK - FURTHER REVIEW'")


class AlternativeCreditIndicators(BaseModel):
    """Engineered alternative-credit financial indicators."""
    financial_stability_score: float = Field(..., description="Normalized weighted composite stability index")
    repayment_capacity: float = Field(..., description="Cashflow buffer adjusted for debt-to-income stress")
    employment_stability: float = Field(..., description="Normalized tenure stability ratio")
    debt_stress: float = Field(..., description="Composite stress score combining DTI and loan burden")
    loan_burden: float = Field(..., description="Ratio of requested loan to annual income")
    interest_burden: float = Field(..., description="Effective interest burden metric")
    income_loan_ratio: float = Field(..., description="Ratio of annual income to requested loan")
    credit_line_burden: float = Field(..., description="Credit utilization and line dependency proxy")


class RiskAssessmentResponse(BaseModel):
    """Main response schema for /api/v1/risk-assessment."""
    success: bool = True
    risk_assessment: RiskAssessmentDetails
    alternative_credit_indicators: AlternativeCreditIndicators
    top_risk_factors: Optional[List[RiskFactor]] = None


class ModelInfoResponse(BaseModel):
    """Safe model metadata without exposing filesystem paths."""
    model: str = "Enhanced Random Forest"
    model_type: str = "RandomForestClassifier"
    threshold: float
    feature_engineering: str = "alternative_credit"
    status: str = "ready"


class HealthResponse(BaseModel):
    """Application readiness and artifact load status."""
    status: str
    model_loaded: bool
    preprocessor_loaded: bool
    threshold_loaded: bool


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
