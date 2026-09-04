"""Stress Simulation service for TVS Credit NIRNAY.

Evaluates 7 distinct financial shock scenarios to determine loan affordability
and repayment resilience under adverse household circumstances.
"""

from typing import List
from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import (
    AlternativeDataProfile,
    StressScenarioResult,
    StressSimulationResponse
)
from app.services.resilience_service import resilience_service


class StressService:
    """Simulates economic stress conditions on repayment feasibility."""

    def run_stress_test(
        self,
        request: RiskAssessmentRequest,
        alt_profile: AlternativeDataProfile
    ) -> StressSimulationResponse:
        monthly_income = max(request.income / 12.0, 1000.0)
        monthly_debt = monthly_income * request.dti_ratio
        est_monthly_emi = (request.loan_amount / max(request.loan_term, 1)) * (1.0 + request.interest_rate / 100.0)
        baseline_living_expenses = max(monthly_income * 0.45, 500.0)

        baseline_resilience = resilience_service.calculate_resilience(request, alt_profile.scores)
        baseline_capacity = max(0.0, 1.0 - (monthly_debt + est_monthly_emi) / (monthly_income + 1.0))
        baseline_risk = "Low Risk" if baseline_resilience >= 75 else ("Moderate Risk" if baseline_resilience >= 55 else "High Risk")

        scenarios_definitions = [
            {
                "id": "scenario_inc_minus_10",
                "name": "Scenario 1: Income decreases by 10%",
                "desc": "Simulates modest business slowdown or overtime reduction.",
                "inc_mult": 0.90,
                "exp_mult": 1.00,
                "missed_penalty": 0,
                "resilience_delta": -8
            },
            {
                "id": "scenario_inc_minus_20",
                "name": "Scenario 2: Income decreases by 20%",
                "desc": "Simulates significant sector slump or reduced commercial orders.",
                "inc_mult": 0.80,
                "exp_mult": 1.00,
                "missed_penalty": 0,
                "resilience_delta": -18
            },
            {
                "id": "scenario_inc_minus_30",
                "name": "Scenario 3: Income decreases by 30%",
                "desc": "Severe macro shock or dual-earner income interruption.",
                "inc_mult": 0.70,
                "exp_mult": 1.00,
                "missed_penalty": 0,
                "resilience_delta": -32
            },
            {
                "id": "scenario_exp_plus_10",
                "name": "Scenario 4: Monthly expenses increase by 10%",
                "desc": "Inflationary spike in food, utilities, and fuel costs.",
                "inc_mult": 1.00,
                "exp_mult": 1.10,
                "missed_penalty": 0,
                "resilience_delta": -7
            },
            {
                "id": "scenario_exp_plus_20",
                "name": "Scenario 5: Monthly expenses increase by 20%",
                "desc": "Unplanned family medical expense or essential asset maintenance.",
                "inc_mult": 1.00,
                "exp_mult": 1.20,
                "missed_penalty": 0,
                "resilience_delta": -16
            },
            {
                "id": "scenario_missed_payment",
                "name": "Scenario 6: One recurring payment is delayed",
                "desc": "Simulates a temporary liquidity mismatch causing a single late billing debit.",
                "inc_mult": 1.00,
                "exp_mult": 1.05,
                "missed_penalty": 1,
                "resilience_delta": -12
            },
            {
                "id": "scenario_income_interruption",
                "name": "Scenario 7: 30-day income pause / transition",
                "desc": "Job transition or temporary gig platform suspension for 1 month.",
                "inc_mult": 0.40,
                "exp_mult": 0.90,
                "missed_penalty": 0,
                "resilience_delta": -42
            }
        ]

        scenario_results: List[StressScenarioResult] = []

        for sc in scenarios_definitions:
            s_income = monthly_income * sc["inc_mult"]
            s_expenses = (baseline_living_expenses * sc["exp_mult"]) + monthly_debt
            s_free_cash = s_income - s_expenses
            s_emi_buffer = s_free_cash - est_monthly_emi

            s_resilience = max(int(baseline_resilience + sc["resilience_delta"]), 12)
            s_capacity = max(0.0, min(1.0, 1.0 - (s_expenses + est_monthly_emi) / (s_income + 1.0)))

            if s_emi_buffer >= (est_monthly_emi * 0.35):
                affordability = "Comfortable"
                risk_level = "Low"
                rec = "Applicant retains sufficient surplus to service loan with zero modification."
            elif s_emi_buffer >= 0:
                affordability = "Manageable"
                risk_level = "Moderate"
                rec = "Repayment is feasible; recommending 6-month tenure extension to lower monthly EMI burden."
            elif s_emi_buffer >= -(est_monthly_emi * 0.30):
                affordability = "Strained"
                risk_level = "High"
                rec = "Deficit under stress; recommend reducing loan principal by 25% or attaching a co-signer."
            else:
                affordability = "Critical"
                risk_level = "Critical"
                rec = "Significant cash deficit under this scenario; structured emergency buffer or restructuring required."

            scenario_results.append(
                StressScenarioResult(
                    scenario_id=sc["id"],
                    scenario_name=sc["name"],
                    description=sc["desc"],
                    stressed_income=round(s_income, 2),
                    stressed_expenses=round(s_expenses, 2),
                    stressed_affordability=affordability,
                    repayment_capacity=round(s_capacity, 4),
                    resilience_score=s_resilience,
                    risk_level=risk_level,
                    recommendation=rec,
                    estimated_emi_buffer=round(s_emi_buffer, 2)
                )
            )

        return StressSimulationResponse(
            baseline_resilience=baseline_resilience,
            baseline_risk=baseline_risk,
            baseline_capacity=round(baseline_capacity, 4),
            scenarios=scenario_results
        )


stress_service = StressService()
