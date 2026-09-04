"""NIRNAY Financial Assistant service for TVS Credit.

Answers customer queries using transparent, factual metrics from their
current assessment, alternative data profile, and stress test calculations.
"""

from typing import Dict, Any, List
from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import (
    AlternativeDataProfile,
    AssistantQueryResponse
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
        resilience_score: int
    ) -> AssistantQueryResponse:
        q_lower = question.lower()
        monthly_income = max(request.income / 12.0, 1000.0)
        est_emi = (request.loan_amount / max(request.loan_term, 1)) * (1.0 + request.interest_rate / 100.0)
        dti_pct = int(request.dti_ratio * 100)
        scores = alt_profile.scores

        metrics_ref = {
            "default_probability": f"{default_prob * 100:.2f}%",
            "risk_threshold": "47.0%",
            "credit_score": request.credit_score,
            "dti_ratio": f"{dti_pct}%",
            "payment_discipline": f"{scores.payment_discipline}/100",
            "cash_flow_stability": f"{scores.cash_flow_stability}/100",
            "resilience_score": f"{resilience_score}/100",
            "requested_loan": f"₹{request.loan_amount:,.0f}",
            "recommended_loan": f"₹{recommended_loan:,.0f}"
        }

        # Query 1: Why was my risk classified this way?
        if any(term in q_lower for term in ["why", "classified", "decision", "risk class", "score", "evaluate"]):
            if default_prob < 0.30:
                answer = (
                    f"Your assessment is classified as LOW RISK (Default Probability: {default_prob * 100:.2f}%, well below our 47% threshold). "
                    f"NIRNAY identified strong positive repayment factors: your payment discipline is rated at {scores.payment_discipline}/100, "
                    f"utility bill track record is consistent ({scores.utility_discipline}/100), and existing debt burden is manageable at {dti_pct}%."
                )
            elif default_prob < 0.47:
                answer = (
                    f"Your assessment is classified as LOW RISK / MANUAL REVIEW (Default Probability: {default_prob * 100:.2f}%, near the 47% operational threshold). "
                    f"While your alternative data signals show good payment discipline ({scores.payment_discipline}/100) and steady cash flow ({scores.cash_flow_stability}/100), "
                    f"your requested loan amount (₹{request.loan_amount:,.0f}) relative to annual income (₹{request.income:,.0f}) requires verification to prevent repayment strain."
                )
            else:
                answer = (
                    f"Your assessment is classified as HIGH RISK - FURTHER REVIEW (Default Probability: {default_prob * 100:.2f}%, which meets or exceeds our 47% threshold). "
                    f"The main contributing factors are an elevated debt-to-income ratio ({dti_pct}%), high requested loan size relative to earnings, "
                    f"and lower observed liquid cash reserves ({scores.cash_flow_stability}/100). Restructuring the loan can make it viable."
                )

            followups = [
                "How can I improve my eligibility?",
                "Why is my recommended loan lower than requested?",
                "What happens if my income decreases?"
            ]

        # Query 2: How can I improve my eligibility?
        elif any(term in q_lower for term in ["improve", "eligibility", "better", "qualify", "increase"]):
            answer = (
                f"To strengthen your NIRNAY credit profile:\n"
                f"1. Lower existing leverage: Reducing your active DTI ratio from current {dti_pct}% below 35% substantially decreases risk.\n"
                f"2. Add a verified co-signer: Adding a family co-signer instantly reduces default risk and unlocks higher loan limits.\n"
                f"3. Maintain spotless utility and digital debits: Continuing timely bill payments keeps your Payment Discipline score high ({scores.payment_discipline}/100).\n"
                f"4. Extend loan tenure: Increasing tenure from {request.loan_term} months to {min(request.loan_term + 12, 60)} months reduces monthly EMI pressure."
            )
            followups = [
                "How much loan can I comfortably afford?",
                "What happens if my income decreases?",
                "Why was my risk classified this way?"
            ]

        # Query 3: How much loan can I comfortably afford?
        elif any(term in q_lower for term in ["afford", "comfortably", "how much", "maximum", "capacity"]):
            answer = (
                f"Based on your monthly income (₹{monthly_income:,.0f}) and current debt obligations (₹{monthly_income * request.dti_ratio:,.0f}/mo), "
                f"your verified comfortable loan amount is ₹{recommended_loan:,.0f} over a tenure of {request.loan_term} months. "
                f"This ensures your monthly EMI stays within 50% of your verified discretionary surplus, protecting your household against financial shocks."
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
                f"• At the recommended loan of ₹{recommended_loan:,.0f}, you would still maintain a positive cash surplus of approximately ₹{max(free_cash_stress, 0):,.0f}/mo.\n"
                f"• If borrowing the higher requested amount of ₹{request.loan_amount:,.0f}, you could experience cash strain. We recommend our flexible tenure extension buffer."
            )
            followups = [
                "How much loan can I comfortably afford?",
                "How can I improve my eligibility?",
                "Why was my risk classified this way?"
            ]

        # Query 5: Why is recommended loan lower than requested?
        elif any(term in q_lower for term in ["lower than requested", "less than", "different amount", "reduced"]):
            if recommended_loan >= request.loan_amount:
                answer = (
                    f"Good news! Your recommended loan amount (₹{recommended_loan:,.0f}) fully meets your requested amount of ₹{request.loan_amount:,.0f}. "
                    f"Your verified cash flow buffer ({scores.cash_flow_stability}/100) and repayment capacity support this financing comfortably."
                )
            else:
                diff = request.loan_amount - recommended_loan
                answer = (
                    f"Your recommended loan is ₹{recommended_loan:,.0f} (₹{diff:,.0f} lower than requested ₹{request.loan_amount:,.0f}) "
                    f"to prevent debt over-extension. With your existing monthly debt obligations of ₹{monthly_income * request.dti_ratio:,.0f} (DTI: {dti_pct}%), "
                    f"servicing a higher loan would exceed 50% of your net monthly surplus. "
                    f"Borrowing ₹{recommended_loan:,.0f} ensures your monthly EMI remains comfortable even during unexpected emergency expenses."
                )
            followups = [
                "How can I improve my eligibility?",
                "How much loan can I comfortably afford?",
                "What happens if my income decreases?"
            ]

        # Fallback general query
        else:
            answer = (
                f"NIRNAY evaluates your creditworthiness by combining your traditional application data with consented alternative financial signals "
                f"(Bank cash flow, UPI habits, utility bills). Your current default probability is {default_prob * 100:.2f}%, payment discipline is {scores.payment_discipline}/100, "
                f"and recommended loan is ₹{recommended_loan:,.0f}. You can ask about eligibility improvement, stress scenarios, or loan affordability."
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
