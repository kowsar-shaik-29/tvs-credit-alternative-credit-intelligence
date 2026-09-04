# TVS Credit Alternative Credit Intelligence / NIRNAY

Production-ready machine learning backend, REST API, and underwriting intelligence system for TVS Credit Alternative Credit Intelligence (NIRNAY).

---

## 1. Project Purpose & Architecture

The **NIRNAY Alternative Credit Intelligence System** evaluates creditworthiness and default probability for loan applicants using an **Enhanced Random Forest** machine-learning architecture augmented with proprietary alternative credit proxy indicators.

### High-Level Architecture

```
TVS Credit NIRNAY Frontend (HTML/CSS/JS)
                 │
                 │ JSON Application Request
                 ▼
         FastAPI REST API
                 │
                 ▼
          Pydantic Schema
                 │
                 ▼
    Exact Feature Engineering
  (8 Alternative Credit Proxies)
                 │
                 ▼
  Fixed Normalization Parameters
  (normalization_params.json)
                 │
                 ▼
    Scikit-Learn Preprocessor
    (enhanced_preprocessor.pkl)
                 │  (Transforms into 39 processed features)
                 ▼
     Enhanced Random Forest
   (enhanced_random_forest.pkl)
                 │
                 ▼
         Default Probability
                 │
                 ▼
        Threshold Evaluator
        (risk_threshold.pkl)
                 │
        ┌────────┴────────┐
        ▼                 ▼
   Binary Class     Decision Engine
  ("LOW RISK" /     ("ELIGIBLE" / "MANUAL REVIEW" /
   "HIGH RISK")      "HIGH RISK - FURTHER REVIEW")
        └────────┬────────┘
                 │
                 ▼
   Alternative Credit Indicators
   & Explainability Breakdown
                 │
                 ▼
          JSON Response
```

---

## 2. Python Environment & Version Compatibility

- **Trained Kernel Environment**: Python **3.12.13** (Kaggle Linux Kernel Docker 28755).
- **Backend Recommended Runtime**: Python **3.12.x** (3.12.10 verified on Windows).
- **Key Framework Versions**:
  - `fastapi` >= 0.115.0
  - `pydantic` >= 2.8.0
  - `scikit-learn` >= 1.5.0
  - `pandas` >= 2.2.0
  - `numpy` >= 1.26.4, < 2.0.0
  - `joblib` >= 1.4.2

> **Important Compatibility Note**: Serialized scikit-learn models (`.pkl`) require compatible scikit-learn and Python versions to avoid `UnpicklingError` or incompatible internal representation changes. Always run the backend in a Python 3.12 environment with scikit-learn 1.5.x.

---

## 3. Directory Structure

```
backend/
├── main.py                     # FastAPI entry point & lifespan handler
├── requirements.txt            # Pinned dependencies
├── README.md                   # System documentation
├── Dockerfile                  # Production container definition
├── .dockerignore               # Docker ignore rules
├── .env.example                # Configuration template
├── .env                        # Local runtime configuration
│
├── config/
│   ├── __init__.py
│   ├── normalization_params.json # Exact dataset min/max values
│   └── settings.py             # Pydantic BaseSettings & path resolver
│
├── models/                     # Trained ML artifacts
│   ├── enhanced_random_forest.pkl
│   ├── enhanced_preprocessor.pkl
│   └── risk_threshold.pkl
│
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints (/health, /api/v1/...)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── risk.py             # Request & Response Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── feature_engineering.py # Exact deterministic feature engineering
│       ├── model_service.py    # Artifact caching and inference
│       └── risk_service.py     # Thresholding & multi-tier decision logic
│
├── scripts/
│   ├── verify_model_parity.py  # Model parity regression test script
│   └── reproduce_artifacts.py  # Notebook reproduction pipeline
│
└── tests/
    ├── test_health.py          # Service health tests
    ├── test_feature_engineering.py # Math & normalization formula tests
    ├── test_prediction.py      # Risk scoring & recommendation tests
    ├── test_api.py             # Endpoint validation & error handling
    └── test_model_parity.py    # Regression parity test
```

---

## 4. Installation & Local Setup

### Step 1: Create and Activate Virtual Environment

