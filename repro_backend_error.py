
import requests
import json
import jwt
import datetime

# 1. Generate a valid token for "user1" (Alice)
SECRET = "secure_secret_key_for_digital_self_ai_project_2026"
payload = {
    "userId": 1, 
    "userName": "user1",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}
token = jwt.encode(payload, SECRET, algorithm="HS256")

# 2. Call the chat endpoint with "recognize Leela"
url = "http://localhost:8000/chat"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
data = {"message": "recognize Leela", "model": "llama3.2:1b"}

print("Sending request...")
try:
    with requests.post(url, json=data, headers=headers, stream=True) as r:
        print(f"Status Code: {r.status_code}")
        for chunk in r.iter_content(chunk_size=None):
            if chunk:
                print(chunk.decode())
except Exception as e:
    print(f"Request failed: {e}")
