import requests
import time
import random
import sys
import json

# Prompts to simulate conversation
PROMPTS = [
    "Hello, who are you?",
    "What is your core directive?",
    "Tell me a very short joke.",
    "What is the speed of light?",
    "Do you remember my name?",
    "What is 2 + 2?",
    "Explain quantum physics in one sentence.",
    "Are you working fast now?",
    "Say something funny.",
    "How is the weather?",
    "Who created you?",
    "What is your favorite color?",
    "Tell me about space.",
    "Are you a robot?",
    "What time is it?",
    "Can you hear me?",
    "Systems check.",
    "Status report.",
    "Memory retrieval test.",
    "Quick response test."
]

def typing_effect(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01) # Simulate reading/typing speed
    print()

def run_test():
    print("==================================================")
    print("      DIGITAL SELF - LIVE CONTINUOUS TEST         ")
    print("==================================================")
    print("Press Ctrl+C to stop.")
    print("Target Model: llama3.2:1b (Fast)")
    print("Target URL: http://localhost:8000/chat")
    print("--------------------------------------------------\n")

    counter = 1
    
    while True:
        prompt = random.choice(PROMPTS)
        print(f"[{counter}] USER: {prompt}")
        
        start_time = time.time()
        try:
            # We explicitly request the 1b model to verify the fix
            payload = {"message": prompt, "model": "llama3.2:1b"}
            
            response = requests.post("http://localhost:8000/chat", json=payload, stream=True)
            
            sys.stdout.write(f"[{counter}] BOT:  ")
            
            full_response = ""
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    text = chunk.decode("utf-8")
                    sys.stdout.write(text)
                    sys.stdout.flush()
                    full_response += text
            
            end_time = time.time()
            duration = end_time - start_time
            print(f"\n    [Metrics] Time: {duration:.2f}s | Length: {len(full_response)} chars")
            
        except Exception as e:
            print(f"\n[ERROR] Connection failed: {e}")
            print("Is the backend running?")
        
        print("-" * 50)
        counter += 1
        time.sleep(2) # Short pause between chats

if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        print("\n\nTest Stopped by User.")
