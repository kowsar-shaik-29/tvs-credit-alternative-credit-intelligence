import json
import httpx

payload = {
    "age": 56,
    "income": 85994.0,
    "loan_amount": 50587.0,
    "credit_score": 520,
    "months_employed": 80,
    "num_credit_lines": 4,
    "interest_rate": 15.23,
    "loan_term": 36,
    "dti_ratio": 0.44,
    "education": "Bachelor's",
    "employment_type": "Full-time",
    "marital_status": "Divorced",
    "has_mortgage": True,
    "has_dependents": True,
    "loan_purpose": "Other",
    "has_cosigner": True
}

r = httpx.post("http://127.0.0.1:8000/api/v1/risk-assessment", json=payload)
print("HTTP Status:", r.status_code)
res = r.json()
print(json.dumps(res, indent=2))
risk = res["risk_assessment"]
ind = res["alternative_credit_indicators"]
print(f"\nAPI Probability: {risk['default_probability']}")
print(f"API Threshold: {risk['risk_threshold']}")
print(f"API Classification: {risk['risk_classification']}")
print(f"API Recommended Action: {risk['recommended_action']}")
print(f"API Financial Stability Score: {ind['financial_stability_score']}")
print(f"API Repayment Capacity: {ind['repayment_capacity']}")
