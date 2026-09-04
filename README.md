# TVS Credit — Alternative Credit Intelligence | NIRNAY

> **Production-Ready Alternative Credit Risk Assessment & Automated Underwriting System**  
> Built around the trained machine learning pipeline from the Kaggle notebook `tvscredit.ipynb`.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (SPA)                         │
│  Vanilla HTML5 / CSS3 / JavaScript (No framework overhead)  │
│  - Single Page Application with dynamic form validation     │
│  - Configurable API endpoint (Runtime config: js/config.js) │
│  - Risk gauge, 8 alternative indicators, TreeSHAP breakdown │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON / HTTP (REST API)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND API                       │
│  - Lifespan pre-loading of model & preprocessing artifacts  │
│  - Feature engineering service (8 alternative indicators)   │
│  - Cached inference service with class-index alignment      │
│  - Operational risk decision tiering (Threshold = 0.47)     │
│  - Explainability endpoint (Top feature risk contributors)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     MODEL ARTIFACTS                         │
│  - enhanced_random_forest.pkl (RandomForestClassifier, 182M)│
│  - enhanced_preprocessor.pkl  (ColumnTransformer, 6.3KB)    │
│  - risk_threshold.pkl         (0.47 decision boundary, 21B) │
│  - normalization_params.json  (Min-max normalization bounds)│
└─────────────────────────────────────────────────────────────┘
```

---

## Machine Learning Pipeline & Parity

- **Model Type**: Enhanced Random Forest Classifier (300 estimators, max depth 14, balanced class weights).
- **Preprocessing**: `ColumnTransformer` with 17 numerical variables (StandardScaler, SimpleImputer) + 7 categorical variables (OneHotEncoder) expanding into 39 processed features.
- **Engineered Features**:
  1. `DTI_Income_Ratio` = $\text{DTIRatio} / (\text{Income} + 1)$
  2. `Credit_to_Loan_Ratio` = $\text{CreditScore} / (\text{LoanAmount} + 1)$
  3. `Income_per_Credit_Line` = $\text{Income} / (\text{NumCreditLines} + 1)$
  4. `Monthly_Income` = $\text{Income} / 12$
  5. `Monthly_Debt` = $\text{Monthly\_Income} \times \text{DTIRatio}$
  6. `Monthly_Loan_Payment` = $(\text{LoanAmount} / \text{LoanTerm}) \times (1 + \text{InterestRate} / 100)$
  7. `Financial_Stability_Score` = $0.35 \times \text{NormCreditScore} + 0.25 \times \text{NormMonthsEmployed} + 0.25 \times \text{NormIncome} + 0.15 \times (1 - \text{NormDTIRatio})$
  8. `Repayment_Capacity` = $\max(0, 1 - (\text{Monthly\_Debt} + \text{Monthly\_Loan\_Payment}) / (\text{Monthly\_Income} + 1))$
- **Decision Threshold**: Exactly `0.47` (optimized from notebook evaluation for default risk classification).
- **Parity Verification**: Verified against notebook inference with zero drift (floating-point tolerance $\le 5.55 \times 10^{-17}$).

---

## Project Structure

```
├── .gitattributes                # Git LFS tracking for *.pkl model files
├── .gitignore                    # Production gitignore rules
├── .env.example                  # Environment configuration template
├── README.md                     # Root project documentation
├── tvscredit.ipynb               # Original Kaggle notebook (source of truth)
├── backend/
│   ├── Dockerfile                # Production Dockerfile for Cloud Run (Python 3.12-slim)
│   ├── .dockerignore             # Docker build context exclusions
│   ├── .env.example              # Backend environment template
│   ├── requirements.txt          # Python dependencies
│   ├── main.py                   # FastAPI application & lifespan loader
│   ├── app/
│   │   ├── api/routes.py         # REST API endpoints (/health, /api/v1/*)
│   │   ├── schemas/risk.py       # Pydantic request & response schemas
│   │   └── services/
│   │       ├── feature_engineering.py # 8 alternative formulas & normalization
│   │       ├── model_service.py       # Model inference & explainability
│   │       └── risk_service.py        # Decisioning logic & thresholds
│   ├── config/
│   │   ├── settings.py           # Dynamic environment configuration
│   │   └── normalization_params.json # Feature normalization bounds
│   ├── data/
│   │   └── .gitkeep              # Training dataset directory (raw CSV excluded)
│   ├── models/
│   │   ├── enhanced_random_forest.pkl # Model weights (tracked via Git LFS)
│   │   ├── enhanced_preprocessor.pkl  # Pipeline preprocessor
│   │   └── risk_threshold.pkl         # 0.47 operational threshold
│   ├── scripts/                  # Parity & diagnostic tools
│   └── tests/                    # Pytest unit & integration test suite
└── frontend/
    ├── index.html                # Responsive UI dashboard
    ├── css/style.css             # Enterprise design system & theme
    └── js/
        ├── config.js             # Runtime environment configuration
        ├── api.js                # Centralized REST client
        └── app.js                # DOM manipulation, form handling & gauges
