"""Exact reproduction script matching tvscredit.ipynb cells 50-58.

Generates:
  - enhanced_random_forest.pkl
  - enhanced_preprocessor.pkl
  - risk_threshold.pkl
  - normalization_params.json
"""

import os
import sys
import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reproduce_artifacts")

BACKEND_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BACKEND_DIR / "models"
CONFIG_DIR = BACKEND_DIR / "config"
DATA_DIR = BACKEND_DIR / "data"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def locate_dataset() -> Path:
    """Find Loan_default.csv in standard locations."""
    candidates = [
        DATA_DIR / "Loan_default.csv",
        BACKEND_DIR.parent / "Loan_default.csv",
        Path("c:/Users/allah/Downloads/Loan_default.csv"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def reproduce_pipeline(csv_path: Path):
    logger.info(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"Dataset loaded. Shape: {df.shape}")

    # Create working copy matching Cell 50
    df_alt = df.copy()

    # Step 1: Feature Engineering (Exact formulas from Cell 50)
    logger.info("Computing engineered alternative credit features...")

    df_alt["IncomeLoanRatio"] = df_alt["Income"] / (df_alt["LoanAmount"] + 1)
    df_alt["EmploymentStability"] = (df_alt["MonthsEmployed"] / 120).clip(0, 1)
    df_alt["CreditLineBurden"] = df_alt["NumCreditLines"] / (df_alt["Income"] / 10000 + 1)
    df_alt["LoanBurden"] = df_alt["LoanAmount"] / (df_alt["Income"] + 1)
    df_alt["InterestBurden"] = df_alt["InterestRate"] * df_alt["LoanBurden"]
    df_alt["DebtStress"] = df_alt["DTIRatio"] + df_alt["LoanBurden"]

    # Min/Max Normalization
    credit_min = float(df_alt["CreditScore"].min())
    credit_max = float(df_alt["CreditScore"].max())
    emp_min = float(df_alt["MonthsEmployed"].min())
    emp_max = float(df_alt["MonthsEmployed"].max())
    inc_min = float(df_alt["Income"].min())
    inc_max = float(df_alt["Income"].max())
    dti_min = float(df_alt["DTIRatio"].min())
    dti_max = float(df_alt["DTIRatio"].max())

    norm_params = {
        "CreditScore": {"min": credit_min, "max": credit_max},
        "MonthsEmployed": {"min": emp_min, "max": emp_max},
        "Income": {"min": inc_min, "max": inc_max},
        "DTIRatio": {"min": dti_min, "max": dti_max},
    }
    norm_path = CONFIG_DIR / "normalization_params.json"
    with open(norm_path, "w", encoding="utf-8") as f:
        json.dump(norm_params, f, indent=2)
    logger.info(f"Saved normalization parameters to {norm_path}")

    credit_norm = (df_alt["CreditScore"] - credit_min) / (credit_max - credit_min)
    employment_norm = (df_alt["MonthsEmployed"] - emp_min) / (emp_max - emp_min)
    income_norm = (df_alt["Income"] - inc_min) / (inc_max - inc_min)
    dti_norm = (df_alt["DTIRatio"] - dti_min) / (dti_max - dti_min)

    df_alt["FinancialStabilityScore"] = (
        0.40 * credit_norm +
        0.30 * employment_norm +
        0.20 * income_norm +
        0.10 * (1 - dti_norm)
    )

    df_alt["RepaymentCapacity"] = (
        df_alt["Income"] / (df_alt["LoanAmount"] + 1)
    ) * (
        1 - df_alt["DTIRatio"].clip(0, 1)
    )

    # Step 2: Prepare Preprocessor and Train/Test Split (Cell 51)
    y_alt = df_alt["Default"]
    X_alt = df_alt.drop(columns=["LoanID", "Default"], errors="ignore")

    numeric_features_alt = X_alt.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features_alt = X_alt.select_dtypes(include=["object"]).columns.tolist()

    logger.info(f"Numerical features ({len(numeric_features_alt)}): {numeric_features_alt}")
    logger.info(f"Categorical features ({len(categorical_features_alt)}): {categorical_features_alt}")

    numeric_transformer_alt = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]
    )

    categorical_transformer_alt = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ]
    )

    preprocessor_alt = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer_alt, numeric_features_alt),
            ("cat", categorical_transformer_alt, categorical_features_alt)
        ]
    )

    X_alt_train, X_alt_test, y_alt_train, y_alt_test = train_test_split(
        X_alt,
        y_alt,
        test_size=0.20,
        random_state=42,
        stratify=y_alt
    )

    logger.info("Fitting preprocessor...")
    X_alt_train_processed = preprocessor_alt.fit_transform(X_alt_train)
    logger.info(f"Processed training shape: {X_alt_train_processed.shape}")

    # Step 3: Train Enhanced Random Forest (Cell 52)
    logger.info("Training Enhanced RandomForestClassifier (300 estimators, max_depth=14, random_state=42)...")
    enhanced_rf_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_split=10,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    enhanced_rf_model.fit(X_alt_train_processed, y_alt_train)
    logger.info("Enhanced Random Forest training complete.")

    FINAL_THRESHOLD = 0.47

    # Step 4: Save Artifacts (Cell 58)
    model_path = MODELS_DIR / "enhanced_random_forest.pkl"
    prep_path = MODELS_DIR / "enhanced_preprocessor.pkl"
    thresh_path = MODELS_DIR / "risk_threshold.pkl"

    joblib.dump(enhanced_rf_model, model_path)
    joblib.dump(preprocessor_alt, prep_path)
    joblib.dump(FINAL_THRESHOLD, thresh_path)

    logger.info(f"Artifacts successfully saved:")
    logger.info(f"  Model       : {model_path}")
    logger.info(f"  Preprocessor: {prep_path}")
    logger.info(f"  Threshold   : {thresh_path}")


if __name__ == "__main__":
    csv_file = locate_dataset()
    if not csv_file:
        logger.error(
            "Loan_default.csv not found in backend/data/ or parent directories. "
            "Please place Loan_default.csv in backend/data/ to reproduce artifacts."
        )
        sys.exit(1)
    reproduce_pipeline(csv_file)
