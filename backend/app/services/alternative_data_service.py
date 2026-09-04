"""Synthetic alternative-data service for TVS Credit NIRNAY.

Generates realistic, deterministic demo data across authorized alternative-data
providers for credit-invisible and thin-file customer archetypes.
"""

from typing import Dict, Any, List, Optional
from app.schemas.risk import RiskAssessmentRequest
from app.schemas.nirnay import (
    ConsentItem,
    BankCashFlowData,
    UPIDigitalData,
    UtilityHistoryData,
    TelecomHistoryData,
    GSTBusinessData,
    TVSRepaymentData,
    AlternativeScores,
    AlternativeDataProfile
)


# Standard 7 Consent Sources
DEFAULT_CONSENT_SOURCES = [
    ConsentItem(
        source_id="bank_cash_flow",
        name="Bank Account Cash Flow",
        category="Banking",
        purpose="Understand recurring income regularity, monthly cash-flow buffer, and expense pressure.",
        data_accessed="Monthly net inflows, average outflows, minimum balance, recurring debits (via Account Aggregator).",
        impact_description="Demonstrates liquidity buffer even if traditional bureau score is absent.",
        is_connected=True,
        consent_granted=True,
        status_label="Consent Granted",
        is_simulated=True
    ),
    ConsentItem(
        source_id="upi_digital",
        name="UPI & Digital Payment Behaviour",
        category="Digital Transactions",
        purpose="Evaluate transaction velocity, digital payment discipline, and cash velocity.",
        data_accessed="Monthly UPI volumes, merchant QR payments, recurring subscription debits, failure rate.",
        impact_description="Validates regular commercial activity and transaction consistency.",
        is_connected=True,
        consent_granted=True,
        status_label="Consent Granted",
        is_simulated=True
    ),
    ConsentItem(
        source_id="utility_payments",
        name="Utility Payment History",
        category="Household Obligations",
        purpose="Verify household payment discipline and residential stability through recurring utility bills.",
        data_accessed="Electricity (State Discom), Water, Piped Gas/LPG, Broadband payment timelines over 12-24 months.",
        impact_description="Strong on-time utility payments act as a direct proxy for credit repayment willingness.",
        is_connected=True,
        consent_granted=True,
        status_label="Consent Granted",
        is_simulated=True
    ),
    ConsentItem(
        source_id="mobile_bill",
        name="Mobile & Telecom Bill History",
        category="Telecom",
        purpose="Assess recurring postpaid / prepaid recharge discipline and contact stability.",
        data_accessed="Monthly telecom billing amount, on-time payment record, operator tenure.",
        impact_description="Reflects financial discipline on personal recurring monthly obligations.",
        is_connected=True,
        consent_granted=True,
        status_label="Consent Granted",
        is_simulated=True
    ),
    ConsentItem(
        source_id="gst_business",
        name="GST & Merchant Commercial Signals",
        category="Commercial",
        purpose="Evaluate micro-enterprise turnover, GST filing timeliness, and commercial cash generation.",
        data_accessed="GSTIN filing frequency (GSTR-3B), reported quarterly turnover, seasonal revenue volatility.",
        impact_description="Enables higher credit limits for self-employed shopkeepers, traders, and small merchants.",
        is_connected=True,
        consent_granted=True,
        status_label="Consent Granted",
        is_simulated=True
    ),
    ConsentItem(
        source_id="tvs_repayment",
        name="TVS Credit Internal Repayment History",
        category="Internal Portfolio",
        purpose="Leverage historical repayment performance across previous TVS Credit two-wheeler, tractor, or consumer loans.",
        data_accessed="Previous loan accounts, tenure, bounce history, on-time closure certificate.",
        impact_description="Prior positive relationship with TVS Credit accelerates decisioning and lowers interest rate.",
        is_connected=True,
        consent_granted=True,
        status_label="Consent Granted",
        is_simulated=True
    ),
    ConsentItem(
        source_id="uploaded_docs",
        name="Uploaded Financial Statements & KYC",
        category="Document Verification",
        purpose="Verify verified salary slips, ITR acknowledgment, or land holding records.",
        data_accessed="PDF salary credit receipts, Form 16, or Aadhaar-masked e-KYC documents.",
        impact_description="Authenticates baseline income and identity attributes.",
        is_connected=True,
        consent_granted=True,
        status_label="Consent Granted",
        is_simulated=True
    )
]


