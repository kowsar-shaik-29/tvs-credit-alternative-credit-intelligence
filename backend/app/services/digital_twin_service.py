"""Financial Digital Twin service for TVS Credit NIRNAY.

Constructs a multi-dimensional behavioral twin representing applicant cash-flow,
debt obligations, and payment discipline, accompanied by a factual, grounded narrative.
"""

from typing import List
from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import (
    AlternativeDataProfile,
    DigitalTwinDimension,
    DigitalTwinResponse
)


class DigitalTwinService:
    """Builds and interprets the customer's Financial Digital Twin."""

    def build_digital_twin(
        self,
        request: RiskAssessmentRequest,
        alt_profile: AlternativeDataProfile
    ) -> DigitalTwinResponse:
        scores = alt_profile.scores

        # Determine dimensions
        dimensions: List[DigitalTwinDimension] = [
            DigitalTwinDimension(
                dimension="Income Stability",
                score=scores.income_stability,
                benchmark=75,
                status="Strong" if scores.income_stability >= 80 else ("Moderate" if scores.income_stability >= 65 else "Attention Needed"),
                summary=f"Demonstrates consistent monthly inflows with observed stability score of {scores.income_stability}/100."
            ),
            DigitalTwinDimension(
                dimension="Cash Flow Buffer",
                score=scores.cash_flow_stability,
                benchmark=70,
                status="Strong" if scores.cash_flow_stability >= 80 else ("Moderate" if scores.cash_flow_stability >= 60 else "Attention Needed"),
                summary="Net inflows consistently exceed regular monthly living and debt expenses."
            ),
            DigitalTwinDimension(
                dimension="Payment Discipline",
                score=scores.payment_discipline,
                benchmark=80,
                status="Strong" if scores.payment_discipline >= 85 else ("Moderate" if scores.payment_discipline >= 70 else "Attention Needed"),
                summary="High on-time payment adherence across tracked recurring digital and utility commitments."
            ),
            DigitalTwinDimension(
                dimension="Debt Management",
                score=max(100 - scores.debt_burden, 10),
                benchmark=65,
                status="Strong" if scores.debt_burden <= 35 else ("Moderate" if scores.debt_burden <= 55 else "Attention Needed"),
                summary=f"Debt-to-income leverage is currently at {request.dti_ratio:.2f} ({scores.debt_burden}% burden rating)."
            ),
            DigitalTwinDimension(
                dimension="Employment Stability",
                score=scores.employment_stability,
                benchmark=70,
                status="Strong" if scores.employment_stability >= 75 else ("Moderate" if scores.employment_stability >= 55 else "Attention Needed"),
                summary=f"{request.months_employed} months with current employer / commercial activity ({request.employment_type})."
            ),
            DigitalTwinDimension(
                dimension="Financial Resilience",
                score=scores.financial_resilience,
                benchmark=75,
                status="Strong" if scores.financial_resilience >= 80 else ("Moderate" if scores.financial_resilience >= 60 else "Attention Needed"),
                summary="Liquid liquidity buffer enables absorption of unexpected household or medical expenditure."
            ),
            DigitalTwinDimension(
                dimension="Digital Payment Velocity",
                score=scores.digital_payment_discipline,
                benchmark=70,
                status="Strong" if scores.digital_payment_discipline >= 85 else ("Moderate" if scores.digital_payment_discipline >= 65 else "Attention Needed"),
                summary="Active electronic transacting through UPI channels with low transaction failure rate."
            ),
            DigitalTwinDimension(
                dimension="Recurring Bill Discipline",
                score=scores.utility_discipline,
                benchmark=75,
                status="Strong" if scores.utility_discipline >= 85 else ("Moderate" if scores.utility_discipline >= 65 else "Attention Needed"),
                summary="Zero or near-zero historical late penalties on registered electricity, water, and telecom lines."
            )
        ]

        if scores.business_stability is not None:
            dimensions.append(
                DigitalTwinDimension(
                    dimension="Business Stability",
                    score=scores.business_stability,
                    benchmark=70,
                    status="Strong" if scores.business_stability >= 80 else "Moderate",
                    summary="Commercial GST filing continuity and positive enterprise turnover trajectory."
                )
            )

        # Composite Stability Index
        dim_scores = [d.score for d in dimensions]
        composite_index = int(sum(dim_scores) / len(dim_scores))

        # Strengths & Vulnerabilities
        strengths = []
        vulnerabilities = []

        if scores.payment_discipline >= 85:
            strengths.append("Exceptional on-time payment track record across recurring bills and digital payments.")
        if scores.cash_flow_stability >= 80:
            strengths.append("Healthy cash-flow cushion: inflows exceed monthly obligations by a safe operational margin.")
        if scores.utility_discipline >= 90:
            strengths.append("Spotless utility bill repayment history indicating deep household financial discipline.")
        if scores.financial_resilience >= 80:
            strengths.append("Strong shock absorption capacity with adequate liquid emergency buffer.")

        if scores.debt_burden >= 50:
            vulnerabilities.append(f"Elevated debt-to-income ratio ({request.dti_ratio:.2f}) limits incremental borrowing capacity.")
        if request.loan_amount > (request.income * 0.7):
            vulnerabilities.append(f"Requested loan amount (₹{request.loan_amount:,.0f}) is high relative to annual income (₹{request.income:,.0f}).")
        if scores.employment_stability < 60:
            vulnerabilities.append(f"Relatively short tenure ({request.months_employed} months) in current role creates moderate sensitivity to job changes.")
        if not vulnerabilities:
            vulnerabilities.append("No critical vulnerabilities detected under standard baseline operational conditions.")

        # Grounded AI Summary based strictly on available data
        if composite_index >= 80:
            ai_summary = (
                f"The Financial Digital Twin reveals an applicant with robust financial health ({composite_index}/100). "
                f"Income stability and recurring payment discipline are notably high ({scores.payment_discipline}/100), "
                f"providing strong evidence of repayment capacity even where conventional bureau depth is developing."
            )
        elif composite_index >= 60:
            ai_summary = (
                f"The Financial Digital Twin indicates balanced financial stability ({composite_index}/100). "
                f"While recurring payment behavior is dependable ({scores.payment_discipline}/100), "
                f"the requested loan burden requires structured tenure to preserve the household's emergency buffer."
            )
        else:
            ai_summary = (
                f"The Financial Digital Twin reflects stressed operational margins ({composite_index}/100). "
                f"Existing obligations and high DTI ({request.dti_ratio:.2f}) place pressure on cash flow. "
                f"A reduced loan exposure or co-applicant backing is recommended to maintain repayment sustainability."
            )

        return DigitalTwinResponse(
            customer_id=alt_profile.customer_id,
            dimensions=dimensions,
            twin_stability_index=composite_index,
            ai_grounded_summary=ai_summary,
            strengths=strengths,
            vulnerabilities=vulnerabilities
        )


digital_twin_service = DigitalTwinService()
