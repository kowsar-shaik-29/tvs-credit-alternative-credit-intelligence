"""Service for TVS Credit NIRNAY Financial Health Passport & Evidence Confidence."""

from typing import List
from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import AlternativeDataProfile, ConsentItem, AlternativeCreditIndicators
from app.schemas.nirnay_enhancements import (
    FinancialHealthPassport,
    EvidenceConfidence,
    ConsentIntelligenceItem,
    ConsentIntelligenceResponse
)


class PassportService:
    """Generates customer-facing Financial Health Passport and Evidence Confidence ratings."""

    def generate_passport(
        self,
        request: RiskAssessmentRequest,
        alt_profile: AlternativeDataProfile,
        resilience_score: int,
        indicators: AlternativeCreditIndicators
    ) -> FinancialHealthPassport:
        """Constructs compact multi-dimensional Financial Health Passport."""
        income_stab = int(alt_profile.scores.income_stability)
        pay_disc = int(alt_profile.scores.payment_discipline)
        # Repayment capacity (0-1 float mapped to 0-100)
        repay_cap = int(min(max(indicators.repayment_capacity * 100.0, 10.0), 100.0))
        # Debt burden
        debt_burden = int(alt_profile.scores.debt_burden)
        emp_stab = int(alt_profile.scores.employment_stability)
        resilience = int(resilience_score)

        # Composite health score
        # Higher is better: reverse debt burden in composite
        composite_health = int(
            (income_stab * 0.20) +
            (pay_disc * 0.25) +
            (repay_cap * 0.20) +
            (max(100 - debt_burden, 0) * 0.15) +
            (emp_stab * 0.10) +
            (resilience * 0.10)
        )
        composite_health = max(min(composite_health, 100), 0)

        if composite_health >= 75:
            overall_status = "HEALTHY"
            tier = "Gold Verified"
            badge = "TVS Prime Eligible"
        elif composite_health >= 55:
            overall_status = "STABLE"
            tier = "Silver Emerging"
            badge = "TVS Growth Pathway"
        else:
            overall_status = "WATCH"
            tier = "Bronze Thin-File"
            badge = "Assisted Structuring"

        return FinancialHealthPassport(
            customer_id=alt_profile.customer_id,
            customer_name=alt_profile.customer_name,
            passport_tier=tier,
            income_stability_score=income_stab,
            payment_discipline_score=pay_disc,
            repayment_capacity_score=repay_cap,
            debt_burden_score=debt_burden,
            employment_stability_score=emp_stab,
            financial_resilience_score=resilience,
            overall_health_status=overall_status,
            badge_label=badge
        )

    def evaluate_evidence_confidence(
        self,
        consents: List[ConsentItem],
        alt_profile: AlternativeDataProfile,
        request: RiskAssessmentRequest
    ) -> EvidenceConfidence:
        """Determines how much consented, verifiable alternative signal evidence backs the assessment."""
        total_sources = len(consents) if consents else 7
        consented_count = sum(1 for c in consents if c.consent_granted) if consents else 4

        strong: List[str] = []
        limited: List[str] = []

        # 1. Payment discipline signal
        if alt_profile.scores.payment_discipline >= 70:
            strong.append("Verified on-time digital & utility payment discipline")
        else:
            limited.append("Recent utility or digital settlement consistency gaps")

        # 2. Cash flow regularity
        if alt_profile.bank_cash_flow and alt_profile.scores.cash_flow_stability >= 65:
            strong.append("Continuous monthly bank deposit buffer & cash flow regularity")
        else:
            limited.append("Limited depth in continuous banking cash flow history")

        # 3. Employment tenure
        if request.months_employed >= 24:
            strong.append(f"Substantial verified employment tenure ({request.months_employed} months)")
        else:
            limited.append(f"Early-stage employment tenure ({request.months_employed} months observed)")

        # 4. Bureau score presence
        if request.credit_score >= 650:
            strong.append(f"Established credit bureau baseline (CIBIL/Bureau: {request.credit_score})")
        else:
            limited.append(f"Limited/thin traditional bureau depth (Score: {request.credit_score})")

        # 5. Commercial / GST
        if alt_profile.gst_business and alt_profile.gst_business.is_applicable:
            strong.append("Verified commercial tax & GST invoice filing history")
        else:
            limited.append("No formal commercial GST / corporate registration record")

        # Compute confidence score
        # Base from consent coverage (up to 40 pts)
        consent_ratio = consented_count / max(total_sources, 1)
        consent_score = consent_ratio * 40.0

        # Quality from verified signals (up to 60 pts)
        signal_score = (len(strong) / max(len(strong) + len(limited), 1)) * 60.0
        confidence_val = int(consent_score + signal_score)
        confidence_val = max(min(confidence_val, 96), 42)

        if confidence_val >= 78:
            level = "High Evidence"
        elif confidence_val >= 60:
            level = "Moderate Evidence"
        else:
            level = "Emerging Evidence"

        return EvidenceConfidence(
            evidence_confidence_score=confidence_val,
            confidence_level=level,
            consented_sources_count=consented_count,
            total_sources_count=total_sources,
            data_completeness_pct=round((consented_count / max(total_sources, 1)) * 100.0, 1),
            strong_evidence=strong[:4],
            limited_evidence=limited[:3]
        )

    def generate_consent_intelligence(
        self,
        consents: List[ConsentItem],
        customer_id: str
    ) -> ConsentIntelligenceResponse:
        """Enhances consent items with clear purpose, derived signal, data retention, and customer controls."""
        details_map = {
            "bank_cash_flow": {
                "name": "Bank Account Cash Flow",
                "used_for": "Evaluating income regularity, average month-end balance, and cash buffer",
                "derived_signal": "Cash Flow Stability Score & Repayment Buffer Indicator",
                "retention": "Not displayed / not retained in prototype"
            },
            "upi_digital": {
                "name": "UPI & Digital Payments",
                "used_for": "Verifying transaction frequency, merchant payment habits, and digital activity",
                "derived_signal": "Digital Payment Discipline (0-100) & Volume Index",
                "retention": "Not displayed / not retained in prototype"
            },
            "utility_payments": {
                "name": "Electricity & Water Bills",
                "used_for": "Observing recurring household payment discipline and delinquency risk",
                "derived_signal": "Utility Payment Discipline & Delay Penalty Index",
                "retention": "Not displayed / not retained in prototype"
            },
            "mobile_bill": {
                "name": "Telecom & Mobile Recharge",
                "used_for": "Checking mobile plan stability, payment punctuality, and connection tenure",
                "derived_signal": "Telecom Consistency & Stability Score",
                "retention": "Not displayed / not retained in prototype"
            },
            "gst_business": {
                "name": "GST & Commercial Invoices",
                "used_for": "Validating small merchant revenues, seasonal turnover, and GST filing regularity",
                "derived_signal": "Business Cash Flow Stability & Commercial Resilience",
                "retention": "Not displayed / not retained in prototype"
            },
            "tvs_repayment": {
                "name": "TVS Credit Relationship History",
                "used_for": "Rewarding past two-wheeler loan settlements and internal brand loyalty",
                "derived_signal": "TVS Ecosystem Loyalty Bonus & Preferred Pricing Eligibility",
                "retention": "Not displayed / not retained in prototype"
            },
            "uploaded_docs": {
                "name": "Income Statements & Rent Slips",
                "used_for": "Corroborating declared informal earnings and fixed monthly obligations",
                "derived_signal": "Document Verification Authenticity & Disposable Income Multiplier",
                "retention": "Not displayed / not retained in prototype"
            }
        }

        intelligence_items: List[ConsentIntelligenceItem] = []
        for c in consents:
            meta = details_map.get(c.source_id, {
                "name": c.name,
                "used_for": c.purpose,
                "derived_signal": c.impact_description,
                "retention": "Not displayed / not retained in prototype"
            })
            intelligence_items.append(
                ConsentIntelligenceItem(
                    source_id=c.source_id,
                    name=meta["name"],
                    used_for=meta["used_for"],
                    derived_signal=meta["derived_signal"],
                    raw_data_retention=meta["retention"],
                    customer_control="Grant | Review | Withdraw",
                    consent_granted=c.consent_granted,
                    status_label="Consent Granted" if c.consent_granted else "Consent Withdrawn",
                    is_simulated=True
                )
            )

        active_count = sum(1 for c in consents if c.consent_granted)

        return ConsentIntelligenceResponse(
            customer_id=customer_id,
            sources=intelligence_items,
            active_consents_count=active_count,
            total_sources_count=len(consents)
        )


passport_service = PassportService()
