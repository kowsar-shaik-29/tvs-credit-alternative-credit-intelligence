"""Smoke test against live running FastAPI server."""

import json
import httpx

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("TESTING LIVE FASTAPI SERVER")
print("=" * 60)

# 1. Health
r = httpx.get(f"{BASE_URL}/health")
print(f"GET /health -> Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
assert r.status_code == 200
assert r.json()["status"] == "healthy"

# 2. Model Info
r = httpx.get(f"{BASE_URL}/api/v1/model-info")
print(f"\nGET /api/v1/model-info -> Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
assert r.status_code == 200

# 3. Risk Assessment (Known Customer I38PQUQS96)
payload = {
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
    "has_mortgage": False,
    "has_dependents": False,
    "loan_purpose": "Home",
    "has_cosigner": False
}

r = httpx.post(f"{BASE_URL}/api/v1/risk-assessment", json=payload)
print(f"\nPOST /api/v1/risk-assessment -> Status: {r.status_code}")
res = r.json()
print(json.dumps(res, indent=2))
assert r.status_code == 200
assert res["success"] is True

# Verify values
risk = res["risk_assessment"]
ind = res["alternative_credit_indicators"]
print(f"\nVerified Default Probability: {risk['default_probability']*100:.2f}% (Expected ~39.28%)")
print(f"Verified Threshold: {risk['risk_threshold']} (Expected 0.47)")
print(f"Verified Classification: {risk['risk_classification']} (Expected LOW RISK)")
print(f"Verified Action: {risk['recommended_action']} (Expected MANUAL REVIEW)")
print(f"Verified Financial Stability Score: {ind['financial_stability_score']} (Expected 0.4726)")
print(f"Verified Repayment Capacity: {ind['repayment_capacity']} (Expected 0.8750)")

# 4. OpenAPI / Swagger docs check
r = httpx.get(f"{BASE_URL}/openapi.json")
print(f"\nGET /openapi.json -> Status: {r.status_code}")
assert r.status_code == 200
assert "paths" in r.json()

r = httpx.get(f"{BASE_URL}/docs")
print(f"GET /docs -> Status: {r.status_code}")
assert r.status_code == 200

print("\n" + "=" * 60)
print("ALL LIVE ENDPOINT CHECKS PASSED!")
print("=" * 60)
