"""Verify end-to-end integration between frontend client and backend API."""

import json
import httpx

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("1. VERIFY FRONTEND WEBSERVER (PORT 3000)")
print("=" * 70)
r_fe = httpx.get(f"{FRONTEND_URL}/index.html")
print(f"GET {FRONTEND_URL}/index.html -> Status: {r_fe.status_code}")
assert r_fe.status_code == 200
assert "TVS CREDIT" in r_fe.text
assert "risk-assessment-form" in r_fe.text
print("Frontend web server is live and serving index.html")

print("\n" + "=" * 70)
print("2. VERIFY BACKEND STATUS (PORT 8000)")
print("=" * 70)
r_be = httpx.get(f"{BACKEND_URL}/health")
print(f"GET {BACKEND_URL}/health -> Status: {r_be.status_code}")
assert r_be.status_code == 200
assert r_be.json()["status"] == "healthy"
print("Backend engine is healthy and all ML artifacts are loaded")

print("\n" + "=" * 70)
print("3. SUBMIT DEMO CUSTOMER (PURPOSE: OTHER) & VERIFY 0.416806 PREDICTION")
print("=" * 70)
demo_customer = {
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

r_demo = httpx.post(f"{BACKEND_URL}/api/v1/risk-assessment", json=demo_customer)
print(f"POST /api/v1/risk-assessment -> Status: {r_demo.status_code}")
res_demo = r_demo.json()
print("Response Risk Assessment:")
print(json.dumps(res_demo["risk_assessment"], indent=2))
assert res_demo["success"] is True
prob_demo = res_demo["risk_assessment"]["default_probability"]
print(f"\n>> Verified Demo Customer Probability: {prob_demo:.6f} (Expected 0.416806 / rounds to 0.4168)")
assert abs(prob_demo - 0.4168) < 0.001
assert res_demo["risk_assessment"]["prediction"] == 0
assert res_demo["risk_assessment"]["risk_classification"] == "LOW RISK"
assert res_demo["risk_assessment"]["recommended_action"] == "MANUAL REVIEW"

print("\n" + "=" * 70)
print("4. SUBMIT DIFFERENT APPLICANT: HIGH-RISK PROFILE")
print("=" * 70)
high_risk_customer = {
    "age": 22,
    "income": 18000.0,
    "loan_amount": 90000.0,
    "credit_score": 380,
    "months_employed": 4,
    "num_credit_lines": 5,
    "interest_rate": 24.5,
    "loan_term": 60,
    "dti_ratio": 0.85,
    "education": "High School",
    "employment_type": "Unemployed",
    "marital_status": "Single",
    "has_mortgage": False,
    "has_dependents": True,
    "loan_purpose": "Other",
    "has_cosigner": False
}

r_hr = httpx.post(f"{BACKEND_URL}/api/v1/risk-assessment", json=high_risk_customer)
print(f"POST /api/v1/risk-assessment -> Status: {r_hr.status_code}")
res_hr = r_hr.json()
print("High Risk Customer Result:")
print(json.dumps(res_hr["risk_assessment"], indent=2))
assert res_hr["success"] is True
prob_hr = res_hr["risk_assessment"]["default_probability"]
print(f">> High Risk Probability: {prob_hr:.4f} ({prob_hr*100:.2f}%)")
assert prob_hr > 0.47
assert res_hr["risk_assessment"]["prediction"] == 1
assert res_hr["risk_assessment"]["risk_classification"] == "HIGH RISK"
assert res_hr["risk_assessment"]["recommended_action"] == "HIGH RISK - FURTHER REVIEW"
print(">> Confirmed model output dynamically changes for different customer input!")

print("\n" + "=" * 70)
print("5. SUBMIT DIFFERENT APPLICANT: PRIME / LOW-RISK ELIGIBLE PROFILE")
print("=" * 70)
prime_customer = {
    "age": 48,
    "income": 125000.0,
    "loan_amount": 20000.0,
    "credit_score": 790,
    "months_employed": 110,
    "num_credit_lines": 2,
    "interest_rate": 6.5,
    "loan_term": 24,
    "dti_ratio": 0.15,
    "education": "Master's",
    "employment_type": "Full-time",
    "marital_status": "Married",
    "has_mortgage": True,
    "has_dependents": True,
    "loan_purpose": "Home",
    "has_cosigner": True
}

r_prime = httpx.post(f"{BACKEND_URL}/api/v1/risk-assessment", json=prime_customer)
print(f"POST /api/v1/risk-assessment -> Status: {r_prime.status_code}")
res_prime = r_prime.json()
print("Prime Customer Result:")
print(json.dumps(res_prime["risk_assessment"], indent=2))
assert res_prime["success"] is True
prob_prime = res_prime["risk_assessment"]["default_probability"]
print(f">> Prime Probability: {prob_prime:.4f} ({prob_prime*100:.2f}%)")
assert prob_prime < 0.30
assert res_prime["risk_assessment"]["prediction"] == 0
assert res_prime["risk_assessment"]["risk_classification"] == "LOW RISK"
assert res_prime["risk_assessment"]["recommended_action"] == "ELIGIBLE"

print("\n" + "=" * 70)
print("6. VERIFY DEDICATED EXPLANATION ENDPOINT")
print("=" * 70)
r_exp = httpx.post(f"{BACKEND_URL}/api/v1/risk-assessment/explanation", json=demo_customer)
print(f"POST /api/v1/risk-assessment/explanation -> Status: {r_exp.status_code}")
assert r_exp.status_code == 200
factors = r_exp.json()
print(f"Returned {len(factors)} explainability risk factors:")
for f in factors[:5]:
    print(f"  {f['feature']:20}: impact={f['impact']:8} value={f['value']}")
assert len(factors) > 0

print("\n" + "=" * 70)
print("ALL FRONTEND/BACKEND INTEGRATION TESTS PASSED PERFECTLY!")
print("=" * 70)
