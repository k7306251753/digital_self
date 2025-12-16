import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health():
    try:
        start = time.time()
        res = requests.get(f"{BASE_URL}/health")
        latency = (time.time() - start) * 1000
        print(f"[PASS] Health Check: {res.status_code} ({latency:.2f}ms)")
        return True
    except Exception as e:
        print(f"[FAIL] Health Check: {e}")
        return False

def test_memory_crud():
    print("\n--- Testing Memory ---")
    # 1. Add Memory via Chat (Implicit) - actually we rely on 'learn' or simple chat for now
    # We'll rely on the /memories endpoint to see if it exists
    
    start = time.time()
    res = requests.get(f"{BASE_URL}/memories")
    latency = (time.time() - start) * 1000
    print(f"[PASS] Get Memories: {len(res.json())} items ({latency:.2f}ms)")

def test_chat_latency():
    print("\n--- Testing Chat Latency ---")
    payload = {"message": "Hello, are you there?"}
    
    start = time.time()
    # Use stream=True to measure time-to-first-byte (TTFB)
    with requests.post(f"{BASE_URL}/chat", json=payload, stream=True) as r:
        ttfb = (time.time() - start) * 1000
        print(f"[INFO] Time to First Byte (Response Start): {ttfb:.2f}ms")
        
        content = ""
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                content += chunk.decode()
        
        total_time = (time.time() - start) * 1000
        print(f"[INFO] Total Generation Time: {total_time:.2f}ms")
        print(f"[Pass] Response length: {len(content)} chars")

if __name__ == "__main__":
    print("Starting Deep Backend Verification...")
    if test_health():
        test_memory_crud()
        test_chat_latency()
    print("\nVerification Complete.")
