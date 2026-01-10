import requests
import jwt
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
JWT_SECRET = "secure_secret_key_for_digital_self_ai_project_2026"
ALGORITHM = "HS256"

# Test Users matching the seeded data
TEST_USERS = [
    {"id": 1, "username": "user1", "secret": "ALPHA"},
    {"id": 2, "username": "user2", "secret": "BETA"},
    {"id": 3, "username": "user3", "secret": "GAMMA"},
    {"id": 4, "username": "user4", "secret": "DELTA"},
    {"id": 5, "username": "user5", "secret": "EPSILON"},
]

def generate_token(user_id, username):
    payload = {
        "userId": user_id,
        "sub": username,
        "iat": datetime.utcnow().timestamp(),
        "exp": datetime.utcnow().timestamp() + 3600
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def print_result(passed, message):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status}: {message}")
    return passed

def run_verification():
    print("="*60)
    print("MULTI-USER API VERIFICATION")
    print("="*60)
    all_passed = True
    
    # 1. Store Memories for each user
    print("\n--- Phase 1: Storing Memories ---")
    for user in TEST_USERS:
        token = generate_token(user['id'], user['username'])
        headers = {"Authorization": f"Bearer {token}"}
        
        # We assume the bot is listening at /chat
        # We'll use a direct memory command to ensure storage
        prompt = f"Remember that my secret is {user['secret']}"
        try:
            # We need to stream or handle the response. The API returns a stream.
            response = requests.post(
                f"{API_URL}/chat", 
                json={"message": prompt, "model": "llama3.2:1b"},
                headers=headers,
                stream=True
            )
            
            # Consume stream
            resp_text = ""
            for chunk in response.iter_content(chunk_size=None):
                if chunk: resp_text += chunk.decode('utf-8')
                
            success = "memory" in resp_text.lower() or "stored" in resp_text.lower()
            all_passed &= print_result(success, f"User {user['username']} stored secret")
            if not success:
                print(f"   Response: {resp_text}")
                
        except Exception as e:
            all_passed &= print_result(False, f"User {user['username']} failed to store: {e}")

    # 2. Verify Isolation
    print("\n--- Phase 2: Verifying Isolation ---")
    for user in TEST_USERS:
        token = generate_token(user['id'], user['username'])
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Get memories via API
            response = requests.get(f"{API_URL}/memories", headers=headers)
            memories = response.json()
            
            # Check 1: Should have their own secret
            has_own = any(user['secret'] in m['content'] for m in memories)
            
            # Check 2: Should NOT have others' secrets
            has_others = False
            for other in TEST_USERS:
                if other['id'] == user['id']: continue
                if any(other['secret'] in m['content'] for m in memories):
                    has_others = True
                    print(f"   [!] Found {other['username']}'s secret in {user['username']}'s memory!")
            
            passed = has_own and not has_others
            all_passed &= print_result(passed, f"User {user['username']} isolation verified")
            if not has_own: print(f"   Missing own secret: {user['secret']}")
            
        except Exception as e:
            all_passed &= print_result(False, f"User {user['username']} check failed: {e}")

    # 3. Spring Boot Integration (Recognition)
    print("\n--- Phase 3: Spring Boot Integration (Recognition) ---")
    # User 1 recognizes User 2
    sender = TEST_USERS[0]
    receiver = TEST_USERS[1]
    
    token = generate_token(sender['id'], sender['username'])
    headers = {"Authorization": f"Bearer {token}"}
    
    prompt = f"Recognize {receiver['username']} for being a great teammate with 50 points"
    print(f"Action: {sender['username']} -> {prompt}")
    
    try:
        response = requests.post(
            f"{API_URL}/chat", 
            json={"message": prompt, "model": "llama3.2:1b"},
            headers=headers,
            stream=True
        )
        resp_text = ""
        for chunk in response.iter_content(chunk_size=None):
            if chunk: resp_text += chunk.decode('utf-8')
            
        # Check for success message from Spring Boot (mocked or real)
        # The code returns "Successfully recognized..."
        success = "successfully recognized" in resp_text.lower()
        all_passed &= print_result(success, "Recognition intent succeeded")
        print(f"   Response: {resp_text.strip()}")
        
    except Exception as e:
        all_passed &= print_result(False, f"Recognition test failed: {e}")

    print("\n" + "="*60)
    if all_passed:
        print("ALL MULTI-USER TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("="*60)

if __name__ == "__main__":
    run_verification()
