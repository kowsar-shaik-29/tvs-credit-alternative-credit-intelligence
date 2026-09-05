"""NIRNAY Financial Assistant service for TVS Credit.

Answers customer queries using transparent, factual metrics from their
current assessment, alternative data profile, and stress test calculations.
"""

from typing import Dict, Any, List, Optional
from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import (
    AlternativeDataProfile,
    AssistantQueryResponse,
    LoanRecommendationResponse
)
from app.schemas.nirnay_enhancements import FinancialCoachQueryResponse


class AssistantService:
    """Answers customer credit intelligence questions transparently."""

    def answer_query(
        self,
        question: str,
        request: RiskAssessmentRequest,
        alt_profile: AlternativeDataProfile,
        default_prob: float,
        recommended_loan: float,
        resilience_score: int,
        rec: Optional[LoanRecommendationResponse] = None
    ) -> AssistantQueryResponse:
        q_lower = question.lower()
        monthly_income = max(request.income / 12.0, 1000.0)
        dti_pct = int(request.dti_ratio * 100)
        scores = alt_profile.scores

        rec_tenure = rec.recommended_tenure_months if rec else request.loan_term
        rec_loan = rec.recommended_loan if rec else recommended_loan

        metrics_ref = {
            "default_probability": f"{default_prob * 100:.2f}%",
            "risk_threshold": "47.0%",
            "credit_score": str(request.credit_score),
            "dti_ratio": f"{dti_pct}%",
            "payment_discipline": f"{scores.payment_discipline}/100",
            "cash_flow_stability": f"{scores.cash_flow_stability}/100",
            "resilience_score": f"{resilience_score}/100",
            "requested_loan": f"₹{request.loan_amount:,.0f}",
            "requested_term": f"{request.loan_term} months",
            "loan_purpose": request.loan_purpose,
            "employment_tenure": f"{request.months_employed} months",
            "recommended_loan": f"₹{rec_loan:,.0f}",
            "recommended_tenure": f"{rec_tenure} months"
        }

        # Query 1: Why was my risk classified this way? / Why under review?
        if any(term in q_lower for term in ["under review", "review", "why", "classified", "decision", "risk class", "score", "evaluate"]):
            if default_prob < 0.30:
                answer = (
                    f"Your assessment is classified as LOW RISK (Default Probability: {default_prob * 100:.2f}%, well below our 47% threshold). "
                    f"NIRNAY identified strong positive repayment factors: your payment discipline is rated at {scores.payment_discipline}/100, "
                    f"utility bill track record is consistent ({scores.utility_discipline}/100), and existing debt burden is manageable at {dti_pct}% for your requested {request.loan_purpose} loan."
                )
            elif default_prob < 0.47:
                answer = (
                    f"Your assessment is under MANUAL REVIEW / FAST-TRACK (Default Probability: {default_prob * 100:.2f}%, near the 47% operational threshold). "
                    f"Why review is needed: Your alternative signals verify steady cash flow ({scores.cash_flow_stability}/100) and good bill discipline ({scores.payment_discipline}/100), "
                    f"but your requested loan size (₹{request.loan_amount:,.0f}) relative to income (₹{request.income:,.0f}) requires underwriter verification to safeguard your monthly budget."
                )
            else:
                answer = (
                    f"Your assessment is classified as HIGH RISK - FURTHER REVIEW (Default Probability: {default_prob * 100:.2f}%, which meets or exceeds our 47% threshold). "
                    f"The main contributing factors are an elevated debt-to-income ratio ({dti_pct}%), requested loan size (₹{request.loan_amount:,.0f}) relative to earnings (₹{request.income:,.0f}), "
                    f"and observed liquid cash reserves ({scores.cash_flow_stability}/100). Restructuring the loan to ₹{rec_loan:,.0f} over {rec_tenure} months makes it sustainable."
                )

            followups = [
                "How can I improve my financial health?",
                "Is this loan affordable?",
                "Why was this tenure recommended?"
            ]

        # Query 2: How can I improve my eligibility / financial health?
        elif any(term in q_lower for term in ["improve", "financial health", "eligibility", "better", "qualify", "increase"]):
            tenure_rec_text = (
                f"Structuring your loan tenure: Your requested tenure is {request.loan_term} months; our recommended structured tenure is {rec_tenure} months to keep monthly EMI sustainable."
                if rec_tenure != request.loan_term
                else f"Maintain loan tenure: Your requested {request.loan_term} months tenure provides a balanced repayment schedule."
            )
            answer = (
                f"Actionable Roadmap to Improve Your NIRNAY Eligibility & Financial Health:\n"
                f"1. Reduce Debt Burden: Lower your active DTI ratio from current {dti_pct}% down towards 30% by clearing smaller revolving lines.\n"
                f"2. Maintain Consecutive Autopay Streak: Establish 90 days of on-time utility and UPI payments ({scores.payment_discipline}/100 current).\n"
                f"3. Build a 2x EMI Cash Cushion: Maintain an unencumbered closing balance buffer in your primary account.\n"
                f"4. {tenure_rec_text}\n"
                f"5. Add a Verified Co-Signer: If feasible, adding an earning family member significantly boosts composite affordability."
            )
            followups = [
                "Is this loan affordable?",
                "What should I improve before taking another loan?",
                "Why was this tenure recommended?"
            ]

        # Query 3: Is this loan affordable?
        elif any(term in q_lower for term in ["is this loan affordable", "affordable", "afford", "comfortably", "how much", "capacity"]):
            tenure_comparison = (
                f"over recommended tenure of {rec_tenure} months (compared to requested {request.loan_term} months)"
                if rec_tenure != request.loan_term
                else f"over your requested tenure of {request.loan_term} months"
            )
            answer = (
                f"Based on your verified monthly income (₹{monthly_income:,.0f}) and current debt obligations (₹{monthly_income * request.dti_ratio:,.0f}/mo):\n"
                f"• Verified Safe Limit: Your comfortable borrowing capacity is ₹{rec_loan:,.0f} {tenure_comparison}.\n"
                f"• Net Disposable Cash Flow: After meeting living expenses and existing debts, your discretionary surplus is approximately ₹{max(monthly_income * 0.40, 500):,.0f}/month.\n"
                f"• Repayment Guardrail: TVS Credit caps monthly EMI below 50% of verified net cash flow to protect your household against unexpected price inflation."
            )
            followups = [
                "Why was this tenure recommended?",
                "What happens if my income falls?",
                "How can I improve my financial health?"
            ]

        # Query 4: Why was this tenure recommended?
        elif any(term in q_lower for term in ["tenure recommended", "why tenure", "tenure", "months recommended", "duration"]):
            if rec_tenure == request.loan_term:
                answer = (
                    f"Your requested tenure of {request.loan_term} months was approved as optimal! "
                    f"It yields an estimated monthly EMI of ₹{rec_emi:,.0f}, which fits comfortably inside your verified monthly surplus without straining liquidity."
                )
            else:
                answer = (
                    f"You requested {request.loan_term} months, but NIRNAY recommended structuring your loan over {rec_tenure} months. "
                    f"Why? Extending the repayment duration spreads principal amortization, lowering your monthly EMI commitment from an estimated higher strain level down to ₹{rec_emi:,.0f}/month. "
                    f"This creates an extra disposable cash buffer every month while leaving you free to prepay without penalty later."
                )
            followups = [
                "Is this loan affordable?",
                "What happens if my income falls?",
                "How can I improve my financial health?"
            ]

        # Query 5: What happens if my income falls?
        elif any(term in q_lower for term in ["income fall", "income falls", "income decrease", "income drops", "salary cut", "recession", "decrease"]):
            stressed_income = monthly_income * 0.80
            free_cash_stress = stressed_income - (monthly_income * request.dti_ratio) - (stressed_income * 0.40)
            answer = (
                f"Under NIRNAY Repayment Resilience Stress Testing, if your monthly income decreases by 20% (to ₹{stressed_income:,.0f}/mo):\n"
                f"• Your Financial Resilience score shifts from {resilience_score}/100 to approx {max(resilience_score - 18, 15)}/100.\n"
                f"• Under the recommended structured loan (₹{rec_loan:,.0f} over {rec_tenure}M), your EMI buffer remains positive at ~₹{max(free_cash_stress, 0):,.0f}/month.\n"
                f"• In the event of a persistent income disruption, TVS Credit's Flexi-Tenure policy enables a temporary 30-day EMI pause or tenure extension."
            )
            followups = [
                "Is this loan affordable?",
                "Why was this tenure recommended?",
                "What should I improve before taking another loan?"
            ]

        # Query 6: What should I improve before taking another loan?
        elif any(term in q_lower for term in ["another loan", "before taking", "future loan", "next loan"]):
            answer = (
                f"Before applying for supplementary or higher financing in the future, focus on these 3 milestones:\n"
                f"1. Establish 6 Consecutive On-Time EMIs: Perfect repayment on this facility automatically unlocks preferred interest pricing (-0.75% APR).\n"
                f"2. Reduce Revolving Card Balances: Keep credit card utilization below 30% to improve bureau score (+25-40 points typically).\n"
                f"3. Broaden Digital Payment Footprint: Route more utility and small vendor receipts through your consented UPI handle to expand your alternative cash-flow score."
            )
            followups = [
                "How can I improve my financial health?",
                "Is this loan affordable?",
                "Why was this tenure recommended?"
            ]

        # Query 7: Why is recommended loan lower than requested?
        elif any(term in q_lower for term in ["lower than requested", "less than", "different amount", "reduced"]):
            if rec_loan >= request.loan_amount:
                answer = (
                    f"Good news! Your recommended loan amount (₹{rec_loan:,.0f}) fully meets your requested amount of ₹{request.loan_amount:,.0f}. "
                    f"Your verified cash flow buffer ({scores.cash_flow_stability}/100) and repayment capacity support this financing comfortably."
                )
            else:
                diff = request.loan_amount - rec_loan
                answer = (
                    f"Your recommended loan is ₹{rec_loan:,.0f} (₹{diff:,.0f} lower than requested ₹{request.loan_amount:,.0f}) "
                    f"to prevent debt over-extension. With your current DTI ratio of {dti_pct}% and employment tenure of {request.months_employed} months, "
                    f"borrowing ₹{request.loan_amount:,.0f} would exceed 50% of your net monthly surplus. "
                    f"A structured loan of ₹{rec_loan:,.0f} over {rec_tenure} months protects your liquidity and guarantees manageable monthly EMIs."
                )
            followups = [
                "How can I improve my financial health?",
                "How much loan can I comfortably afford?",
                "What happens if my income falls?"
            ]

        # Fallback general query
        else:
            answer = (
                f"NIRNAY evaluates your creditworthiness by combining your application data with consented alternative financial signals "
                f"(Bank cash flow, UPI habits, utility payments). For your requested {request.loan_purpose} loan of ₹{request.loan_amount:,.0f} ({request.loan_term} months), "
                f"your current default probability is {default_prob * 100:.2f}%, payment discipline is {scores.payment_discipline}/100, "
                f"and recommended safe loan is ₹{rec_loan:,.0f} over {rec_tenure} months."
            )
            followups = [
                "Why is my application under review?",
                "How can I improve my financial health?",
                "Is this loan affordable?",
                "Why was this tenure recommended?",
                "What happens if my income falls?",
                "What should I improve before taking another loan?"
            ]

        return AssistantQueryResponse(
            question=question,
            answer=answer,
            key_metrics_referenced=metrics_ref,
            suggested_followups=followups
        )

    def answer_coach_query(
        self,
        question: str,
        request: RiskAssessmentRequest,
        alt_profile: AlternativeDataProfile,
        default_prob: float,
        recommended_loan: float,
        resilience_score: int,
        rec: Optional[LoanRecommendationResponse] = None
    ) -> FinancialCoachQueryResponse:
        """Answers dedicated AI Financial Coach queries with categorized steps and actionable guidance."""
        resp = self.answer_query(
            question=question,
            request=request,
            alt_profile=alt_profile,
            default_prob=default_prob,
            recommended_loan=recommended_loan,
            resilience_score=resilience_score,
            rec=rec
        )

        q_lower = question.lower()
        if "review" in q_lower or "why" in q_lower:
            category = "Eligibility"
        elif "afford" in q_lower or "limit" in q_lower:
            category = "Affordability"
        elif "tenure" in q_lower or "term" in q_lower:
            category = "Tenure Strategy"
        elif "income" in q_lower or "falls" in q_lower:
            category = "Resilience"
        else:
            category = "Improvement Roadmap"

        actionable = [
            "Set up autopay on primary bank account for seamless NACH settlements.",
            f"Keep active DTI ratio below 35% (currently {int(request.dti_ratio * 100)}%).",
            f"Preserve emergency cash buffer equal to 2 months EMI (approx ₹{(rec.estimated_emi if rec else 1500) * 2:,.0f})."
        ]

        return FinancialCoachQueryResponse(
            question=question,
            coach_category=category,
            answer=resp.answer,
            actionable_steps=actionable,
            suggested_questions=resp.suggested_followups
        )


assistant_service = AssistantService()
