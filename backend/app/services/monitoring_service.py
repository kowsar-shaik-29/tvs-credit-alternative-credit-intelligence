"""Continuous Financial Health Monitoring service for TVS Credit NIRNAY.

Provides conceptual ongoing risk and early warning surveillance across
post-disbursal repayment behavior, cash-flow buffer changes, and utility delays.
"""

from typing import List
from app.schemas.nirnay import (
    AlternativeDataProfile,
    EarlyWarningAlert,
    FinancialHealthResponse
)


class MonitoringService:
    """Simulates ongoing financial health tracking and proactive early warning detection."""

    def evaluate_health(
        self,
        customer_id: str,
        alt_profile: AlternativeDataProfile,
        default_prob: float
    ) -> FinancialHealthResponse:
        scores = alt_profile.scores
        alerts: List[EarlyWarningAlert] = []

        if scores.cash_flow_stability >= 80 and scores.payment_discipline >= 85:
            health_status = "Stable"
            trend = "+5% cash buffer expansion over last 90 days"
            alerts.append(
                EarlyWarningAlert(
                    severity="Info",
                    title="Healthy Inflow Trajectory",
                    description="Monthly net deposits show consistent surpluses over average debits.",
                    metric_changed="Cash Flow Stability",
                    observed_trend="Improving (+4.2%)",
                    recommended_intervention="Eligible for automated credit limit enhancement upon 6 on-time EMIs."
                )
            )
        elif scores.cash_flow_stability >= 65:
            health_status = "Watch"
            trend = "Stable with seasonal variations (±4%)"
            alerts.append(
                EarlyWarningAlert(
                    severity="Watch",
                    title="Mild Inflow Variance",
                    description="Inflow variance detected around month-end period.",
                    metric_changed="Monthly Inflow Volatility",
                    observed_trend="Flat / Slightly volatile",
                    recommended_intervention="Schedule EMI auto-debit on 5th of each month aligned with peak deposit window."
                )
            )
        elif scores.cash_flow_stability >= 45:
            health_status = "Early Warning"
            trend = "-8% reduction in average monthly balance over previous cycle"
            alerts.append(
                EarlyWarningAlert(
                    severity="Early Warning",
                    title="Liquidity Buffer Compression",
                    description="Minimum monthly balance decreased by 8% relative to 90-day benchmark.",
                    metric_changed="Minimum Monthly Balance",
                    observed_trend="Decreasing (-8.1%)",
                    recommended_intervention="Proactive SMS reminder 3 days prior to EMI due date; provide flexible split-repayment option."
                )
            )
        else:
            health_status = "High Risk"
            trend = "-18% contraction in cash-flow buffer"
            alerts.append(
                EarlyWarningAlert(
                    severity="High Risk",
                    title="Elevated Debt Stress Detected",
                    description="Multiple non-loan recurring payments delayed over past 60 days.",
                    metric_changed="Payment Timeliness",
                    observed_trend="Declining",
                    recommended_intervention="Initiate dedicated relationship manager outreach for loan restructuring or tenure elongation."
                )
            )

        return FinancialHealthResponse(
            customer_id=customer_id,
            health_status=health_status,
            last_evaluation_period="Current Billing Cycle (Simulated)",
            stability_trend=trend,
            active_alerts=alerts
        )


monitoring_service = MonitoringService()