```

---

## Important: Model Artifact Sizing & Git LFS

The trained model `backend/models/enhanced_random_forest.pkl` is **182.4 MB** (182,385,273 bytes).  
GitHub enforces a hard limit of **100 MB** per file for standard git commits.

### Setting up Git LFS (Recommended for GitHub):

1. Install Git LFS on your system:
   ```bash
   git lfs install
   ```
2. `.gitattributes` is already configured in the repository:
   ```gitattributes
   *.pkl filter=lfs diff=lfs merge=lfs -text
   backend/models/*.pkl filter=lfs diff=lfs merge=lfs -text
   ```
3. When staging and committing, Git LFS will automatically track the model pickle as an LFS pointer.

### Alternative Model Storage for Production Containers:
For Google Cloud Run or Kubernetes deployments, you may also store the model file in a **Google Cloud Storage (GCS) bucket** or **GitHub Release Asset** and download it during container initialization or build.

---

## Local Development Setup

### 1. Backend Setup

```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

### 2. Frontend Setup

Serve the `frontend/` folder with any HTTP static server:

```bash
# Using Python:
python -m http.server 3000 --directory frontend

# Or using Node:
# npx serve frontend -p 3000
```

Open `http://localhost:3000` in your browser.

---

## Production Deployment

### 1. Deploying Backend to Google Cloud Run

The backend includes a production-ready `Dockerfile` that binds to `0.0.0.0` and reads Cloud Run's dynamic `$PORT`.

```bash
# Build and deploy from the backend directory using Google Cloud CLI:
cd backend
gcloud run deploy tvs-nirnay-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

Note the output service URL, for example: `https://tvs-nirnay-api-xyz-uc.a.run.app`.

### 2. Deploying Frontend (Static Hosting)

The frontend is a vanilla HTML/CSS/JS SPA and requires **no build step**.

#### Configurable API URL:
Configure the deployed backend URL using any of these methods:
- **Query Parameter**: Append `?api_url=https://tvs-nirnay-api-xyz-uc.a.run.app` to your frontend URL.
- **Window Global**: In `frontend/index.html` (before `config.js`):
  ```html
  <script>window.API_BASE_URL = "https://tvs-nirnay-api-xyz-uc.a.run.app";</script>
  ```
- **Runtime LocalStorage**: Set `localStorage.setItem("TVS_API_BASE_URL", "https://your-backend-url")`.

#### Hosting Options:
- **GitHub Pages**: Go to Repository Settings → Pages → Select branch & folder (`/frontend` or root).
- **Firebase Hosting**: Run `firebase init hosting` and set public directory to `frontend`.
- **Vercel / Netlify**: Deploy as a static directory without build commands.

---

## Test Suite & Verification

Run the full automated pytest suite:
```bash
python -m pytest backend/tests -v
```

Run the Kaggle model parity verification test:
```bash
python backend/scripts/verify_model_parity.py
```
