"""Comprehensive verification script executing all 5 required checks against the running backend."""

import subprocess
import sys
import json
import httpx

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("CHECK 1: GET /health")
print("=" * 70)
try:
    r = httpx.get(f"{BASE_URL}/health", timeout=5.0)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    print(">> CHECK 1 PASSED")
except Exception as e:
    print(f">> CHECK 1 FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("CHECK 2: GET /api/v1/model-info")
print("=" * 70)
try:
    r = httpx.get(f"{BASE_URL}/api/v1/model-info", timeout=5.0)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"
    print(">> CHECK 2 PASSED")
except Exception as e:
    print(f">> CHECK 2 FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("CHECK 3: POST /api/v1/risk-assessment (Known Customer I38PQUQS96)")
print("=" * 70)
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
    "loan_purpose": "Home",
    "has_cosigner": False
}
try:
    r = httpx.post(f"{BASE_URL}/api/v1/risk-assessment", json=payload, timeout=5.0)
    print(f"Status Code: {r.status_code}")
    data = r.json()
    print(f"Response:\n{json.dumps(data, indent=2)}")
    assert r.status_code == 200
    assert data["success"] is True
    risk = data["risk_assessment"]
    assert risk["prediction"] == 0
    assert risk["risk_classification"] == "LOW RISK"
    assert risk["recommended_action"] == "MANUAL REVIEW"
    print(">> CHECK 3 PASSED")
except Exception as e:
    print(f">> CHECK 3 FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("CHECK 4: RUN PYTEST")
print("=" * 70)
pytest_res = subprocess.run(
    [sys.executable, "-m", "pytest", "backend/tests/", "-v", "--tb=short"],
    capture_output=True,
    text=True
)
print(pytest_res.stdout)
if pytest_res.returncode != 0:
    print(pytest_res.stderr)
    print(">> CHECK 4 FAILED")
    sys.exit(pytest_res.returncode)
else:
    print(">> CHECK 4 PASSED")

print("\n" + "=" * 70)
print("CHECK 5: RUN MODEL PARITY TEST")
print("=" * 70)
parity_res = subprocess.run(
    [sys.executable, "backend/scripts/verify_model_parity.py"],
    capture_output=True,
    text=True
)
print(parity_res.stdout)
if parity_res.returncode != 0:
    print(parity_res.stderr)
    print(">> CHECK 5 FAILED")
    sys.exit(parity_res.returncode)
else:
    print(">> CHECK 5 PASSED")

print("\n" + "=" * 70)
print("ALL 5 CHECKS COMPLETED AND PASSED SUCCESSFULLY!")
print("=" * 70)
