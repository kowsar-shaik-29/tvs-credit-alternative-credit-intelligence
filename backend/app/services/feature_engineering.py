"""Deterministic feature engineering service matching Kaggle notebook logic exactly."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from config.settings import settings
from app.schemas.risk import RiskAssessmentRequest, AlternativeCreditIndicators

logger = logging.getLogger("tvs_credit.feature_engineering")


class FeatureEngineeringService:
    """Calculates alternative-credit engineered features using exact formulas from the notebook."""

    def __init__(self, norm_params_path: Path = None):
        self.norm_params_path = norm_params_path or settings.resolved_normalization_params_path
        self.norm_params = self._load_normalization_params()

    def _load_normalization_params(self) -> Dict[str, Dict[str, float]]:
        """Load fixed min/max normalization parameters from JSON."""
        if not self.norm_params_path.exists():
            logger.error(f"Normalization parameters file not found at {self.norm_params_path}")
            raise FileNotFoundError(
                f"Normalization params not found at {self.norm_params_path}. "
                "Ensure backend/config/normalization_params.json exists."
            )
        with open(self.norm_params_path, "r", encoding="utf-8") as f:
            params = json.load(f)
        logger.info(f"Loaded normalization parameters from {self.norm_params_path.name}")
        return params

    def convert_api_to_dataframe(self, request: RiskAssessmentRequest) -> pd.DataFrame:
        """Convert API snake_case schema to the exact DataFrame columns expected by the model."""
        data_dict = {
            "Age": float(request.age),
            "Income": float(request.income),
            "LoanAmount": float(request.loan_amount),
            "CreditScore": float(request.credit_score),
            "MonthsEmployed": float(request.months_employed),
            "NumCreditLines": float(request.num_credit_lines),
            "InterestRate": float(request.interest_rate),
            "LoanTerm": float(request.loan_term),
            "DTIRatio": float(request.dti_ratio),
            "Education": str(request.education),
            "EmploymentType": str(request.employment_type),
            "MaritalStatus": str(request.marital_status),
            "HasMortgage": "Yes" if request.has_mortgage else "No",
            "HasDependents": "Yes" if request.has_dependents else "No",
            "LoanPurpose": str(request.loan_purpose),
            "HasCoSigner": "Yes" if request.has_cosigner else "No",
        }
        return pd.DataFrame([data_dict])

    def engineer_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, AlternativeCreditIndicators]:
        """Apply the exact 8 alternative credit formulas and financial stability normalization.

        Returns:
            df_featured: DataFrame with all 24 columns required by the preprocessor.
            indicators: AlternativeCreditIndicators schema for the API response.
        """
        df_featured = df.copy()

        # 1. IncomeLoanRatio
        df_featured["IncomeLoanRatio"] = (
            df_featured["Income"] / (df_featured["LoanAmount"] + 1)
        )

        # 2. EmploymentStability (clipped between 0 and 1)
        df_featured["EmploymentStability"] = (
            df_featured["MonthsEmployed"] / 120.0
        ).clip(0.0, 1.0)

        # 3. CreditLineBurden
        df_featured["CreditLineBurden"] = (
            df_featured["NumCreditLines"] / (df_featured["Income"] / 10000.0 + 1)
        )

        # 4. LoanBurden
        df_featured["LoanBurden"] = (
            df_featured["LoanAmount"] / (df_featured["Income"] + 1)
        )

        # 5. InterestBurden
        df_featured["InterestBurden"] = (
            df_featured["InterestRate"] * df_featured["LoanBurden"]
        )

        # 6. DebtStress
        df_featured["DebtStress"] = (
            df_featured["DTIRatio"] + df_featured["LoanBurden"]
        )

        # 7. Financial Stability Score
        credit_min = self.norm_params["CreditScore"]["min"]
        credit_max = self.norm_params["CreditScore"]["max"]
        credit_range = (credit_max - credit_min) if (credit_max - credit_min) > 0 else 1.0

        emp_min = self.norm_params["MonthsEmployed"]["min"]
        emp_max = self.norm_params["MonthsEmployed"]["max"]
        emp_range = (emp_max - emp_min) if (emp_max - emp_min) > 0 else 1.0

        inc_min = self.norm_params["Income"]["min"]
        inc_max = self.norm_params["Income"]["max"]
        inc_range = (inc_max - inc_min) if (inc_max - inc_min) > 0 else 1.0

        dti_min = self.norm_params["DTIRatio"]["min"]
        dti_max = self.norm_params["DTIRatio"]["max"]
        dti_range = (dti_max - dti_min) if (dti_max - dti_min) > 0 else 1.0

        credit_norm = (
            (df_featured["CreditScore"] - credit_min) / credit_range
        ).clip(0.0, 1.0)

        employment_norm = (
            (df_featured["MonthsEmployed"] - emp_min) / emp_range
        ).clip(0.0, 1.0)

        income_norm = (
            (df_featured["Income"] - inc_min) / inc_range
        ).clip(0.0, 1.0)

        dti_norm = (
            (df_featured["DTIRatio"] - dti_min) / dti_range
        ).clip(0.0, 1.0)

        df_featured["FinancialStabilityScore"] = (
            0.40 * credit_norm
            + 0.30 * employment_norm
            + 0.20 * income_norm
            + 0.10 * (1.0 - dti_norm)
        )

        # 8. RepaymentCapacity
        df_featured["RepaymentCapacity"] = (
            df_featured["Income"] / (df_featured["LoanAmount"] + 1)
        ) * (
            1.0 - df_featured["DTIRatio"].clip(0.0, 1.0)
        )

        # Ensure exact column ordering as trained in notebook
        expected_columns = [
            "Age", "Income", "LoanAmount", "CreditScore", "MonthsEmployed",
            "NumCreditLines", "InterestRate", "LoanTerm", "DTIRatio",
            "IncomeLoanRatio", "EmploymentStability", "CreditLineBurden",
            "LoanBurden", "InterestBurden", "DebtStress",
            "FinancialStabilityScore", "RepaymentCapacity",
            "Education", "EmploymentType", "MaritalStatus",
            "HasMortgage", "HasDependents", "LoanPurpose", "HasCoSigner"
        ]

        df_featured = df_featured[expected_columns]

        # Construct rounded indicators for API response readability (raw values used for inference)
        indicators = AlternativeCreditIndicators(
            financial_stability_score=round(float(df_featured["FinancialStabilityScore"].iloc[0]), 4),
            repayment_capacity=round(float(df_featured["RepaymentCapacity"].iloc[0]), 4),
            employment_stability=round(float(df_featured["EmploymentStability"].iloc[0]), 4),
            debt_stress=round(float(df_featured["DebtStress"].iloc[0]), 4),
            loan_burden=round(float(df_featured["LoanBurden"].iloc[0]), 4),
            interest_burden=round(float(df_featured["InterestBurden"].iloc[0]), 4),
            income_loan_ratio=round(float(df_featured["IncomeLoanRatio"].iloc[0]), 4),
            credit_line_burden=round(float(df_featured["CreditLineBurden"].iloc[0]), 4),
        )

        return df_featured, indicators


# Singleton instance
feature_engineering_service = FeatureEngineeringService()
