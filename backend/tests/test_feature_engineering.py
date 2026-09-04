"""Unit tests for exact feature engineering formulas and financial stability calculations."""

import pytest
import pandas as pd
from app.schemas.risk import RiskAssessmentRequest
from app.services.feature_engineering import feature_engineering_service


@pytest.fixture
def sample_customer_request():
    """Known test customer from Kaggle notebook cell 65 (LoanID: I38PQUQS96)."""
    return RiskAssessmentRequest(
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


def test_normalization_params_loaded():
    params = feature_engineering_service.norm_params
    assert "CreditScore" in params
    assert "MonthsEmployed" in params
    assert "Income" in params
    assert "DTIRatio" in params
    assert params["CreditScore"]["min"] == 300.0
    assert params["CreditScore"]["max"] == 849.0
    assert params["MonthsEmployed"]["min"] == 0.0
    assert params["MonthsEmployed"]["max"] == 119.0
    assert params["Income"]["min"] == 15000.0
    assert params["Income"]["max"] == 149999.0
    assert params["DTIRatio"]["min"] == 0.1
    assert params["DTIRatio"]["max"] == 0.9


def test_api_to_dataframe_conversion(sample_customer_request):
    df = feature_engineering_service.convert_api_to_dataframe(sample_customer_request)
    assert df.shape == (1, 16)
    assert df["Age"].iloc[0] == 30.0
    assert df["Income"].iloc[0] == 50000.0
    assert df["HasMortgage"].iloc[0] == "No"
    assert df["HasDependents"].iloc[0] == "No"
    assert df["HasCoSigner"].iloc[0] == "No"


def test_exact_feature_engineering_math(sample_customer_request):
    df_raw = feature_engineering_service.convert_api_to_dataframe(sample_customer_request)
    df_featured, indicators = feature_engineering_service.engineer_features(df_raw)

    # 1. IncomeLoanRatio = 50000 / (40000 + 1) = 1.24996875...
    expected_ilr = 50000.0 / 40001.0
    assert abs(df_featured["IncomeLoanRatio"].iloc[0] - expected_ilr) < 1e-6

    # 2. EmploymentStability = 36 / 120 = 0.3
    assert abs(df_featured["EmploymentStability"].iloc[0] - 0.30) < 1e-6

    # 3. CreditLineBurden = 3 / (50000 / 10000 + 1) = 3 / 6 = 0.5
    assert abs(df_featured["CreditLineBurden"].iloc[0] - 0.50) < 1e-6

    # 4. LoanBurden = 40000 / (50000 + 1) = 0.799984...
    expected_lb = 40000.0 / 50001.0
    assert abs(df_featured["LoanBurden"].iloc[0] - expected_lb) < 1e-6

    # 5. InterestBurden = 10.0 * (40000 / 50001) = 7.99984...
    expected_ib = 10.0 * expected_lb
    assert abs(df_featured["InterestBurden"].iloc[0] - expected_ib) < 1e-6

    # 6. DebtStress = 0.30 + (40000 / 50001) = 1.099984...
    expected_ds = 0.30 + expected_lb
    assert abs(df_featured["DebtStress"].iloc[0] - expected_ds) < 1e-6

    # 7. FinancialStabilityScore matching cell 66 (0.472618)
    credit_norm = (650.0 - 300.0) / (849.0 - 300.0)
    emp_norm = (36.0 - 0.0) / (119.0 - 0.0)
    inc_norm = (50000.0 - 15000.0) / (149999.0 - 15000.0)
    dti_norm = (0.30 - 0.10) / (0.90 - 0.10)
    expected_fss = 0.40 * credit_norm + 0.30 * emp_norm + 0.20 * inc_norm + 0.10 * (1.0 - dti_norm)
    assert abs(df_featured["FinancialStabilityScore"].iloc[0] - expected_fss) < 1e-6
    assert abs(df_featured["FinancialStabilityScore"].iloc[0] - 0.472618) < 1e-4

    # 8. RepaymentCapacity matching cell 66 (0.874978)
    expected_rc = expected_ilr * (1.0 - 0.30)
    assert abs(df_featured["RepaymentCapacity"].iloc[0] - expected_rc) < 1e-6
    assert abs(df_featured["RepaymentCapacity"].iloc[0] - 0.874978) < 1e-4


def test_feature_engineering_determinism(sample_customer_request):
    """Ensure identical inputs always produce bitwise identical outputs."""
    df_raw = feature_engineering_service.convert_api_to_dataframe(sample_customer_request)
    df_feat1, ind1 = feature_engineering_service.engineer_features(df_raw)
    df_feat2, ind2 = feature_engineering_service.engineer_features(df_raw)

    pd.testing.assert_frame_equal(df_feat1, df_feat2)
    assert ind1.model_dump() == ind2.model_dump()
