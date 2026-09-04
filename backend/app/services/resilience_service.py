"""Financial Resilience evaluation service for TVS Credit NIRNAY.

Quantifies an applicant's capacity to absorb unforeseen financial shocks
(health emergencies, inflation surges, revenue disruptions) without loan default.
"""

from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import AlternativeScores


class ResilienceService:
    """Calculates granular financial resilience and shock resistance."""

    def calculate_resilience(
        self,
        request: RiskAssessmentRequest,
        alt_scores: AlternativeScores
    ) -> int:
        """Compute composite resilience score (0 - 100)."""
        # Component 1: Cash Flow Buffer (30%)
        buffer_score = alt_scores.cash_flow_stability * 0.30

        # Component 2: Debt Headroom (25%) - inverse of DTI / debt burden
        debt_headroom = max(100 - (request.dti_ratio * 100), 10.0) * 0.25

        # Component 3: Payment Consistency (20%)
        payment_component = alt_scores.payment_discipline * 0.20

        # Component 4: Income Continuity (15%)
        income_component = alt_scores.income_stability * 0.15

        # Component 5: Employment / Activity Stability (10%)
        tenure_factor = min(request.months_employed / 48.0, 1.0) * 100.0
        tenure_component = tenure_factor * 0.10

        composite = buffer_score + debt_headroom + payment_component + income_component + tenure_component
        return int(max(min(round(composite), 99), 15))


resilience_service = ResilienceService()
