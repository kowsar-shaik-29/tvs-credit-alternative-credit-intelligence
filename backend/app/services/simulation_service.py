"""Simulation service for TVS Credit NIRNAY: What-If Loan Simulator & Credit Improvement Roadmap."""

import math
from typing import Optional, List
from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import AlternativeDataProfile, AlternativeCreditIndicators
from app.schemas.nirnay_enhancements import (
    WhatIfSimulationResponse,
    LoanOptionSummary,
    CreditImprovementResponse,
    CreditImprovementItem
)
from app.services.resilience_service import resilience_service
from app.services.feature_engineering import feature_engineering_service
from app.services.model_service import model_service


def calculate_emi(principal: float, annual_rate_pct: float, tenure_months: int) -> float:
    """Standard reducing-balance Monthly EMI calculation."""
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    if annual_rate_pct <= 0:
        return round(principal / tenure_months, 2)

    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    try:
        factor = math.pow(1.0 + monthly_rate, tenure_months)
        emi = principal * monthly_rate * (factor / (factor - 1.0))
        return round(emi, 2)
    except (ZeroDivisionError, OverflowError):
        return round(principal / tenure_months, 2)


class SimulationService:
    """Handles What-If scenarios and Credit Improvement simulation."""

    def simulate_what_if(
        self,
        current_request: RiskAssessmentRequest,
        simulated_loan_amount: float,
        simulated_loan_term: int,
        simulated_interest_rate: float,
        alt_profile: AlternativeDataProfile,
        default_prob: float
    ) -> WhatIfSimulationResponse:
        """Evaluate how modified borrowing terms alter affordability, EMI, and stress resilience."""
        monthly_income = max(current_request.income / 12.0, 1000.0)

        # 1. Current Option Summary
        current_emi = calculate_emi(
            current_request.loan_amount,
            current_request.interest_rate,
            current_request.loan_term
        )
        current_dti_burden = (current_emi / monthly_income) + current_request.dti_ratio
        current_affordability = (
            "Comfortable" if current_dti_burden < 0.40
            else ("Manageable" if current_dti_burden < 0.65 else "Strained")
        )
        current_resilience = resilience_service.calculate_resilience(
            current_request, alt_profile.scores
        )
        current_summary = LoanOptionSummary(
            loan_amount=round(current_request.loan_amount, 2),
            loan_term=current_request.loan_term,
            interest_rate=round(current_request.interest_rate, 2),
            estimated_emi=round(current_emi, 2),
            affordability_status=current_affordability,
            monthly_free_cash_flow=round(max(monthly_income - current_emi, 0), 2),
            emi_to_income_ratio=round(current_emi / monthly_income, 4),
            resilience_score=current_resilience,
            risk_indicator="Low" if current_affordability == "Comfortable" else ("Moderate" if current_affordability == "Manageable" else "High"),
            default_probability=round(default_prob, 4)
        )

        # 2. Simulated Option Summary
        simulated_emi = calculate_emi(
            simulated_loan_amount,
            simulated_interest_rate,
            simulated_loan_term
        )
        sim_dti_burden = (simulated_emi / monthly_income) + current_request.dti_ratio
        sim_affordability = (
            "Comfortable" if sim_dti_burden < 0.40
            else ("Manageable" if sim_dti_burden < 0.65 else "Strained")
        )

        # Compute resilience under simulated terms
        sim_request = RiskAssessmentRequest(
            age=current_request.age,
            income=current_request.income,
            loan_amount=simulated_loan_amount,
            credit_score=current_request.credit_score,
            months_employed=current_request.months_employed,
            num_credit_lines=current_request.num_credit_lines,
            interest_rate=simulated_interest_rate,
            loan_term=simulated_loan_term,
            dti_ratio=current_request.dti_ratio,
            education=current_request.education,
            employment_type=current_request.employment_type,
            marital_status=current_request.marital_status,
            has_mortgage=current_request.has_mortgage,
            has_dependents=current_request.has_dependents,
            loan_purpose=current_request.loan_purpose,
            has_cosigner=current_request.has_cosigner
        )
        sim_resilience = resilience_service.calculate_resilience(
            sim_request, alt_profile.scores
        )

        # Calculate model probability for simulated loan if model service is ready
        sim_prob = None
        if model_service.is_ready:
            try:
                sim_df = feature_engineering_service.convert_api_to_dataframe(sim_request)
                sim_df_feat, _ = feature_engineering_service.engineer_features(sim_df)
                sim_prob = float(model_service.predict_default_probability(sim_df_feat))
            except Exception:
                sim_prob = None

        sim_summary = LoanOptionSummary(
            loan_amount=round(simulated_loan_amount, 2),
            loan_term=simulated_loan_term,
            interest_rate=round(simulated_interest_rate, 2),
            estimated_emi=round(simulated_emi, 2),
            affordability_status=sim_affordability,
            monthly_free_cash_flow=round(max(monthly_income - simulated_emi, 0), 2),
            emi_to_income_ratio=round(simulated_emi / monthly_income, 4),
            resilience_score=sim_resilience,
            risk_indicator="Low" if sim_affordability == "Comfortable" else ("Moderate" if sim_affordability == "Manageable" else "High"),
            default_probability=round(sim_prob, 4) if sim_prob is not None else None
        )

        # 3. TVS Structured Recommended Safer Alternative
        # Cap recommended loan to safe cash flow
        safe_max_loan = min(current_request.loan_amount, monthly_income * 0.45 * 24.0)
        safe_tenure = max(36, current_request.loan_term)
        safe_emi = calculate_emi(safe_max_loan, min(current_request.interest_rate, 11.5), safe_tenure)
        safer_summary = LoanOptionSummary(
            loan_amount=round(safe_max_loan, 2),
            loan_term=safe_tenure,
            interest_rate=round(min(current_request.interest_rate, 11.5), 2),
            estimated_emi=round(safe_emi, 2),
            affordability_status="Comfortable",
            monthly_free_cash_flow=round(max(monthly_income - safe_emi, 0), 2),
            emi_to_income_ratio=round(safe_emi / monthly_income, 4),
            resilience_score=min(current_resilience + 12, 98),
            risk_indicator="Low",
            default_probability=round(max(default_prob * 0.85, 0.05), 4)
        )

        # 4. Deltas and Comparison
        emi_diff = round(current_emi - simulated_emi, 2)
        res_diff = sim_resilience - current_resilience

        if emi_diff > 500:
            afford_impact = "Significant Improvement"
            comparison_verdict = (
                f"Simulated option lowers monthly EMI by ₹{emi_diff:,.0f}, freeing up essential disposable "
                f"cash buffer and boosting repayment resilience."
            )
        elif emi_diff < -500:
            afford_impact = "Increased Burden"
            comparison_verdict = (
                f"Simulated option increases monthly EMI by ₹{abs(emi_diff):,.0f}. Ensure your verifiable "
                f"monthly cash buffer comfortably accommodates this higher outflow."
            )
        else:
            afford_impact = "Modest Adjustment"
            comparison_verdict = (
                f"Simulated option produces a balanced EMI variation (₹{abs(emi_diff):,.0f}/mo difference) "
                f"with stable operational resilience."
            )

        return WhatIfSimulationResponse(
            current_option=current_summary,
            simulated_option=sim_summary,
            recommended_safer_option=safer_summary,
            emi_difference=emi_diff,
            resilience_difference=res_diff,
            affordability_impact=afford_impact,
            comparison_verdict=comparison_verdict
        )

    def generate_credit_improvement_plan(
        self,
        request: RiskAssessmentRequest,
        alt_profile: AlternativeDataProfile,
        indicators: Optional[AlternativeCreditIndicators] = None
    ) -> CreditImprovementResponse:
        """Synthesizes actionable, non-punitive credit improvement roadmap based on live metrics."""
        levers: List[CreditImprovementItem] = []
        monthly_income = max(request.income / 12.0, 1000.0)

        # Lever 1: Debt-to-Income (DTI) Optimization
        dti_pct = int(request.dti_ratio * 100)
        if dti_pct > 35:
            target_dti = 30
            debt_reduction_est = (dti_pct - target_dti) * monthly_income / 100.0
            levers.append(
                CreditImprovementItem(
                    area_key="debt_burden",
                    area_name="Reduce Existing Debt Burden (DTI)",
                    current_value_display=f"Current DTI: {dti_pct}% of verified monthly income",
                    target_recommendation=f"Pay down secondary credit cards or micro-loans to lower DTI below 30%",
                    timeframe_to_impact="30 - 60 Days",
                    potential_impact_label="High Affordability Impact",
                    action_steps=[
                        f"Consolidate or settle smaller revolving balances to free up ~₹{debt_reduction_est:,.0f}/month.",
                        "Avoid opening new retail credit lines before loan approval.",
                        "Maintain debt commitments below 35% of regular earnings."
                    ]
                )
            )
        else:
            levers.append(
                CreditImprovementItem(
                    area_key="debt_burden",
                    area_name="Maintain Healthy Leverage (DTI)",
                    current_value_display=f"Current DTI: {dti_pct}% (Well-Controlled)",
                    target_recommendation="Keep existing debt obligations below 30% threshold",
                    timeframe_to_impact="Ongoing",
                    potential_impact_label="Sustained Low Risk",
                    action_steps=[
                        "Continue timely settlement of credit card balances.",
                        "Ensure total monthly debt outflows do not exceed verified baseline."
                    ]
                )
            )

        # Lever 2: Payment Consistency & Alternative Discipline
        pay_disc = alt_profile.scores.payment_discipline
        if pay_disc < 85:
            levers.append(
                CreditImprovementItem(
                    area_key="payment_discipline",
                    area_name="Strengthen Digital & Utility Payment Discipline",
                    current_value_display=f"Alternative Payment Discipline: {pay_disc}/100",
                    target_recommendation="Establish a clean 90-day streak of on-time utility and UPI bill payments",
                    timeframe_to_impact="60 - 90 Days",
                    potential_impact_label="Direct Underwriting Score Boost",
                    action_steps=[
                        "Set up automated NACH or UPI autopay for electricity, broadband, and mobile recharge.",
                        "Ensure zero bounce on recurring auto-debits over the next 3 consecutive billing cycles.",
                        "Upload utility statements showing 6+ continuous on-time settlements."
                    ]
                )
            )
        else:
            levers.append(
                CreditImprovementItem(
                    area_key="payment_discipline",
                    area_name="Maintain High Payment Consistency",
                    current_value_display=f"Alternative Payment Discipline: {pay_disc}/100 (Strong)",
                    target_recommendation="Continue automated on-time digital bill settlements",
                    timeframe_to_impact="Sustained",
                    potential_impact_label="Prime Underwriting Tier",
                    action_steps=[
                        "Keep recurring bill autopay active across all verified utility accounts.",
                        "Preserve strong digital payment footprint."
                    ]
                )
            )

        # Lever 3: Loan Term & EMI Optimization
        est_current_emi = calculate_emi(request.loan_amount, request.interest_rate, request.loan_term)
        if request.loan_term < 36:
            extended_term = 36
            extended_emi = calculate_emi(request.loan_amount, request.interest_rate, extended_term)
            savings_mo = est_current_emi - extended_emi
            levers.append(
                CreditImprovementItem(
                    area_key="tenure_structuring",
                    area_name="Optimize Loan Tenure Structuring",
                    current_value_display=f"Requested Term: {request.loan_term} Months (EMI: ₹{est_current_emi:,.0f}/mo)",
                    target_recommendation=f"Extend tenure to {extended_term} months to reduce monthly EMI burden",
                    timeframe_to_impact="Immediate (Pre-Disbursal)",
                    potential_impact_label="Immediate Affordability Relief",
                    action_steps=[
                        f"Extending duration saves approximately ₹{savings_mo:,.0f} every month.",
                        "A lower EMI-to-income ratio significantly increases automated underwriting approval odds.",
                        "Pre-payment without penalty is supported once cash flow strengthens."
                    ]
                )
            )

        # Lever 4: Income Stability & Cash Flow Cushion
        cash_score = alt_profile.scores.cash_flow_stability
        levers.append(
            CreditImprovementItem(
                area_key="cash_flow_cushion",
                area_name="Expand Operational Cash Flow Cushion",
                current_value_display=f"Cash Flow Stability Score: {cash_score}/100",
                target_recommendation="Build and maintain an emergency reserve equal to 2x monthly EMI in primary account",
                timeframe_to_impact="60 - 90 Days",
                potential_impact_label="High Stress Resilience",
                action_steps=[
                    f"Aim for an unencumbered bank balance buffer of ₹{est_current_emi * 2:,.0f}.",
                    "Route regular client payments or salary through a single consented bank feed to verify stability.",
                    "Demonstrate positive month-end closing balances over 3 consecutive statements."
                ]
            )
        )

        # Lever 5: Security / Co-Signer Backing
        if not request.has_cosigner and alt_profile.scores.debt_burden > 50:
            levers.append(
                CreditImprovementItem(
                    area_key="cosigner_support",
                    area_name="Add Verified Co-Signer or Guarantor",
                    current_value_display="No Co-Signer Added",
                    target_recommendation="Include an earning family member or business partner as guarantor",
                    timeframe_to_impact="Immediate",
                    potential_impact_label="Unlocks Higher Financing",
                    action_steps=[
                        "A co-signer pools household income and mitigates individual credit score gaps.",
                        "Reduces risk classification from Manual Review to Fast-Track Eligibility."
                    ]
                )
            )

        readiness = int(
            (alt_profile.scores.payment_discipline * 0.35) +
            (max(100 - dti_pct, 10) * 0.35) +
            (alt_profile.scores.cash_flow_stability * 0.30)
        )
        readiness = max(min(readiness, 100), 25)

        return CreditImprovementResponse(
            customer_id=alt_profile.customer_id,
            overall_readiness_score=readiness,
            improvement_levers=levers,
            potential_monthly_savings_est=round(max(est_current_emi * 0.22, 450.0), 2)
        )


simulation_service = SimulationService()
