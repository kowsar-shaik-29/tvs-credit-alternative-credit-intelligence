"""FastAPI REST API routes for TVS Credit Alternative Credit Intelligence / NIRNAY."""

import uuid
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.schemas.risk import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    ModelInfoResponse,
    HealthResponse,
    RiskFactor,
    ErrorResponse,
    ErrorDetail
)
from app.schemas.nirnay import (
    ConsentItem,
    ConsentUpdateRequest,
    ConsentStatusResponse,
    AlternativeScores,
    AlternativeDataProfile,
    DigitalTwinResponse,
    StressSimulationResponse,
    LoanRecommendationResponse,
    CustomerFriendlyFactor,
    FinancialHealthResponse,
    AuditTrailRecord,
    AssistantQueryRequest,
    AssistantQueryResponse,
    FullNirnayAssessmentResponse
)
from app.services.feature_engineering import feature_engineering_service
from app.services.model_service import model_service
from app.services.risk_service import risk_service
from app.services.alternative_data_service import alternative_data_service, DEFAULT_CONSENT_SOURCES
from app.services.digital_twin_service import digital_twin_service
from app.services.resilience_service import resilience_service
from app.services.stress_service import stress_service
from app.services.recommendation_service import recommendation_service
from app.services.monitoring_service import monitoring_service
from app.services.audit_service import audit_service
from app.services.assistant_service import assistant_service
from app.services.explanation_service import customer_explanation_service

logger = logging.getLogger("tvs_credit.api")

api_router = APIRouter()


# =========================================================================
# EXISTING CORE ML & HEALTH ENDPOINTS (PRESERVED 100%)
# =========================================================================

@api_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health and Readiness Check",
    description="Returns the operational status of the service and verification of loaded ML artifacts."
)
async def health_check():
    """Verify backend health and artifact readiness."""
    model_loaded = model_service.model is not None
    preprocessor_loaded = model_service.preprocessor is not None
    threshold_loaded = model_service.threshold is not None
    is_healthy = model_loaded and preprocessor_loaded and threshold_loaded

    status_str = "healthy" if is_healthy else "degraded"

    return HealthResponse(
        status=status_str,
        model_loaded=model_loaded,
        preprocessor_loaded=preprocessor_loaded,
        threshold_loaded=threshold_loaded,
    )


@api_router.get(
    "/api/v1/model-info",
    response_model=ModelInfoResponse,
    summary="Model Metadata",
    description="Returns public configuration metadata regarding the trained model and risk parameters."
)
async def get_model_info():
    """Return model architecture and operational metadata without internal file paths."""
    if not model_service.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model service is initializing or artifacts are missing."
        )

    model_type = (
        model_service.model.__class__.__name__
        if model_service.model else "RandomForestClassifier"
    )

    return ModelInfoResponse(
        model="Enhanced Random Forest",
        model_type=model_type,
        threshold=round(model_service.threshold, 2),
        feature_engineering="alternative_credit",
        status="ready"
    )


@api_router.post(
    "/api/v1/risk-assessment",
    response_model=RiskAssessmentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "Model Service Unavailable"}
    },
    summary="Credit Risk Assessment & Alternative Intelligence",
    description="Runs input validation, exact feature engineering, ML preprocessor, and Random Forest risk scoring."
)
async def assess_risk(request: RiskAssessmentRequest):
    """Execute end-to-end risk evaluation for a credit application."""
    if not model_service.is_ready:
        logger.error("Inference requested while model service is not ready.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Risk assessment engine is currently unavailable."
        )

    try:
        # 1. Map API fields to DataFrame
        raw_df = feature_engineering_service.convert_api_to_dataframe(request)

        # 2. Compute exact alternative credit features
        df_featured, indicators = feature_engineering_service.engineer_features(raw_df)

        # 3. Model inference using predict_proba()
        default_probability = model_service.predict_default_probability(df_featured)

        # 4. Evaluate risk classification and recommendation
        risk_details = risk_service.evaluate_risk(
            probability=default_probability,
            threshold=model_service.threshold
        )

        # 5. Explainability factors
        factors = model_service.explain_prediction(df_featured, top_k=5)

        logger.info(
            f"Successfully processed assessment: pred={risk_details.prediction}, "
            f"prob={risk_details.default_probability:.4f}, class={risk_details.risk_classification}"
        )

        return RiskAssessmentResponse(
            success=True,
            risk_assessment=risk_details,
            alternative_credit_indicators=indicators,
            top_risk_factors=factors
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during risk assessment execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while evaluating credit risk."
        )


