import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

payload = {
    "age": 30,
    "income": 50000.0,
    "loan_amount": 40000.0,
    "credit_score": 650,
    "months_employed": 36,
    "num_credit_lines": 3,
    "interest_rate": 10.0,
    "loan_term": 36,
    "dti_ratio": 0.30,
    "education": "Bachelor's",
    "employment_type": "Full-time",
    "marital_status": "Single",
    "has_mortgage": False,
    "has_dependents": False,
    "loan_purpose": "Other",
    "has_cosigner": False
}

print("1. GET /health")
r = httpx.get(f"{BASE_URL}/health")
print("Status:", r.status_code)
print(json.dumps(r.json(), indent=2))

print("\n2. GET /api/v1/model-info")
r = httpx.get(f"{BASE_URL}/api/v1/model-info")
print("Status:", r.status_code)
print(json.dumps(r.json(), indent=2))

print("\n3. POST /api/v1/risk-assessment (loan_purpose='Other')")
r = httpx.post(f"{BASE_URL}/api/v1/risk-assessment", json=payload)
print("Status:", r.status_code)
print(json.dumps(r.json(), indent=2))

print("\n4. POST /api/v1/risk-assessment/explanation")
r = httpx.post(f"{BASE_URL}/api/v1/risk-assessment/explanation", json=payload)
print("Status:", r.status_code)
print(json.dumps(r.json(), indent=2))
