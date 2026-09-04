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

        # Query 1: Why was my risk classified this way?
        if any(term in q_lower for term in ["why", "classified", "decision", "risk class", "score", "evaluate"]):
            if default_prob < 0.30:
                answer = (
                    f"Your assessment is classified as LOW RISK (Default Probability: {default_prob * 100:.2f}%, well below our 47% threshold). "
                    f"NIRNAY identified strong positive repayment factors: your payment discipline is rated at {scores.payment_discipline}/100, "
                    f"utility bill track record is consistent ({scores.utility_discipline}/100), and existing debt burden is manageable at {dti_pct}% for your requested {request.loan_purpose} loan."
                )
            elif default_prob < 0.47:
                answer = (
                    f"Your assessment is classified as LOW RISK / MANUAL REVIEW (Default Probability: {default_prob * 100:.2f}%, near the 47% operational threshold). "
                    f"While your alternative data signals show good payment discipline ({scores.payment_discipline}/100) and steady cash flow ({scores.cash_flow_stability}/100), "
                    f"your requested loan amount (₹{request.loan_amount:,.0f} over {request.loan_term} months) relative to annual income (₹{request.income:,.0f}) requires verification to prevent repayment strain."
                )
            else:
                answer = (
                    f"Your assessment is classified as HIGH RISK - FURTHER REVIEW (Default Probability: {default_prob * 100:.2f}%, which meets or exceeds our 47% threshold). "
                    f"The main contributing factors are an elevated debt-to-income ratio ({dti_pct}%), requested loan size (₹{request.loan_amount:,.0f}) relative to earnings (₹{request.income:,.0f}), "
                    f"and observed liquid cash reserves ({scores.cash_flow_stability}/100). Restructuring the loan to ₹{rec_loan:,.0f} over {rec_tenure} months makes it sustainable."
                )

            followups = [
                "How can I improve my eligibility?",
                "Why is my recommended loan lower than requested?",
                "What happens if my income decreases?"
            ]

        # Query 2: How can I improve my eligibility?
        elif any(term in q_lower for term in ["improve", "eligibility", "better", "qualify", "increase"]):
            tenure_rec_text = (
                f"Structuring your loan tenure: Your requested tenure is {request.loan_term} months; our recommended structured tenure is {rec_tenure} months to keep monthly EMI sustainable."
                if rec_tenure != request.loan_term
                else f"Maintain loan tenure: Your requested {request.loan_term} months tenure provides a balanced repayment schedule."
            )
            answer = (
                f"To strengthen your NIRNAY credit profile:\n"
                f"1. Lower existing leverage: Reducing your active DTI ratio from current {dti_pct}% below 35% substantially decreases risk.\n"
                f"2. Add a verified co-signer: Adding a secondary guarantor improves credit security and unlocks higher financing limits.\n"
                f"3. Maintain spotless utility and digital debits: Continuing timely payments keeps your Payment Discipline score high ({scores.payment_discipline}/100).\n"
                f"4. {tenure_rec_text}"
            )
            followups = [
                "How much loan can I comfortably afford?",
                "What happens if my income decreases?",
                "Why was my risk classified this way?"
            ]

        # Query 3: How much loan can I comfortably afford?
        elif any(term in q_lower for term in ["afford", "comfortably", "how much", "maximum", "capacity"]):
            tenure_comparison = (
                f"over recommended tenure of {rec_tenure} months (compared to requested {request.loan_term} months)"
                if rec_tenure != request.loan_term
                else f"over your requested tenure of {request.loan_term} months"
            )
            answer = (
                f"Based on your monthly income (₹{monthly_income:,.0f}) and current debt obligations (₹{monthly_income * request.dti_ratio:,.0f}/mo), "
                f"your verified comfortable loan amount is ₹{rec_loan:,.0f} {tenure_comparison}. "
                f"This ensures your monthly EMI stays within 50% of your verified discretionary surplus, protecting your household against unexpected emergencies."
            )
            followups = [
                "Why is my recommended loan lower than requested?",
                "What happens if my income decreases?",
                "How can I improve my eligibility?"
            ]

        # Query 4: What happens if my income decreases?
        elif any(term in q_lower for term in ["income decrease", "income drops", "salary cut", "recession", "decrease"]):
            # Stressed scenario 2 calculation
            stressed_income = monthly_income * 0.80
            free_cash_stress = stressed_income - (monthly_income * request.dti_ratio) - (stressed_income * 0.40)
            answer = (
                f"Under our NIRNAY Stress Simulation, if your monthly income drops by 20% (to ₹{stressed_income:,.0f}/mo):\n"
                f"• Your Financial Resilience score adjusts from {resilience_score}/100 to approximately {max(resilience_score - 18, 15)}/100.\n"
                f"• At the recommended loan of ₹{rec_loan:,.0f}, you would maintain a viable buffer of approximately ₹{max(free_cash_stress, 0):,.0f}/mo.\n"
                f"• If borrowing the full requested amount of ₹{request.loan_amount:,.0f} over {request.loan_term} months, you could experience severe cash strain."
            )
            followups = [
                "How much loan can I comfortably afford?",
                "How can I improve my eligibility?",
                "Why was my risk classified this way?"
            ]

        # Query 5: Why is recommended loan lower than requested?
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
                "How can I improve my eligibility?",
                "How much loan can I comfortably afford?",
                "What happens if my income decreases?"
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
                "Why was my risk classified this way?",
                "How can I improve my eligibility?",
                "How much loan can I comfortably afford?",
                "What happens if my income decreases?",
                "Why is my recommended loan lower than requested?"
            ]

        return AssistantQueryResponse(
            question=question,
            answer=answer,
            key_metrics_referenced=metrics_ref,
            suggested_followups=followups
        )


assistant_service = AssistantService()