@api_router.post(
    "/api/v1/risk-assessment/explanation",
    response_model=List[RiskFactor],
    summary="Model Explainability Factors",
    description="Generates the top risk and stability drivers for a given applicant profile."
)
async def get_explanation(request: RiskAssessmentRequest):
    """Return top feature contributors to default risk for the given applicant."""
    if not model_service.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model service is not ready."
        )

    try:
        raw_df = feature_engineering_service.convert_api_to_dataframe(request)
        df_featured, _ = feature_engineering_service.engineer_features(raw_df)
        factors = model_service.explain_prediction(df_featured, top_k=8)
        return factors
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate risk factor explanation."
        )


# =========================================================================
# EXTENDED NIRNAY INTELLIGENCE ENDPOINTS
# =========================================================================

# Active customer consent state (in-memory for session)
_CUSTOMER_CONSENTS: Dict[str, List[ConsentItem]] = {}


@api_router.get(
    "/api/v1/consent",
    response_model=ConsentStatusResponse,
    summary="Get Consent Status",
    description="Returns the 7 configurable alternative data consent categories and current authorization status."
)
async def get_consent_status(customer_id: str = "TVS-CUST-10492"):
    """Retrieve explicit consent status for customer."""
    if customer_id not in _CUSTOMER_CONSENTS:
        _CUSTOMER_CONSENTS[customer_id] = alternative_data_service.get_default_consents()

    sources = _CUSTOMER_CONSENTS[customer_id]
    all_granted = all(s.consent_granted for s in sources)

    return ConsentStatusResponse(
        customer_id=customer_id,
        sources=sources,
        all_consents_granted=all_granted,
        last_updated="Just now"
    )


@api_router.post(
    "/api/v1/consent",
    response_model=ConsentStatusResponse,
    summary="Update Data Consent",
    description="Allows applicant to explicitly grant, review, or withdraw consent for individual alternative data sources."
)
async def update_consent(update: ConsentUpdateRequest, customer_id: str = "TVS-CUST-10492"):
    """Update authorization toggle for a specific alternative data source."""
    if customer_id not in _CUSTOMER_CONSENTS:
        _CUSTOMER_CONSENTS[customer_id] = alternative_data_service.get_default_consents()

    sources = _CUSTOMER_CONSENTS[customer_id]
    found = False
    for s in sources:
        if s.source_id == update.source_id:
            s.consent_granted = update.consent_granted
            s.status_label = "Consent Granted" if update.consent_granted else "Consent Withdrawn"
            found = True
            break

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{update.source_id}' not recognized."
        )

    all_granted = all(s.consent_granted for s in sources)
    return ConsentStatusResponse(
        customer_id=customer_id,
        sources=sources,
        all_consents_granted=all_granted,
        last_updated="Updated"
    )


@api_router.post(
    "/api/v1/alternative-data/profile",
    response_model=AlternativeDataProfile,
    summary="Generate Alternative Credit Profile",
    description="Constructs consented synthetic alternative data across bank cash flow, UPI, bills, telecom, and GST."
)
async def get_alternative_profile(
    request: RiskAssessmentRequest,
    customer_id: str = "TVS-CUST-10492"
):
    """Generate deterministic simulated alternative credit signals for applicant."""
    consents = _CUSTOMER_CONSENTS.get(customer_id, alternative_data_service.get_default_consents())
    return alternative_data_service.generate_alternative_profile(
        request=request,
        customer_id=customer_id,
        consents=consents
    )


