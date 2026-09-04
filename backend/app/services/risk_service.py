"""Risk classification and multi-tier credit recommendation decision engine."""

import logging
from app.schemas.risk import RiskAssessmentDetails

logger = logging.getLogger("tvs_credit.risk_service")


class RiskService:
    """Implements separate model risk classification and final credit recommendation actions."""

    @staticmethod
    def evaluate_risk(probability: float, threshold: float) -> RiskAssessmentDetails:
        """Evaluate model output against threshold and decision rules.

        Args:
            probability: Default probability (class 1) from 0.0 to 1.0.
            threshold: Operational risk threshold (typically 0.47 from risk_threshold.pkl).

        Returns:
            RiskAssessmentDetails with prediction, classification, and recommended action.
        """
        # Model classification (binary boundary based on risk threshold)
        if probability >= threshold:
            prediction = 1
            risk_classification = "HIGH RISK"
        else:
            prediction = 0
            risk_classification = "LOW RISK"

        # Business Recommendation / Decision Logic
        if probability < 0.30:
            recommended_action = "ELIGIBLE"
        elif probability < threshold:
            recommended_action = "MANUAL REVIEW"
        else:
            recommended_action = "HIGH RISK - FURTHER REVIEW"

        logger.info(
            f"Risk evaluation: prob={probability:.4f}, thresh={threshold:.2f}, "
            f"class={risk_classification}, action={recommended_action}"
        )

        return RiskAssessmentDetails(
            default_probability=round(float(probability), 4),
            risk_threshold=round(float(threshold), 2),
            prediction=prediction,
            risk_classification=risk_classification,
            recommended_action=recommended_action,
        )


# Singleton instance
risk_service = RiskService()
