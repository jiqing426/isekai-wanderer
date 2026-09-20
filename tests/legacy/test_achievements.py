#!/usr/bin/env python3
import requests
import json

# Login
resp = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'email': 'cr013test@example.com',
    'password': '***'
})
token = resp.json()['access_token']

# Test achievements endpoint
resp = requests.get('http://localhost:8000/api/v1/achievements', 
                   headers={'Authorization': f'Bearer {token}'})
print('Status:', resp.status_code)
print('Response:', json.dumps(resp.json(), indent=2, ensure_ascii=False))
