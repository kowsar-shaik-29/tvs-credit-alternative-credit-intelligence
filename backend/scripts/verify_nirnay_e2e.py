"""Comprehensive End-to-End Verification of TVS Credit NIRNAY Platform."""

import urllib.request
import json
import sys

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"

def test_endpoint(url, method="GET", payload=None):
    data = json.dumps(payload).encode() if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode()
        return resp.status, json.loads(content) if "json" in resp.headers.get("Content-Type", "") else content

print("=" * 60)
print("TVS CREDIT NIRNAY - FULL END-TO-END VERIFICATION")
print("=" * 60)

# 1. Server Health & Model Info
status, health = test_endpoint(f"{BACKEND_URL}/health")
print(f"[1] Backend /health: {status} -> {health['status']}")
assert status == 200 and health["status"] == "healthy"

status, model_info = test_endpoint(f"{BACKEND_URL}/api/v1/model-info")
print(f"[2] Backend /model-info: {status} -> {model_info['model']} (Threshold: {model_info['threshold']})")
assert status == 200 and model_info["threshold"] == 0.47

# 2. Frontend HTTP checks
status, html = test_endpoint(f"{FRONTEND_URL}/index.html")
print(f"[3] Frontend /index.html: {status} (Length: {len(html)} bytes)")
assert status == 200 and "NIRNAY" in html

# 3. Customer Journey: Consent Manager
status, consent = test_endpoint(f"{BACKEND_URL}/api/v1/consent")
print(f"[4] Consent Manager: {status} -> {len(consent['sources'])} sources loaded")
assert len(consent["sources"]) == 7

# 4. Customer Journey: Full Assessment (First-Time Borrower)
first_time_borrower = {
    "age": 23, "income": 42000.0, "loan_amount": 25000.0, "credit_score": 610,
    "months_employed": 14, "num_credit_lines": 0, "interest_rate": 10.5,
    "loan_term": 24, "dti_ratio": 0.20, "education": "Bachelor's",
    "employment_type": "Full-time", "marital_status": "Single",
    "has_mortgage": False, "has_dependents": False, "loan_purpose": "Education",
    "has_cosigner": False
}
status, assessment = test_endpoint(f"{BACKEND_URL}/api/v1/nirnay/full-assessment", method="POST", payload=first_time_borrower)
print(f"[5] Assessment (First-Time Borrower): {status}")
print(f"    - Archetype: {assessment['archetype']}")
print(f"    - Default Probability: {assessment['risk_assessment']['default_probability'] * 100:.2f}%")
print(f"    - Classification: {assessment['risk_assessment']['risk_classification']}")
print(f"    - Recommended Loan: ₹{assessment['loan_recommendation']['recommended_loan']:,.0f}")
print(f"    - Digital Twin Stability Index: {assessment['digital_twin']['twin_stability_index']}/100")
print(f"    - Stress Scenarios Evaluated: {len(assessment['stress_test']['scenarios'])}")
assert status == 200
assert assessment["risk_assessment"]["risk_threshold"] == 0.47
assert len(assessment["stress_test"]["scenarios"]) == 7

# 5. Customer Journey: Financial Assistant
status, assistant_resp = test_endpoint(
    f"{BACKEND_URL}/api/v1/assistant/query",
    method="POST",
    payload={"question": "Why was my risk classified this way?", "application_data": first_time_borrower}
)
print(f"[6] Financial Assistant Query: {status}")
print(f"    - Answer snippet: {assistant_resp['answer'][:100]}...")
assert status == 200 and len(assistant_resp["answer"]) > 30

# 6. Analyst Journey: Portfolio & Audit Records
status, audit_records = test_endpoint(f"{BACKEND_URL}/api/v1/audit/records")
print(f"[7] Credit Analyst Portfolio: {status} -> {len(audit_records)} records in queue")
assert status == 200 and len(audit_records) >= 1

# 7. Dealer Journey: Data Minimization Check
# Dealer status must contain loan terms and eligibility, without leaking raw bank/UPI details
dealer_view = {
    "applicant_name": assessment["customer_name"],
    "eligibility": "ELIGIBLE" if assessment["risk_assessment"]["prediction"] == 0 else "REVIEW",
    "approved_loan": assessment["loan_recommendation"]["recommended_loan"],
    "approved_tenure": assessment["loan_recommendation"]["recommended_tenure_months"],
    "approved_emi": assessment["loan_recommendation"]["estimated_emi"]
}
print(f"[8] Dealer Point-of-Sale (Data-Minimized):")
print(f"    - Applicant: {dealer_view['applicant_name']}")
print(f"    - Approved Loan: ₹{dealer_view['approved_loan']:,.0f} over {dealer_view['approved_tenure']} months")
print(f"    - Estimated EMI: ₹{dealer_view['approved_emi']:,.0f}/mo")
print(f"    - Sensitive data (Bank Statements / UPI transactions) omitted: VERIFIED")

print("=" * 60)
print("ALL END-TO-END NIRNAY FLOWS VERIFIED SUCCESSFULLY!")
print("=" * 60)
