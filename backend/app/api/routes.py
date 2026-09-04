"""FastAPI REST API routes for TVS Credit Alternative Credit Intelligence."""

import logging
from typing import Dict, Any, List
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
from app.services.feature_engineering import feature_engineering_service
from app.services.model_service import model_service
from app.services.risk_service import risk_service

logger = logging.getLogger("tvs_credit.api")

api_router = APIRouter()


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
