
import requests
import jwt
import time

JWT_SECRET = "secure_secret_key_for_digital_self_ai_project_2026"
ALGORITHM = "HS256"

def create_token(user_id="test_user"):
    payload = {"userId": user_id}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def test_chats():
    token = create_token()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        print("Sending request to /chats...")
        start = time.time()
        response = requests.get("http://localhost:8000/chats", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        print(f"Time: {time.time() - start:.2f}s")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chats()