@api_router.get(
    "/api/v1/customer/{customer_id}/alternative-data",
    response_model=AlternativeDataProfile,
    summary="Get Customer Alternative Data",
    description="Fetches alternative data profile for an existing customer ID using a baseline reference profile."
)
async def get_customer_alternative_data(customer_id: str):
    """Retrieve alternative data profile for customer."""
    # Build default reference request
    ref_req = RiskAssessmentRequest(
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
    consents = _CUSTOMER_CONSENTS.get(customer_id, alternative_data_service.get_default_consents())
    return alternative_data_service.generate_alternative_profile(ref_req, customer_id, consents)


@api_router.post(
    "/api/v1/digital-twin",
    response_model=DigitalTwinResponse,
    summary="Build Financial Digital Twin",
    description="Generates the multi-dimensional behavioral twin matrix with grounded AI explanation."
)
async def build_digital_twin(
    request: RiskAssessmentRequest,
    customer_id: str = "TVS-CUST-10492"
):
    """Construct multi-dimensional Financial Digital Twin."""
    consents = _CUSTOMER_CONSENTS.get(customer_id, alternative_data_service.get_default_consents())
    alt_profile = alternative_data_service.generate_alternative_profile(request, customer_id, consents)
    return digital_twin_service.build_digital_twin(request, alt_profile)


@api_router.post(
    "/api/v1/stress-test",
    response_model=StressSimulationResponse,
    summary="Simulate Repayment Stress Scenarios",
    description="Evaluates 7 financial stress scenarios (Income drops, expense increases, missed bills, interruptions)."
)
async def run_stress_test(
    request: RiskAssessmentRequest,
    customer_id: str = "TVS-CUST-10492"
):
    """Run stress simulation across 7 shock scenarios."""
    consents = _CUSTOMER_CONSENTS.get(customer_id, alternative_data_service.get_default_consents())
    alt_profile = alternative_data_service.generate_alternative_profile(request, customer_id, consents)
    return stress_service.run_stress_test(request, alt_profile)


@api_router.post(
    "/api/v1/loan-recommendation",
    response_model=LoanRecommendationResponse,
    summary="Responsible Loan Recommendation",
    description="Determines maximum comfortable borrowing limit, recommended loan, tenure, and estimated EMI."
)
async def get_loan_recommendation(
    request: RiskAssessmentRequest,
    customer_id: str = "TVS-CUST-10492"
):
    """Generate responsible loan structuring recommendation."""
    if not model_service.is_ready:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model service unavailable")

    raw_df = feature_engineering_service.convert_api_to_dataframe(request)
    df_featured, _ = feature_engineering_service.engineer_features(raw_df)
    prob = model_service.predict_default_probability(df_featured)

    consents = _CUSTOMER_CONSENTS.get(customer_id, alternative_data_service.get_default_consents())
    alt_profile = alternative_data_service.generate_alternative_profile(request, customer_id, consents)

    return recommendation_service.recommend_loan(request, alt_profile, prob)


@api_router.get(
    "/api/v1/customer/{customer_id}/financial-health",
    response_model=FinancialHealthResponse,
    summary="Continuous Financial Health & Early Warnings",
    description="Returns post-disbursal surveillance status and early warning indicators."
)
async def get_financial_health(customer_id: str):
    """Retrieve ongoing financial health monitoring status."""
    ref_req = RiskAssessmentRequest(
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
    consents = _CUSTOMER_CONSENTS.get(customer_id, alternative_data_service.get_default_consents())
    alt_profile = alternative_data_service.generate_alternative_profile(ref_req, customer_id, consents)
    return monitoring_service.evaluate_health(customer_id, alt_profile, 0.3933)


@api_router.get(
    "/api/v1/customer/{customer_id}/audit",
    response_model=Optional[AuditTrailRecord],
    summary="Get Decision Audit Record",
    description="Returns compliance audit trail for the customer's decision."
)
async def get_audit_record(customer_id: str):
    """Retrieve decision audit trail record."""
    record = audit_service.get_record(customer_id)
    if not record:
        # Generate default record if not yet evaluated
        record = audit_service.log_assessment(
            application_id=f"TVS-APP-{uuid.uuid4().hex[:8].upper()}",
            customer_id=customer_id,
            customer_name="Arun Kumar (Notebook Reference)",
            default_prob=0.3933,
            risk_class="LOW RISK",
            recommended_action="MANUAL REVIEW",
            consented_sources=["bank_cash_flow", "upi_digital", "utility_payments", "mobile_bill"],
            alt_stability_score=87,
            resilience_score=86
        )
    return record


@api_router.get(
    "/api/v1/audit/records",
    response_model=List[AuditTrailRecord],
    summary="List Recent Audit Records",
    description="Returns list of recent credit assessment audit records for Credit Analyst portfolio review."
)
async def list_audit_records():
    """List portfolio audit records."""
    records = audit_service.list_recent_records()
    if not records:
        # Seed baseline records for analyst portal inspection
        seed_records = [
            ("TVS-APP-8192", "TVS-CUST-10492", "Arun Kumar (Notebook Reference)", 0.4168, "LOW RISK", "MANUAL REVIEW", 87, 86),
            ("TVS-APP-7401", "TVS-CUST-10114", "Rahul Sharma (First-Time Borrower)", 0.2840, "LOW RISK", "ELIGIBLE", 92, 85),
            ("TVS-APP-9210", "TVS-CUST-10882", "M. Lakshmi Narayanan (Kirana Merchant)", 0.3320, "LOW RISK", "MANUAL REVIEW", 88, 84),
            ("TVS-APP-5502", "TVS-CUST-10331", "Vikram Sen (Platform Delivery Partner)", 0.3750, "LOW RISK", "MANUAL REVIEW", 79, 76),
            ("TVS-APP-6204", "TVS-CUST-10654", "Suresh Patel (Kisan Allied & Rural)", 0.2910, "LOW RISK", "ELIGIBLE", 83, 82),
            ("TVS-APP-4109", "TVS-CUST-10901", "Prakash Verma (Stressed Leverage)", 0.7113, "HIGH RISK", "HIGH RISK - FURTHER REVIEW", 48, 42),
            ("TVS-APP-9981", "TVS-CUST-10022", "Deepa Sundaram (Prime Alternative Profile)", 0.0357, "LOW RISK", "ELIGIBLE", 96, 95)
        ]
        for app_id, cust_id, name, prob, rclass, act, stab, res in seed_records:
            audit_service.log_assessment(
                application_id=app_id,
                customer_id=cust_id,
                customer_name=name,
                default_prob=prob,
                risk_class=rclass,
                recommended_action=act,
                consented_sources=["bank_cash_flow", "upi_digital", "utility_payments", "mobile_bill"],
                alt_stability_score=stab,
                resilience_score=res
            )
        records = audit_service.list_recent_records()
    return records


@api_router.post(
    "/api/v1/nirnay/full-assessment",
    response_model=FullNirnayAssessmentResponse,
    summary="Unified NIRNAY Full Assessment Pipeline",
    description="Executes composite pipeline: ML risk scoring, alternative data generation, digital twin, stress test, recommendation, and audit logging."
)
async def run_full_nirnay_assessment(
    request: RiskAssessmentRequest,
    customer_id: str = "TVS-CUST-10492"
):
    """Execute complete end-to-end NIRNAY intelligence evaluation."""
    if not model_service.is_ready:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model service unavailable")

    try:
        # 1. Existing ML pipeline
        raw_df = feature_engineering_service.convert_api_to_dataframe(request)
        df_featured, indicators = feature_engineering_service.engineer_features(raw_df)
        default_prob = model_service.predict_default_probability(df_featured)
        risk_details = risk_service.evaluate_risk(default_prob, model_service.threshold)
        raw_factors = model_service.explain_prediction(df_featured, top_k=6)

        # 2. Consents & Alternative Data Profile
        consents = _CUSTOMER_CONSENTS.get(customer_id, alternative_data_service.get_default_consents())
        alt_profile = alternative_data_service.generate_alternative_profile(request, customer_id, consents)

        # 3. Financial Digital Twin
        digital_twin = digital_twin_service.build_digital_twin(request, alt_profile)

        # 4. Customer-Friendly Factors
        friendly_factors = customer_explanation_service.build_friendly_factors(
            request, alt_profile, raw_factors, default_prob
        )

        # 5. Stress Simulation (7 scenarios)
        stress_results = stress_service.run_stress_test(request, alt_profile)

        # 6. Responsible Loan Recommendation
        recommendation = recommendation_service.recommend_loan(request, alt_profile, default_prob)

        # 7. Continuous Health Monitoring
        health_eval = monitoring_service.evaluate_health(customer_id, alt_profile, default_prob)

        # 8. Audit Record
        app_id = f"TVS-APP-{uuid.uuid4().hex[:8].upper()}"
        consented_list = [c.source_id for c in consents if c.consent_granted]
        audit_record = audit_service.log_assessment(
            application_id=app_id,
            customer_id=customer_id,
            customer_name=alt_profile.customer_name,
            default_prob=default_prob,
            risk_class=risk_details.risk_classification,
            recommended_action=risk_details.recommended_action,
            consented_sources=consented_list,
            alt_stability_score=alt_profile.scores.cash_flow_stability,
            resilience_score=stress_results.baseline_resilience,
            dealer_status=f"Eligible for ₹{recommendation.recommended_loan:,.0f}" if risk_details.prediction == 0 else "Verification Required"
        )

        return FullNirnayAssessmentResponse(
            application_id=app_id,
            customer_id=customer_id,
            customer_name=alt_profile.customer_name,
            archetype=alt_profile.archetype_name,
            risk_assessment=risk_details,
            traditional_indicators=indicators,
            raw_ml_factors=raw_factors,
            consent_status=consents,
            alternative_scores=alt_profile.scores,
            digital_twin=digital_twin,
            customer_friendly_factors=friendly_factors,
            stress_test=stress_results,
            loan_recommendation=recommendation,
            financial_health=health_eval,
            audit_record=audit_record
        )

    except Exception as e:
        logger.error(f"Error in full NIRNAY assessment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating full NIRNAY credit assessment."
        )


@api_router.post(
    "/api/v1/assistant/query",
    response_model=AssistantQueryResponse,
    summary="NIRNAY Financial Assistant Query",
    description="Answers applicant inquiries regarding risk classification, eligibility improvement, affordability, and stress resilience."
)
async def query_assistant(query: AssistantQueryRequest):
    """Answer applicant questions transparently using live profile data."""
    req = query.application_data
    if not req:
        # Default reference
        req = RiskAssessmentRequest(
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

    customer_id = query.customer_id or "TVS-CUST-10492"
    consents = _CUSTOMER_CONSENTS.get(customer_id, alternative_data_service.get_default_consents())
    alt_profile = alternative_data_service.generate_alternative_profile(req, customer_id, consents)

    # Compute probability
    default_prob = 0.3933
    if model_service.is_ready:
        raw_df = feature_engineering_service.convert_api_to_dataframe(req)
        df_featured, _ = feature_engineering_service.engineer_features(raw_df)
        default_prob = model_service.predict_default_probability(df_featured)

    rec = recommendation_service.recommend_loan(req, alt_profile, default_prob)
    resilience = resilience_service.calculate_resilience(req, alt_profile.scores)

    return assistant_service.answer_query(
        question=query.question,
        request=req,
        alt_profile=alt_profile,
        default_prob=default_prob,
        recommended_loan=rec.recommended_loan,
        resilience_score=resilience
    )