```bash
# Using Python 3.12
py -3.12 -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activate on Linux/macOS
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Model Artifacts Placement

Ensure the following 3 serialized files are placed inside `backend/models/`:
- `enhanced_random_forest.pkl`
- `enhanced_preprocessor.pkl`
- `risk_threshold.pkl`

*(If recreating artifacts from the raw dataset, place `Loan_default.csv` in `backend/data/` and run `python scripts/reproduce_artifacts.py`)*

### Step 4: Run the Backend Locally

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive Swagger documentation will be available at:
`http://localhost:8000/docs`

---

## 5. Environment Variables Configuration

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Bind IP address |
| `PORT` | `8000` | Bind HTTP port (Cloud Run sets dynamically) |
| `ENVIRONMENT` | `development` | Application environment (`development` / `production`) |
| `FRONTEND_URL` | `http://localhost:3000,...` | Allowed CORS origins (comma-separated) |
| `MODEL_PATH` | `models/enhanced_random_forest.pkl` | Path to Random Forest model |
| `PREPROCESSOR_PATH` | `models/enhanced_preprocessor.pkl` | Path to ColumnTransformer |
| `THRESHOLD_PATH` | `models/risk_threshold.pkl` | Path to threshold artifact |
| `NORMALIZATION_PARAMS_PATH` | `config/normalization_params.json` | Min/max bounds for stability calculation |

---

## 6. API Endpoints

### 1. `GET /health`
Verifies backend status and artifact loading.

```json
{
  "status": "healthy",
  "model_loaded": true,
  "preprocessor_loaded": true,
  "threshold_loaded": true
}
```

### 2. `GET /api/v1/model-info`
Provides safe model metadata.

```json
{
  "model": "Enhanced Random Forest",
  "model_type": "RandomForestClassifier",
  "threshold": 0.47,
  "feature_engineering": "alternative_credit",
  "status": "ready"
}
```

### 3. `POST /api/v1/risk-assessment`
Main underwriting intelligence endpoint.

#### Example Request:
```json
{
  "age": 30,
  "income": 50000,
  "loan_amount": 40000,
  "credit_score": 650,
  "months_employed": 36,
  "num_credit_lines": 3,
  "interest_rate": 10.0,
  "loan_term": 36,
  "dti_ratio": 0.30,
  "education": "Bachelor's",
  "employment_type": "Full-time",
  "marital_status": "Single",
  "has_mortgage": false,
  "has_dependents": false,
  "loan_purpose": "Home",
  "has_cosigner": false
}
```

#### Example Response:
```json
{
  "success": true,
  "risk_assessment": {
    "default_probability": 0.3928,
    "risk_threshold": 0.47,
    "prediction": 0,
    "risk_classification": "LOW RISK",
    "recommended_action": "MANUAL REVIEW"
  },
  "alternative_credit_indicators": {
    "financial_stability_score": 0.4726,
    "repayment_capacity": 0.8750,
    "employment_stability": 0.3000,
    "debt_stress": 1.1000,
    "loan_burden": 0.8000,
    "interest_burden": 7.9998,
    "income_loan_ratio": 1.2500,
    "credit_line_burden": 0.5000
  },
  "top_risk_factors": [
    {
      "feature": "InterestBurden",
      "impact": "Negative",
      "value": 0.0591
    }
  ]
}
```

---

## 7. Model Parity Verification & Testing

### Running the Critical Parity Script:
```bash
python scripts/verify_model_parity.py
```
Expected Output:
```
MODEL PARITY CHECK
------------------
Probability from notebook    : 0.3928 (39.28%)
Probability from API pipeline: 0.3928 (39.28%)
Difference                   : 0.000000

OVERALL MODEL PARITY: PASS
```

### Running the Complete Pytest Suite:
```bash
pytest tests/ -v
```

---

## 8. Docker & Cloud Run Deployment

### Build Container:
```bash
docker build -t tvs-credit-nirnay:latest .
```

### Run Container:
```bash
docker run -p 8000:8000 -e PORT=8000 tvs-credit-nirnay:latest
```

### Google Cloud Run Deployment:
```bash
# Tag and push to Google Container / Artifact Registry
docker tag tvs-credit-nirnay:latest gcr.io/YOUR_PROJECT_ID/tvs-credit-nirnay:latest
docker push gcr.io/YOUR_PROJECT_ID/tvs-credit-nirnay:latest

# Deploy to Cloud Run
gcloud run deploy tvs-credit-nirnay \
  --image gcr.io/YOUR_PROJECT_ID/tvs-credit-nirnay:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
