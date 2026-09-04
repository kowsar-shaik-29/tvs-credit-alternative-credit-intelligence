import urllib.request
import json

base = 'http://127.0.0.1:8000'

# 1. Health
with urllib.request.urlopen(f'{base}/health') as resp:
    print('Health:', resp.status)

# 2. Consent
with urllib.request.urlopen(f'{base}/api/v1/consent') as resp:
    c = json.loads(resp.read().decode())
    print('Consent sources count:', len(c['sources']))

# 3. Full assessment
payload = {
    'age': 30, 'income': 50000, 'loan_amount': 40000, 'credit_score': 650,
    'months_employed': 36, 'num_credit_lines': 3, 'interest_rate': 10.0,
    'loan_term': 36, 'dti_ratio': 0.30, 'education': "Bachelor's",
    'employment_type': 'Full-time', 'marital_status': 'Single',
    'has_mortgage': False, 'has_dependents': False, 'loan_purpose': 'Other',
    'has_cosigner': False
}
req = urllib.request.Request(f'{base}/api/v1/nirnay/full-assessment', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print('Full assessment:', resp.status, 'Prob:', res['risk_assessment']['default_probability'], 'Twin index:', res['digital_twin']['twin_stability_index'], 'Scenarios:', len(res['stress_test']['scenarios']))

# 4. Assistant query
req = urllib.request.Request(f'{base}/api/v1/assistant/query', data=json.dumps({'question': 'Why was my risk classified this way?', 'application_data': payload}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print('Assistant answer length:', len(res['answer']))
    print('Sample answer snippet:', res['answer'][:120])
