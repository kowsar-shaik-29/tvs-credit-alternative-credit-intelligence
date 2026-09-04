"""Customer-Friendly Explainability service for TVS Credit NIRNAY.

Translates internal machine-learning feature attributions and alternative signals
into clear, accessible Positive, Risk, and Neutral factors for applicants and analysts.
"""

from typing import List
from app.schemas.risk import RiskAssessmentRequest, RiskFactor
from app.schemas.nirnay import (
    AlternativeDataProfile,
    CustomerFriendlyFactor
)


class CustomerExplanationService:
    """Translates credit indicators and ML contributions into human-readable explanations."""

    def build_friendly_factors(
        self,
        request: RiskAssessmentRequest,
        alt_profile: AlternativeDataProfile,
        raw_factors: List[RiskFactor],
        default_prob: float
    ) -> List[CustomerFriendlyFactor]:
        friendly: List[CustomerFriendlyFactor] = []
        scores = alt_profile.scores

        # Positive Factors
        if scores.payment_discipline >= 80:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Positive",
                    factor_name="Recurring Payment Discipline",
                    score_display=f"{scores.payment_discipline}/100",
                    impact="Positive",
                    plain_explanation="Consistent on-time payment track record across verified utility and digital commitments."
                )
            )

        if scores.cash_flow_stability >= 75:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Positive",
                    factor_name="Cash Flow Regularity",
                    score_display=f"{scores.cash_flow_stability}/100",
                    impact="Positive",
                    plain_explanation="Regular monthly deposits create a dependable operational liquidity buffer over living expenses."
                )
            )

        if request.credit_score >= 650:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Positive",
                    factor_name="Established Credit Bureau Score",
                    score_display=f"{request.credit_score}",
                    impact="Positive",
                    plain_explanation="Credit bureau score reflects responsible previous credit management history."
                )
            )
        elif scores.utility_discipline >= 85:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Positive",
                    factor_name="Alternative Utility Reliability",
                    score_display=f"{scores.utility_discipline}/100",
                    impact="Positive",
                    plain_explanation="Flawless utility payment history acts as strong substitute proof of credit discipline."
                )
            )

        if request.months_employed >= 36:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Positive",
                    factor_name="Stable Employment Tenure",
                    score_display=f"{request.months_employed} months",
                    impact="Positive",
                    plain_explanation="Sustained employment with current employer demonstrates low risk of sudden income loss."
                )
            )

        if request.has_cosigner:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Positive",
                    factor_name="Co-Signer Backing",
                    score_display="Present",
                    impact="Positive",
                    plain_explanation="Secondary guarantor significantly improves credit security and repayment certainty."
                )
            )

        # Risk Factors
        if request.dti_ratio >= 0.50:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Risk",
                    factor_name="Existing Debt Obligations (DTI)",
                    score_display=f"{int(request.dti_ratio * 100)}%",
                    impact="Negative",
                    plain_explanation="A significant portion of monthly earnings is already committed to servicing existing debts."
                )
            )

        monthly_inc = max(request.income / 12.0, 1.0)
        est_emi = (request.loan_amount / max(request.loan_term, 1))
        if est_emi > (monthly_inc * 0.40):
            friendly.append(
                CustomerFriendlyFactor(
                    category="Risk",
                    factor_name="Requested Loan Burden",
                    score_display=f"₹{request.loan_amount:,.0f}",
                    impact="Negative",
                    plain_explanation="The requested loan size is relatively high compared to current verified monthly earnings."
                )
            )

        if request.interest_rate >= 14.0:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Risk",
                    factor_name="Interest Cost Burden",
                    score_display=f"{request.interest_rate}% p.a.",
                    impact="Negative",
                    plain_explanation="Higher applicable interest rate increases the total monthly repayment commitment."
                )
            )

        if request.months_employed < 18:
            friendly.append(
                CustomerFriendlyFactor(
                    category="Risk",
                    factor_name="Early Career / New Activity Tenure",
                    score_display=f"{request.months_employed} months",
                    impact="Negative",
                    plain_explanation="Limited duration in current occupation creates moderate sensitivity to economic shifts."
                )
            )

        if scores.debt_burden >= 60 and not any(f.factor_name.startswith("Existing Debt") for f in friendly):
            friendly.append(
                CustomerFriendlyFactor(
                    category="Risk",
                    factor_name="Elevated Leverage Index",
                    score_display=f"{scores.debt_burden}/100",
                    impact="Negative",
                    plain_explanation="Multiple outstanding commitments diminish the household's free discretionary cash flow."
                )
            )

        # Neutral Factors
        friendly.append(
            CustomerFriendlyFactor(
                category="Neutral",
                factor_name="Loan Term Duration",
                score_display=f"{request.loan_term} months",
                impact="Neutral",
                plain_explanation=f"Structured over {request.loan_term} months; balancing manageable monthly payments with overall interest."
            )
        )

        friendly.append(
            CustomerFriendlyFactor(
                category="Neutral",
                factor_name="Loan Purpose",
                score_display=f"{request.loan_purpose}",
                impact="Neutral",
                plain_explanation=f"Loan earmarked for {request.loan_purpose} financing with appropriate category underwriting guidelines."
            )
        )

        return friendly


customer_explanation_service = CustomerExplanationService()