class AlternativeDataService:
    """Service generating and processing alternative credit signals."""

    def get_default_consents(self) -> List[ConsentItem]:
        """Return a copy of the default 7 consent items."""
        return [c.model_copy() for c in DEFAULT_CONSENT_SOURCES]

    def identify_archetype(self, request: RiskAssessmentRequest) -> str:
        """Infer customer archetype based on request attributes."""
        if request.credit_score == 650 and request.age == 30 and request.income == 50000:
            return "notebook_demo"
        if request.credit_score <= 450 and request.dti_ratio >= 0.70:
            return "high_risk"
        if request.employment_type == "Self-employed" or request.loan_purpose == "Business":
            return "small_merchant"
        if request.employment_type == "Part-time" and request.months_employed < 24:
            return "gig_worker"
        if request.num_credit_lines == 0 or (request.credit_score >= 600 and request.months_employed < 18):
            return "first_time_borrower"
        if request.income >= 90000 and request.credit_score >= 720:
            return "strong_alternative"
        if request.loan_purpose in ["Auto", "Other"] and request.income < 40000:
            return "rural_customer"
        return "thin_file_stable"

    def generate_alternative_profile(
        self,
        request: RiskAssessmentRequest,
        customer_id: str = "TVS-CUST-10492",
        consents: Optional[List[ConsentItem]] = None,
        archetype: Optional[str] = None
    ) -> AlternativeDataProfile:
        """Generate comprehensive simulated alternative data matching the applicant's profile."""
        if not archetype or archetype == "custom":
            archetype = self.identify_archetype(request)
        monthly_income = max(request.income / 12.0, 1000.0)
        observed_months = max(min(request.months_employed, 36), 6)

        # Consent mapping
        consent_dict = {}
        if consents:
            consent_dict = {c.source_id: c.consent_granted for c in consents}
        else:
            consent_dict = {c.source_id: True for c in DEFAULT_CONSENT_SOURCES}

        # Profile generators based on archetype
        if archetype == "first_time_borrower":
            # Young or entry-level: zero traditional credit, but excellent digital & utility discipline
            bank = BankCashFlowData(
                average_monthly_inflow=round(monthly_income * 1.02, 2),
                average_monthly_outflow=round(monthly_income * 0.72, 2),
                cash_flow_stability=86.0,
                income_consistency=90.0,
                minimum_monthly_balance=round(monthly_income * 0.28, 2),
                recurring_expenses=round(monthly_income * 0.40, 2),
                inflow_outflow_ratio=1.41,
                months_of_observed_history=observed_months
            ) if consent_dict.get("bank_cash_flow", True) else None

            upi = UPIDigitalData(
                transaction_count_monthly=48,
                average_transaction_amount=380.0,
                monthly_transaction_volume=round(monthly_income * 0.45, 2),
                payment_consistency=94.0,
                failed_transaction_rate=1.2,
                recurring_payment_consistency=92.0,
                digital_payment_discipline=93.0
            ) if consent_dict.get("upi_digital", True) else None

            utility = UtilityHistoryData(
                bills_paid=observed_months,
                bills_on_time=max(observed_months - 1, 1),
                missed_payments=0,
                average_bill_amount=1450.0,
                payment_consistency=96.0,
                utility_payment_discipline=95.0,
                months_of_history=observed_months
            ) if consent_dict.get("utility_payments", True) else None

            telecom = TelecomHistoryData(
                average_monthly_bill=499.0,
                bills_paid_on_time=observed_months,
                missed_payments=0,
                average_payment_delay_days=0.5,
                payment_consistency=98.0,
                months_of_history=observed_months
            ) if consent_dict.get("mobile_bill", True) else None

            gst = GSTBusinessData(is_applicable=False)

            tvs = TVSRepaymentData(
                has_history=False,
                relationship_notes="First-time applicant. No prior TVS borrowing relationship."
            )

            scores = AlternativeScores(
                payment_discipline=94,
                income_stability=88,
                cash_flow_stability=86,
                utility_discipline=95,
                digital_payment_discipline=93,
                employment_stability=max(int(min(request.months_employed / 36.0, 1.0) * 80 + 15), 35),
                business_stability=None,
                debt_burden=min(max(int(request.dti_ratio * 100), 10), 95),
                financial_resilience=85
            )

        elif archetype == "small_merchant":
            # Self-employed shopkeeper/merchant: active GST, daily UPI QR collections
            bank = BankCashFlowData(
                average_monthly_inflow=round(monthly_income * 1.35, 2),
                average_monthly_outflow=round(monthly_income * 0.95, 2),
                cash_flow_stability=82.0,
                income_consistency=84.0,
                minimum_monthly_balance=round(monthly_income * 0.35, 2),
                recurring_expenses=round(monthly_income * 0.55, 2),
                inflow_outflow_ratio=1.42,
                months_of_observed_history=observed_months
            ) if consent_dict.get("bank_cash_flow", True) else None

            upi = UPIDigitalData(
                transaction_count_monthly=142,
                average_transaction_amount=620.0,
                monthly_transaction_volume=round(monthly_income * 1.15, 2),
                payment_consistency=91.0,
                failed_transaction_rate=0.8,
                recurring_payment_consistency=88.0,
                digital_payment_discipline=90.0
            ) if consent_dict.get("upi_digital", True) else None

            utility = UtilityHistoryData(
                bills_paid=observed_months,
                bills_on_time=max(observed_months - 2, 1),
                missed_payments=0,
                average_bill_amount=3850.0,
                payment_consistency=93.0,
                utility_payment_discipline=92.0,
                months_of_history=observed_months
            ) if consent_dict.get("utility_payments", True) else None

            telecom = TelecomHistoryData(
                average_monthly_bill=899.0,
                bills_paid_on_time=max(observed_months - 3, 1),
                missed_payments=0,
                average_payment_delay_days=1.2,
                payment_consistency=92.0,
                months_of_history=observed_months
            ) if consent_dict.get("mobile_bill", True) else None

            gst = GSTBusinessData(
                is_applicable=True,
                business_name="Commercial Merchant Trade Facility",
                business_tenure_years=round(request.months_employed / 12.0, 1),
                monthly_revenue_trend="Consistent / Seasonal Uplift",
                gst_filing_consistency=95.0,
                revenue_stability=88.0,
                business_cash_flow_stability=85.0,
                seasonal_volatility="Moderate (Festival peaks)"
            ) if consent_dict.get("gst_business", True) else None

            rel_note = (
                "Completed TVS Two-Wheeler loan with 100% on-time record."
                if request.loan_purpose == "Auto"
                else f"Completed prior TVS {request.loan_purpose} credit facility with 100% on-time record."
            )
            tvs = TVSRepaymentData(
                has_history=True,
                previous_loans_count=1,
                repayment_consistency=96.0,
                on_time_payments=max(observed_months - 2, 1),
                missed_payments=0,
                completed_loans=1,
                relationship_notes=rel_note
            ) if consent_dict.get("tvs_repayment", True) else None

            scores = AlternativeScores(
                payment_discipline=92,
                income_stability=85,
                cash_flow_stability=83,
                utility_discipline=92,
                digital_payment_discipline=90,
                employment_stability=max(int(min(request.months_employed / 48.0, 1.0) * 75 + 15), 35),
                business_stability=88,
                debt_burden=min(max(int(request.dti_ratio * 100), 10), 95),
                financial_resilience=84
            )

        elif archetype == "gig_worker":
            # Delivery or rideshare partner: variable daily payouts, high UPI activity, low bureau lines
            bank = BankCashFlowData(
                average_monthly_inflow=round(monthly_income * 1.05, 2),
                average_monthly_outflow=round(monthly_income * 0.82, 2),
                cash_flow_stability=78.0,
                income_consistency=79.0,
                minimum_monthly_balance=round(monthly_income * 0.18, 2),
                recurring_expenses=round(monthly_income * 0.45, 2),
                inflow_outflow_ratio=1.28,
                months_of_observed_history=observed_months
            ) if consent_dict.get("bank_cash_flow", True) else None

            upi = UPIDigitalData(
                transaction_count_monthly=95,
                average_transaction_amount=240.0,
                monthly_transaction_volume=round(monthly_income * 0.65, 2),
                payment_consistency=89.0,
                failed_transaction_rate=1.8,
                recurring_payment_consistency=86.0,
                digital_payment_discipline=88.0
            ) if consent_dict.get("upi_digital", True) else None

            utility = UtilityHistoryData(
                bills_paid=observed_months,
                bills_on_time=max(observed_months - 1, 1),
                missed_payments=0,
                average_bill_amount=1150.0,
                payment_consistency=90.0,
                utility_payment_discipline=89.0,
                months_of_history=observed_months
            ) if consent_dict.get("utility_payments", True) else None

            telecom = TelecomHistoryData(
                average_monthly_bill=399.0,
                bills_paid_on_time=observed_months,
                missed_payments=0,
                average_payment_delay_days=0.8,
                payment_consistency=94.0,
                months_of_history=observed_months
            ) if consent_dict.get("mobile_bill", True) else None

            gst = GSTBusinessData(is_applicable=False)

            tvs = TVSRepaymentData(
                has_history=False,
                relationship_notes=f"New platform partner applicant ({request.employment_type}) applying for {request.loan_purpose} financing."
            )

            scores = AlternativeScores(
                payment_discipline=89,
                income_stability=78,
                cash_flow_stability=77,
                utility_discipline=89,
                digital_payment_discipline=88,
                employment_stability=max(int(min(request.months_employed / 24.0, 1.0) * 70 + 15), 30),
                business_stability=None,
                debt_burden=min(max(int(request.dti_ratio * 100), 10), 95),
                financial_resilience=76
            )

        elif archetype == "rural_customer":
            # Semi-urban or agri allied: seasonal cash spikes, prompt TVS rural repayment
            bank = BankCashFlowData(
                average_monthly_inflow=round(monthly_income * 1.10, 2),
                average_monthly_outflow=round(monthly_income * 0.70, 2),
                cash_flow_stability=79.0,
                income_consistency=81.0,
                minimum_monthly_balance=round(monthly_income * 0.30, 2),
                recurring_expenses=round(monthly_income * 0.35, 2),
                inflow_outflow_ratio=1.57,
                months_of_observed_history=observed_months
            ) if consent_dict.get("bank_cash_flow", True) else None

            upi = UPIDigitalData(
                transaction_count_monthly=32,
                average_transaction_amount=450.0,
                monthly_transaction_volume=round(monthly_income * 0.45, 2),
                payment_consistency=88.0,
                failed_transaction_rate=1.5,
                recurring_payment_consistency=87.0,
                digital_payment_discipline=86.0
            ) if consent_dict.get("upi_digital", True) else None

            utility = UtilityHistoryData(
                bills_paid=observed_months,
                bills_on_time=max(observed_months - 1, 1),
                missed_payments=0,
                average_bill_amount=880.0,
                payment_consistency=94.0,
                utility_payment_discipline=93.0,
                months_of_history=observed_months
            ) if consent_dict.get("utility_payments", True) else None

            telecom = TelecomHistoryData(
                average_monthly_bill=349.0,
                bills_paid_on_time=observed_months,
                missed_payments=0,
                average_payment_delay_days=1.1,
                payment_consistency=93.0,
                months_of_history=observed_months
            ) if consent_dict.get("mobile_bill", True) else None

            gst = GSTBusinessData(is_applicable=False)

            rel_note = (
                "Prior TVS Two-Wheeler loan serviced with spotless rural repayment track record."
                if request.loan_purpose == "Auto"
                else f"Prior TVS {request.loan_purpose} credit facility serviced with spotless rural repayment track record."
            )
            tvs = TVSRepaymentData(
                has_history=True,
                previous_loans_count=1,
                repayment_consistency=95.0,
                on_time_payments=max(observed_months - 2, 1),
                missed_payments=0,
                completed_loans=1,
                relationship_notes=rel_note
            ) if consent_dict.get("tvs_repayment", True) else None

            scores = AlternativeScores(
                payment_discipline=91,
                income_stability=81,
                cash_flow_stability=80,
                utility_discipline=93,
                digital_payment_discipline=86,
                employment_stability=max(int(min(request.months_employed / 48.0, 1.0) * 70 + 15), 35),
                business_stability=None,
                debt_burden=min(max(int(request.dti_ratio * 100), 10), 95),
                financial_resilience=82
            )

        elif archetype == "high_risk":
            # High indebtedness, negative cash flow, delayed bills
            bank = BankCashFlowData(
                average_monthly_inflow=round(monthly_income * 0.95, 2),
                average_monthly_outflow=round(monthly_income * 0.98, 2),
                cash_flow_stability=44.0,
                income_consistency=52.0,
                minimum_monthly_balance=round(monthly_income * 0.04, 2),
                recurring_expenses=round(monthly_income * 0.72, 2),
                inflow_outflow_ratio=0.97,
                months_of_observed_history=observed_months
            ) if consent_dict.get("bank_cash_flow", True) else None

            upi = UPIDigitalData(
                transaction_count_monthly=22,
                average_transaction_amount=310.0,
                monthly_transaction_volume=round(monthly_income * 0.25, 2),
                payment_consistency=54.0,
                failed_transaction_rate=9.8,
                recurring_payment_consistency=48.0,
                digital_payment_discipline=50.0
            ) if consent_dict.get("upi_digital", True) else None

            on_time_util = max(int(observed_months * 0.6), 1)
            utility = UtilityHistoryData(
                bills_paid=observed_months,
                bills_on_time=on_time_util,
                missed_payments=observed_months - on_time_util,
                average_bill_amount=1650.0,
                payment_consistency=58.0,
                utility_payment_discipline=52.0,
                months_of_history=observed_months
            ) if consent_dict.get("utility_payments", True) else None

            on_time_tel = max(int(observed_months * 0.5), 1)
            telecom = TelecomHistoryData(
                average_monthly_bill=599.0,
                bills_paid_on_time=on_time_tel,
                missed_payments=observed_months - on_time_tel,
                average_payment_delay_days=8.4,
                payment_consistency=52.0,
                months_of_history=observed_months
            ) if consent_dict.get("mobile_bill", True) else None

            gst = GSTBusinessData(is_applicable=False)

            tvs = TVSRepaymentData(
                has_history=True,
                previous_loans_count=1,
                repayment_consistency=58.0,
                on_time_payments=max(int(observed_months * 0.6), 1),
                missed_payments=3,
                overdue_history=True,
                completed_loans=0,
                relationship_notes="Existing loan with delayed EMI payments observed in history."
            ) if consent_dict.get("tvs_repayment", True) else None

            scores = AlternativeScores(
                payment_discipline=51,
                income_stability=50,
                cash_flow_stability=44,
                utility_discipline=52,
                digital_payment_discipline=50,
                employment_stability=max(min(int(request.months_employed / 36.0 * 50 + 20), 65), 25),
                business_stability=None,
                debt_burden=min(max(int(request.dti_ratio * 100), 10), 95),
                financial_resilience=42
            )

        elif archetype == "strong_alternative":
            # Prime earner: large cash flow buffer, high savings rate, flawless utility
            bank = BankCashFlowData(
                average_monthly_inflow=round(monthly_income * 1.15, 2),
                average_monthly_outflow=round(monthly_income * 0.55, 2),
                cash_flow_stability=94.0,
                income_consistency=96.0,
                minimum_monthly_balance=round(monthly_income * 0.85, 2),
                recurring_expenses=round(monthly_income * 0.30, 2),
                inflow_outflow_ratio=2.09,
                months_of_observed_history=observed_months
            ) if consent_dict.get("bank_cash_flow", True) else None

            upi = UPIDigitalData(
                transaction_count_monthly=62,
                average_transaction_amount=950.0,
                monthly_transaction_volume=round(monthly_income * 0.45, 2),
                payment_consistency=97.0,
                failed_transaction_rate=0.4,
                recurring_payment_consistency=98.0,
                digital_payment_discipline=97.0
            ) if consent_dict.get("upi_digital", True) else None

            utility = UtilityHistoryData(
                bills_paid=observed_months,
                bills_on_time=observed_months,
                missed_payments=0,
                average_bill_amount=2850.0,
                payment_consistency=100.0,
                utility_payment_discipline=98.0,
                months_of_history=observed_months
            ) if consent_dict.get("utility_payments", True) else None

            telecom = TelecomHistoryData(
                average_monthly_bill=999.0,
                bills_paid_on_time=observed_months,
                missed_payments=0,
                average_payment_delay_days=0.0,
                payment_consistency=100.0,
                months_of_history=observed_months
            ) if consent_dict.get("mobile_bill", True) else None

            gst = GSTBusinessData(is_applicable=False)

            rel_note = (
                "Two prior TVS loans completed with flawless zero-bounce records."
                if request.loan_purpose == "Auto"
                else f"Prior TVS {request.loan_purpose} credit facility completed with flawless zero-bounce records."
            )
            tvs = TVSRepaymentData(
                has_history=True,
                previous_loans_count=2,
                repayment_consistency=99.0,
                on_time_payments=observed_months,
                missed_payments=0,
                completed_loans=2,
                relationship_notes=rel_note
            ) if consent_dict.get("tvs_repayment", True) else None

            scores = AlternativeScores(
                payment_discipline=98,
                income_stability=96,
                cash_flow_stability=94,
                utility_discipline=98,
                digital_payment_discipline=97,
                employment_stability=max(int(min(request.months_employed / 48.0, 1.0) * 75 + 20), 40),
                business_stability=None,
                debt_burden=min(max(int(request.dti_ratio * 100), 10), 95),
                financial_resilience=95
            )

        else:
            # Default / Notebook reference profile / Thin-file stable
            bank = BankCashFlowData(
                average_monthly_inflow=round(monthly_income * 1.05, 2),
                average_monthly_outflow=round(monthly_income * 0.74, 2),
                cash_flow_stability=84.0,
                income_consistency=87.0,
                minimum_monthly_balance=round(monthly_income * 0.25, 2),
                recurring_expenses=round(monthly_income * 0.42, 2),
                inflow_outflow_ratio=1.42,
                months_of_observed_history=observed_months
            ) if consent_dict.get("bank_cash_flow", True) else None

            upi = UPIDigitalData(
                transaction_count_monthly=38,
                average_transaction_amount=420.0,
                monthly_transaction_volume=round(monthly_income * 0.35, 2),
                payment_consistency=92.0,
                failed_transaction_rate=1.4,
                recurring_payment_consistency=90.0,
                digital_payment_discipline=89.0
            ) if consent_dict.get("upi_digital", True) else None

            utility = UtilityHistoryData(
                bills_paid=observed_months,
                bills_on_time=max(observed_months - 1, 1),
                missed_payments=0,
                average_bill_amount=1650.0,
                payment_consistency=95.0,
                utility_payment_discipline=94.0,
                months_of_history=observed_months
            ) if consent_dict.get("utility_payments", True) else None

            telecom = TelecomHistoryData(
                average_monthly_bill=549.0,
                bills_paid_on_time=max(observed_months - 1, 1),
                missed_payments=0,
                average_payment_delay_days=0.7,
                payment_consistency=96.0,
                months_of_history=observed_months
            ) if consent_dict.get("mobile_bill", True) else None

            gst = GSTBusinessData(is_applicable=False)

            tvs = TVSRepaymentData(
                has_history=False,
                relationship_notes=f"No prior TVS credit history for {request.loan_purpose} financing."
            )

            scores = AlternativeScores(
                payment_discipline=92,
                income_stability=84,
                cash_flow_stability=87,
                utility_discipline=95,
                digital_payment_discipline=89,
                employment_stability=max(int(min(request.months_employed / 48.0, 1.0) * 75 + 15), 35),
                business_stability=None,
                debt_burden=min(max(int(request.dti_ratio * 100), 10), 95),
                financial_resilience=86
            )

        name_map = {
            "notebook_demo": "Arun Kumar (Notebook Reference)",
            "first_time_borrower": "Rahul Sharma (First-Time Borrower)",
            "small_merchant": "M. Lakshmi Narayanan (Kirana Merchant)",
            "gig_worker": "Vikram Sen (Platform Delivery Partner)",
            "rural_customer": "Suresh Patel (Kisan Allied & Rural)",
            "strong_alternative": "Deepa Sundaram (Prime Alternative Profile)",
            "high_risk": "Prakash Verma (Stressed Leverage)",
            "thin_file_stable": "Ananya Roy (Thin-File Salaried)"
        }

        # Check if request matches a known preset customer's inputs
        known_presets = {
            "notebook_demo": (30, 50000.0, 36, 40000.0, 36, 650, 0.30),
            "first_time_borrower": (23, 42000.0, 14, 25000.0, 24, 610, 0.20),
            "strong_alternative": (45, 135000.0, 72, 60000.0, 36, 780, 0.18),
            "thin_file_stable": (34, 38000.0, 40, 20000.0, 24, 630, 0.22),
            "gig_worker": (27, 35000.0, 16, 18000.0, 18, 590, 0.28),
            "small_merchant": (41, 75000.0, 54, 80000.0, 36, 660, 0.32),
            "rural_customer": (38, 32000.0, 48, 28000.0, 30, 620, 0.24),
            "high_risk": (29, 28000.0, 12, 65000.0, 36, 420, 0.78)
        }
        matched_preset = None
        for p_key, (p_age, p_inc, p_mo, p_loan, p_term, p_cs, p_dti) in known_presets.items():
            if (request.age == p_age and abs(request.income - p_inc) < 1.0 and
                request.months_employed == p_mo and abs(request.loan_amount - p_loan) < 1.0 and
                request.loan_term == p_term and request.credit_score == p_cs and
                abs(request.dti_ratio - p_dti) < 0.01):
                matched_preset = p_key
                break

        if matched_preset and matched_preset in name_map:
            customer_name = name_map[matched_preset]
        else:
            customer_name = f"Applicant ({request.employment_type} • {request.loan_purpose} Loan)"

        return AlternativeDataProfile(
            customer_id=customer_id,
            customer_name=customer_name,
            archetype_name=archetype.replace("_", " ").title(),
            bank_cash_flow=bank,
            upi_digital=upi,
            utility_history=utility,
            telecom_history=telecom,
            gst_business=gst,
            tvs_repayment=tvs,
            scores=scores
        )


alternative_data_service = AlternativeDataService()
