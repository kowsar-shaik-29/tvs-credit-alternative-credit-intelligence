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
from app.schemas.nirnay_enhancements import (
    HealthTimelineMilestone,
    FinancialHealthTimelineResponse
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

    def generate_health_timeline(
        self,
        customer_id: str,
        alt_profile: AlternativeDataProfile
    ) -> FinancialHealthTimelineResponse:
        """Generates a 4-month simulated post-disbursal financial health trajectory."""
        scores = alt_profile.scores

        m1 = HealthTimelineMilestone(
            period="Month 1",
            health_status="Stable",
            headline="Disbursal & Mandate Activation",
            trigger_event="First scheduled auto-debit cleared successfully on due date.",
            financial_impact="Bank cash buffer intact; initial debt service ratio established at healthy baseline.",
            recommended_action="Maintain automated NACH mandate active; continue standard digital receipts."
        )

        m2_status = "Stable" if scores.payment_discipline >= 60 else "Watch"
        m2 = HealthTimelineMilestone(
            period="Month 2",
            health_status=m2_status,
            headline="Recurring Digital Inflows Verified",
            trigger_event="Consistent UPI transactions and utility payments recorded on schedule.",
            financial_impact="Payment streak builds positive behavioral score (+3.2% stability lift).",
            recommended_action="Continue timely settlement of recurring telecom and electricity obligations."
        )

        m3_status = "Watch" if scores.cash_flow_stability < 75 else "Stable"
        m3 = HealthTimelineMilestone(
            period="Month 3",
            health_status=m3_status,
            headline="Liquidity Buffer Observation",
            trigger_event="Short 4-day settlement variance observed on one utility invoice.",
            financial_impact="Cash buffer remains positive (1.3x monthly EMI) despite minor timing friction.",
            recommended_action="TVS Credit proactive reminder SMS sent 48 hours prior to EMI date to safeguard zero-bounce status."
        )

        m4_status = "Early Warning" if (scores.debt_burden > 60 or scores.cash_flow_stability < 60) else "Stable"
        m4_impact = (
            "Seasonal expenditure pressures slightly tighten disposable headroom."
            if m4_status == "Early Warning"
            else "Sustained stability allows automated eligibility for credit line top-up."
        )
        m4_action = (
            "Proactive option to activate TVS Flexi-Tenure (extend by 6 months) if seasonal pressure persists."
            if m4_status == "Early Warning"
            else "Fast-track pre-approved top-up loan offer dispatched via customer WhatsApp portal."
        )
        m4 = HealthTimelineMilestone(
            period="Month 4",
            health_status=m4_status,
            headline="Quarterly Performance Review",
            trigger_event="Assessment of 90-day post-disbursal repayment record across all consented feeds.",
            financial_impact=m4_impact,
            recommended_action=m4_action
        )

        return FinancialHealthTimelineResponse(
            customer_id=customer_id,
            current_period="Month 1 (Disbursal Active)",
            milestones=[m1, m2, m3, m4],
            proactive_guidance=(
                "NIRNAY Continuous Surveillance uses non-intrusive consented milestones to protect borrower cash flow "
                "and provide proactive repayment flexibility before formal delinquency occurs."
            )
        )


monitoring_service = MonitoringService()
