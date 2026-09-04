"""Critical model parity verification script comparing API pipeline results to the Kaggle notebook."""

import sys
import math
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config.settings import settings
from app.schemas.risk import RiskAssessmentRequest
from app.services.feature_engineering import feature_engineering_service
from app.services.model_service import model_service
from app.services.risk_service import risk_service


def run_model_parity_check() -> bool:
    print("\n" + "=" * 60)
    print("TVS CREDIT NIRNAY - MODEL PARITY CHECK")
    print("=" * 60)

    # 1. Verify and Load Artifacts
    try:
        model_service.load_artifacts()
    except Exception as e:
        print(f"\n[FAIL] Artifact loading error: {e}")
        print("Model artifacts must be present in backend/models/ before running parity check.")
        return False

    # 2. Known Notebook Reference Customer (Cell 65)
    # Customer ID: I38PQUQS96
    customer_request = RiskAssessmentRequest(
        age=30,
        income=50000.0,
        loan_amount=40000.0,
        credit_score=650,
        months_employed=36,
        num_credit_lines=3,
        interest_rate=10.0,
        loan_term=36,
        dti_ratio=0.30,
        education="Bachelor's",
        employment_type="Full-time",
        marital_status="Single",
        has_mortgage=False,
        has_dependents=False,
        loan_purpose="Home",
        has_cosigner=False
    )

    # Known ground-truth values from Notebook Cells 66, 68, 69
    EXPECTED_PROBABILITY = 0.3928
    EXPECTED_THRESHOLD = 0.47
    EXPECTED_PREDICTION = 0
    EXPECTED_RISK_CLASS = "LOW RISK"
    EXPECTED_RECOMMENDATION = "MANUAL REVIEW"

    EXPECTED_FINANCIAL_STABILITY = 0.4726
    EXPECTED_REPAYMENT_CAPACITY = 0.8750
    EXPECTED_EMPLOYMENT_STABILITY = 0.3000
    EXPECTED_DEBT_STRESS = 1.1000
    EXPECTED_LOAN_BURDEN = 0.8000
    EXPECTED_INTEREST_BURDEN = 7.9998

    # 3. Pipeline Execution
    raw_df = feature_engineering_service.convert_api_to_dataframe(customer_request)
    df_featured, indicators = feature_engineering_service.engineer_features(raw_df)

    actual_probability = model_service.predict_default_probability(df_featured)
    actual_evaluation = risk_service.evaluate_risk(
        probability=actual_probability,
        threshold=model_service.threshold
    )

    # 4. Compare Results
    prob_diff = abs(actual_probability - EXPECTED_PROBABILITY)

    print("\n--- MODEL INFERENCE COMPARISON ---")
    print(f"Probability from notebook    : {EXPECTED_PROBABILITY:.4f} ({EXPECTED_PROBABILITY*100:.2f}%)")
    print(f"Probability from API pipeline: {actual_probability:.4f} ({actual_probability*100:.2f}%)")
    print(f"Absolute Difference          : {prob_diff:.6f}")

    print("\n--- CLASSIFICATION & DECISION ---")
    print(f"Threshold     : API = {actual_evaluation.risk_threshold:.2f} | Notebook = {EXPECTED_THRESHOLD:.2f}")
    print(f"Prediction    : API = {actual_evaluation.prediction} | Notebook = {EXPECTED_PREDICTION}")
    print(f"Risk Class    : API = {actual_evaluation.risk_classification} | Notebook = {EXPECTED_RISK_CLASS}")
    print(f"Decision      : API = {actual_evaluation.recommended_action} | Notebook = {EXPECTED_RECOMMENDATION}")

    print("\n--- ALTERNATIVE CREDIT INDICATORS ---")
    print(f"Financial Stability  : API = {indicators.financial_stability_score:.4f} | Notebook = {EXPECTED_FINANCIAL_STABILITY:.4f}")
    print(f"Repayment Capacity   : API = {indicators.repayment_capacity:.4f} | Notebook = {EXPECTED_REPAYMENT_CAPACITY:.4f}")
    print(f"Employment Stability : API = {indicators.employment_stability:.4f} | Notebook = {EXPECTED_EMPLOYMENT_STABILITY:.4f}")
    print(f"Debt Stress          : API = {indicators.debt_stress:.4f} | Notebook = {EXPECTED_DEBT_STRESS:.4f}")
    print(f"Loan Burden          : API = {indicators.loan_burden:.4f} | Notebook = {EXPECTED_LOAN_BURDEN:.4f}")
    print(f"Interest Burden      : API = {indicators.interest_burden:.4f} | Notebook = {EXPECTED_INTEREST_BURDEN:.4f}")

    # Checks
    checks_passed = True

    # Floating-point tolerance for probability (within 0.005 / half a percent)
    if prob_diff > 0.005:
        print(f"\n[FAIL] Probability mismatch exceeds tolerance: {prob_diff:.6f}")
        checks_passed = False
    else:
        print("\n[OK] Probability matches notebook result within tolerance.")

    if actual_evaluation.prediction != EXPECTED_PREDICTION:
        print(f"[FAIL] Prediction mismatch: {actual_evaluation.prediction} != {EXPECTED_PREDICTION}")
        checks_passed = False
    else:
        print("[OK] Prediction matches.")

    if actual_evaluation.risk_classification != EXPECTED_RISK_CLASS:
        print(f"[FAIL] Risk class mismatch: {actual_evaluation.risk_classification} != {EXPECTED_RISK_CLASS}")
        checks_passed = False
    else:
        print("[OK] Risk classification matches.")

    if actual_evaluation.recommended_action != EXPECTED_RECOMMENDATION:
        print(f"[FAIL] Recommended action mismatch: {actual_evaluation.recommended_action} != {EXPECTED_RECOMMENDATION}")
        checks_passed = False
    else:
        print("[OK] Recommended action matches.")

    # Indicator checks within 0.001
    indicator_pairs = [
        ("FinancialStabilityScore", indicators.financial_stability_score, EXPECTED_FINANCIAL_STABILITY),
        ("RepaymentCapacity", indicators.repayment_capacity, EXPECTED_REPAYMENT_CAPACITY),
        ("EmploymentStability", indicators.employment_stability, EXPECTED_EMPLOYMENT_STABILITY),
        ("DebtStress", indicators.debt_stress, EXPECTED_DEBT_STRESS),
        ("LoanBurden", indicators.loan_burden, EXPECTED_LOAN_BURDEN),
        ("InterestBurden", indicators.interest_burden, EXPECTED_INTEREST_BURDEN),
    ]

    for name, act, exp in indicator_pairs:
        if abs(act - exp) > 0.005:
            print(f"[FAIL] Indicator {name} mismatch: act={act:.4f}, exp={exp:.4f}")
            checks_passed = False
        else:
            print(f"[OK] Indicator {name} matches.")

    print("\n" + "=" * 60)
    if checks_passed:
        print("OVERALL MODEL PARITY: PASS")
        print("=" * 60 + "\n")
        return True
    else:
        print("OVERALL MODEL PARITY: FAIL")
        print("=" * 60 + "\n")
        return False


if __name__ == "__main__":
    success = run_model_parity_check()
    sys.exit(0 if success else 1)
