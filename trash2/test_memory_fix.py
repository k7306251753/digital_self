"""
Test script to verify memory extraction fixes
"""
from brain.memory_controller import MemoryController
from brain import db

def test_fact_extraction():
    print("="*60)
    print("Testing Fact Extraction")
    print("="*60)
    
    mc = MemoryController()
    
    test_cases = [
        ("just remember my birthday was 27th December", "birthday is 27th December"),
        ("ok remember I got TT shot on 4th December 2025", "I got TT shot on 4th December 2025"),
        ("remember my favorite color is blue", "favorite color is blue"),
        ("please remember my name is Krishna", "name is Krishna"),
    ]
    
    print("\n1. Testing _extract_fact() method:")
    for input_text, expected in test_cases:
        result = mc._extract_fact(input_text)
        status = "OK" if expected.lower() in result.lower() else "FAIL"
        print(f"  [{status}] Input: '{input_text}'")
        print(f"    Result: '{result}'")
        print(f"    Expected to contain: '{expected}'")
        print()

def test_memory_storage_and_retrieval():
    print("="*60)
    print("Testing Memory Storage and Retrieval")
    print("="*60)
    
    # Clear test memories first
    print("\n2. Clearing old test memories...")
    conn = db.get_db_connection()
    if conn:
        c = conn.cursor()
        c.execute("DELETE FROM long_term_memory WHERE content LIKE '%test_memory_%'")
        conn.commit()
        conn.close()
    
    mc = MemoryController()
    
    # Test storing memories with commands
    test_memories = [
        "remember test_memory_birthday is December 27th",
        "just remember test_memory_tt_shot on December 4th 2025",
    ]
    
    print("\n3. Storing test memories:")
    for memory in test_memories:
        is_cmd, response = mc.process_input(memory)
        print(f"  Input: '{memory}'")
        print(f"  Response: '{response}'")
        print()
    
    # Test retrieval
    print("\n4. Testing retrieval:")
    queries = [
        "when is test_memory_birthday",
        "test_memory_tt_shot date"
    ]
    
    for query in queries:
        results = db.search_memories(query)
        print(f"  Query: '{query}'")
        print(f"  Found {len(results)} memories:")
        for r in results:
            print(f"    - [{r['category']}] {r['content']}")
        print()

if __name__ == "__main__":
    test_fact_extraction()
    test_memory_storage_and_retrieval()
    print("="*60)
    print("Test Complete!")
    print("="*60)
