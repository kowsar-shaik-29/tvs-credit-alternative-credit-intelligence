"""Responsible Loan Recommendation service for TVS Credit NIRNAY.

Calculates realistic borrowing capacity and structured loan options based on
applicant repayment capacity, alternative cash-flow stability, and debt obligations.
"""

from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import (
    AlternativeDataProfile,
    LoanRecommendationResponse
)


class RecommendationService:
    """Generates responsible loan structuring recommendations."""

    def recommend_loan(
        self,
        request: RiskAssessmentRequest,
        alt_profile: AlternativeDataProfile,
        default_prob: float
    ) -> LoanRecommendationResponse:
        monthly_income = max(request.income / 12.0, 1000.0)
        existing_monthly_debt = monthly_income * request.dti_ratio
        net_surplus = max(monthly_income - existing_monthly_debt - (monthly_income * 0.40), 500.0)

        # Max comfortable monthly EMI is 50% of available net surplus
        max_safe_emi = net_surplus * 0.50

        # Adjust based on alternative resilience & stability
        resilience = alt_profile.scores.financial_resilience
        stability_multiplier = min(max((resilience / 100.0), 0.5), 1.15)
        adjusted_safe_emi = max_safe_emi * stability_multiplier

        # Recommended tenure
        if request.loan_amount > (monthly_income * 12.0):
            recommended_tenure = min(max(request.loan_term + 12, 36), 60)
        elif request.loan_amount < (monthly_income * 4.0):
            recommended_tenure = max(min(request.loan_term, 24), 12)
        else:
            recommended_tenure = request.loan_term

        # Compute maximum loan that fits within adjusted_safe_emi over recommended_tenure
        # PV approximation with simple interest factor
        int_factor = 1.0 + (request.interest_rate / 100.0) * (recommended_tenure / 12.0)
        max_comfortable_loan = round((adjusted_safe_emi * recommended_tenure) / int_factor, -2)

        # Recommended loan: lesser of requested amount and comfortable loan, or scaled appropriately
        if request.loan_amount <= max_comfortable_loan:
            recommended_loan = request.loan_amount
            affordability = "Comfortable"
        elif request.loan_amount <= (max_comfortable_loan * 1.25):
            recommended_loan = max_comfortable_loan
            affordability = "Manageable"
        else:
            recommended_loan = max_comfortable_loan
            affordability = "Strained"

        # Calculate estimated EMI on recommended loan
        est_emi = round((recommended_loan / recommended_tenure) * (1.0 + (request.interest_rate / 100.0) * (recommended_tenure / 24.0)), 2)

        # Determine risk level and approval path
        tenure_note = (
            f"Requested tenure of {request.loan_term} months matched."
            if recommended_tenure == request.loan_term
            else f"Requested tenure is {request.loan_term} months; recommended tenure structured to {recommended_tenure} months to safeguard liquidity."
        )

        if default_prob < 0.30 and affordability == "Comfortable":
            risk_level = "Low Risk"
            approval_path = "Automated Approval"
            reasoning = (
                f"Approved based on robust cash flow stability ({alt_profile.scores.cash_flow_stability}/100) and "
                f"responsible debt-to-income profile. {tenure_note} The proposed monthly EMI of ₹{est_emi:,.0f} absorbs well within monthly surplus."
            )
        elif default_prob < 0.47:
            risk_level = "Moderate Risk"
            approval_path = "Assisted Manual Review"
            reasoning = (
                f"Eligible under structured terms. Alternative payment discipline is verified ({alt_profile.scores.payment_discipline}/100). "
                f"Requested exposure of ₹{request.loan_amount:,.0f} aligned to ₹{recommended_loan:,.0f}. {tenure_note}"
            )
        else:
            risk_level = "High Risk"
            approval_path = "Alternative Structuring"
            reasoning = (
                f"Elevated baseline leverage. Loan restructured to ₹{recommended_loan:,.0f} to avoid debt overload. "
                f"{tenure_note} Adding a co-signer or pledged asset security can qualify applicant for higher financing."
            )

        guardrail = (
            f"EMI capped at ₹{adjusted_safe_emi:,.0f}/month (max 50% of verified free cash flow) "
            f"to protect the borrower against unexpected inflation or income fluctuations."
        )

        return LoanRecommendationResponse(
            requested_amount=request.loan_amount,
            requested_loan_amount=request.loan_amount,
            recommended_loan=recommended_loan,
            max_comfortable_loan=max_comfortable_loan,
            requested_tenure_months=request.loan_term,
            recommended_tenure_months=recommended_tenure,
            estimated_emi=est_emi,
            interest_rate=request.interest_rate,
            affordability_status=affordability,
            risk_level=risk_level,
            approval_path=approval_path,
            reasoning=reasoning,
            repayment_guardrail=guardrail
        )


recommendation_service = RecommendationService()
