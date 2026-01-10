from digital_self import DigitalSelf
from brain import db
import time

def test():
    print("--- Initialzing ---")
    bot = DigitalSelf()
    
    # 1. Test Storage
    print("\n[TEST] Storing 'I got a TT shot on 4th December 2025'...")
    try:
        bot.memory_controller.store_observation("I got a TT shot on 4th December 2025.")
        print("[PASS] Method called without error.")
    except Exception as e:
        print(f"[FAIL] Method raised: {e}")

    # 2. Check DB
    print("\n[TEST] Checking Database...")
    memories = db.get_memories(limit=5)
    found = False
    for m in memories:
        print(f" - Found: {m['content']}")
        if "TT shot" in m['content']:
            found = True
    
    if found:
        print("[PASS] Memory saved to DB.")
    else:
        print("[FAIL] Memory NOT found in DB.")

    # 3. Test Retrieval with Keyword Search
    print("\n[TEST] Retrieval: 'When did I get my TT shot?'")
    context = bot.memory_controller.retrieve_context("When did I get my TT shot?")
    print(f"Context Result:\n{context}")
    
    if "4th December" in context:
        print("[PASS] Retrieved correct context.")
    else:
        print("[FAIL] Context missing target info.")

if __name__ == "__main__":
    test()
