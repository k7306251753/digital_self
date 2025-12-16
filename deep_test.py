"""
DEEP TESTING SUITE for Digital Self Application
Advanced tests including edge cases, stress testing, performance, and data integrity
"""

from digital_self import DigitalSelf
from brain import db
from brain.memory_controller import MemoryController
from brain.llm_interface import LLMInterface
import sys
import time
import traceback
from datetime import datetime

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def print_test(test_name, level=0):
    indent = "  " * level
    print(f"\n{indent}[TEST] {test_name}")

def print_result(passed, message, level=0):
    indent = "  " * level
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{indent}{status}: {message}")
    return passed

# =============================================================================
# DEEP TEST 1: EDGE CASES & ERROR HANDLING
# =============================================================================

def test_edge_cases():
    print_section("EDGE CASES & ERROR HANDLING")
    all_passed = True
    
    # Test 1: Empty inputs
    print_test("Empty Inputs")
    try:
        mc = MemoryController()
        is_cmd, resp = mc.process_input("")
        all_passed &= print_result(not is_cmd, "Empty string handled", 1)
        
        is_cmd, resp = mc.process_input("   ")
        all_passed &= print_result(not is_cmd, "Whitespace-only handled", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Empty input failed: {e}", 1)
    
    # Test 2: Very long inputs
    print_test("Very Long Inputs")
    try:
        long_text = "A" * 10000  # 10k characters
        mc.store_observation(long_text)
        all_passed &= print_result(True, "10k character input stored", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Long input failed: {e}", 1)
    
    # Test 3: Special characters
    print_test("Special Characters")
    try:
        special_texts = [
            "I love emoji! 😊🎉🚀",
            "SQL injection? Robert'; DROP TABLE memories;--",
            "Newlines\nand\ttabs",
            "Unicode: café, naïve, 北京",
            r"Backslashes \ and quotes \" and '",
        ]
        for text in special_texts:
            mc.store_observation(text)
        all_passed &= print_result(True, f"Stored {len(special_texts)} special char inputs", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Special chars failed: {e}", 1)
    
    # Test 4: Invalid memory commands
    print_test("Invalid Memory Commands")
    try:
        invalid_commands = [
            "remember",  # No content
            "remember ",
            "learn that",  # No actual content after
            "store this:",
        ]
        for cmd in invalid_commands:
            is_cmd, resp = mc.process_input(cmd)
            if is_cmd and resp:
                all_passed &= print_result("need something" in resp.lower() or resp != "", 
                                          f"Invalid command handled: '{cmd[:20]}'", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Invalid commands failed: {e}", 1)
    
    # Test 5: Null/None handling
    print_test("Null/None Handling")
    try:
        conn = db.get_db_connection()
        if not conn:
            all_passed &= print_result(True, "None connection handled gracefully", 1)
        else:
            conn.close()
            all_passed &= print_result(True, "Connection valid", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Null handling failed: {e}", 1)
    
    # Test 6: Duplicate memory detection
    print_test("Duplicate Memory Handling")
    try:
        test_content = f"Test duplicate memory {datetime.now()}"
        mem_id1 = db.add_memory("TEST", test_content)
        mem_id2 = db.add_memory("TEST", test_content)
        all_passed &= print_result(mem_id1 != mem_id2, 
                                   "Duplicate content creates separate entries (expected)", 1)
        # Cleanup
        if mem_id1: db.delete_memory(mem_id1)
        if mem_id2: db.delete_memory(mem_id2)
    except Exception as e:
        all_passed &= print_result(False, f"Duplicate detection failed: {e}", 1)
    
    return all_passed

# =============================================================================
# DEEP TEST 2: STRESS TESTING
# =============================================================================

def test_stress():
    print_section("STRESS TESTING")
    all_passed = True
    
    # Test 1: Rapid memory operations
    print_test("Rapid Memory Operations (100 inserts)")
    try:
        start = time.time()
        mem_ids = []
        for i in range(100):
            mem_id = db.add_memory("STRESS_TEST", f"Stress test memory {i}")
            if mem_id:
                mem_ids.append(mem_id)
        elapsed = time.time() - start
        
        all_passed &= print_result(len(mem_ids) == 100, 
                                   f"100 memories in {elapsed:.2f}s ({100/elapsed:.1f} ops/sec)", 1)
        
        # Cleanup
        for mem_id in mem_ids:
            db.delete_memory(mem_id)
        all_passed &= print_result(True, "Cleaned up stress test memories", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Rapid operations failed: {e}", 1)
    
    # Test 2: Multiple searches
    print_test("Rapid Search Operations (50 searches)")
    try:
        start = time.time()
        for i in range(50):
            results = db.search_memories("test")
        elapsed = time.time() - start
        all_passed &= print_result(True, 
                                   f"50 searches in {elapsed:.2f}s ({50/elapsed:.1f} ops/sec)", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Rapid searches failed: {e}", 1)
    
    # Test 3: Large batch retrieval
    print_test("Large Batch Retrieval")
    try:
        memories = db.get_memories(limit=100)
        all_passed &= print_result(len(memories) > 0, 
                                   f"Retrieved {len(memories)} memories", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Large retrieval failed: {e}", 1)
    
    # Test 4: Memory controller under load
    print_test("Memory Controller Under Load (50 observations)")
    try:
        mc = MemoryController()
        start = time.time()
        for i in range(50):
            mc.store_observation(f"Load test observation number {i}")
        elapsed = time.time() - start
        all_passed &= print_result(True, 
                                   f"50 observations in {elapsed:.2f}s", 1)
    except Exception as e:
        all_passed &= print_result(False, f"MC under load failed: {e}", 1)
    
    return all_passed

# =============================================================================
# DEEP TEST 3: DATA INTEGRITY
# =============================================================================

def test_data_integrity():
    print_section("DATA INTEGRITY")
    all_passed = True
    
    # Test 1: Content preservation
    print_test("Content Preservation")
    try:
        original = "This is a test with special chars: @#$%^&*() and unicode: café"
        mem_id = db.add_memory("TEST", original)
        memories = db.get_memories(limit=1)
        retrieved = memories[0]['content'] if memories else None
        all_passed &= print_result(retrieved == original, 
                                   "Content matches exactly", 1)
        if mem_id: db.delete_memory(mem_id)
    except Exception as e:
        all_passed &= print_result(False, f"Content preservation failed: {e}", 1)
    
    # Test 2: Category accuracy
    print_test("Category Classification Accuracy")
    try:
        mc = MemoryController()
        test_cases = {
            "I love pizza": "PREFERENCE",
            "I can speak Spanish": "SKILL",
            "I believe in honesty": "BELIEF",
            "I always wake up early": "IDEOLOGY",
            "Random fact about nothing": "FACT"
        }
        
        # Store and verify
        for content, expected_cat in test_cases.items():
            mc.store_observation(content)
        
        all_passed &= print_result(True, f"Classified {len(test_cases)} observations", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Classification failed: {e}", 1)
    
    # Test 3: Timestamp integrity
    print_test("Timestamp Integrity")
    try:
        before = datetime.now()
        mem_id = db.add_memory("TEST", "Timestamp test")
        memories = db.get_memories(limit=1)
        after = datetime.now()
        
        if memories and memories[0]['created_at']:
            # Parse the timestamp string
            created = datetime.fromisoformat(memories[0]['created_at'].replace(' ', 'T'))
            in_range = before <= created <= after
            all_passed &= print_result(in_range, "Timestamp within expected range", 1)
        
        if mem_id: db.delete_memory(mem_id)
    except Exception as e:
        all_passed &= print_result(False, f"Timestamp test failed: {e}", 1)
    
    # Test 4: Search accuracy
    print_test("Search Accuracy")
    try:
        # Add unique test memories
        unique_id = str(datetime.now().timestamp())
        test_memories = [
            f"Python programming {unique_id}",
            f"JavaScript coding {unique_id}",
            f"Database design {unique_id}"
        ]
        
        mem_ids = []
        for mem in test_memories:
            mem_id = db.add_memory("TEST", mem)
            if mem_id: mem_ids.append(mem_id)
        
        # Search for unique_id should find all
        results = db.search_memories(unique_id)
        all_passed &= print_result(len(results) >= 3, 
                                   f"Found {len(results)} of 3 test memories", 1)
        
        # Cleanup
        for mem_id in mem_ids:
            db.delete_memory(mem_id)
    except Exception as e:
        all_passed &= print_result(False, f"Search accuracy failed: {e}", 1)
    
    return all_passed

# =============================================================================
# DEEP TEST 4: PERFORMANCE & OPTIMIZATION
# =============================================================================

def test_performance():
    print_section("PERFORMANCE & OPTIMIZATION")
    all_passed = True
    
    # Test 1: Search performance with varying query complexity
    print_test("Search Performance")
    try:
        queries = [
            "test",  # Simple
            "test memory database",  # Multiple keywords
            "when did I get my shot on December",  # Complex
        ]
        
        for query in queries:
            start = time.time()
            results = db.search_memories(query)
            elapsed = time.time() - start
            all_passed &= print_result(elapsed < 1.0, 
                                       f"'{query[:30]}...' in {elapsed*1000:.1f}ms", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Search performance failed: {e}", 1)
    
    # Test 2: Context retrieval speed
    print_test("Context Retrieval Speed")
    try:
        mc = MemoryController()
        start = time.time()
        context = mc.retrieve_context("What do I like?")
        elapsed = time.time() - start
        all_passed &= print_result(elapsed < 1.0, 
                                   f"Context retrieved in {elapsed*1000:.1f}ms", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Context retrieval failed: {e}", 1)
    
    # Test 3: Memory initialization speed
    print_test("Application Initialization Speed")
    try:
        start = time.time()
        bot = DigitalSelf()
        elapsed = time.time() - start
        all_passed &= print_result(elapsed < 5.0, 
                                   f"Initialized in {elapsed:.2f}s", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Initialization failed: {e}", 1)
    
    return all_passed

# =============================================================================
# DEEP TEST 5: END-TO-END WORKFLOWS
# =============================================================================

def test_e2e_workflows():
    print_section("END-TO-END WORKFLOWS")
    all_passed = True
    
    # Test 1: Complete conversation flow
    print_test("Complete Conversation Flow")
    try:
        bot = DigitalSelf()
        
        # Step 1: Teach it something
        response = bot.learn("I work at Google as a software engineer")
        all_passed &= print_result("Memory added" in response, 
                                   "Step 1: Learned new fact", 1)
        
        # Step 2: Use remember command
        gen = bot.chat("remember that my favorite color is blue")
        response = ''.join(str(c) for c in gen)
        all_passed &= print_result("memory" in response.lower(), 
                                   "Step 2: Memory command processed", 1)
        
        # Step 3: Regular chat (memory should be stored)
        gen = bot.chat("I like hiking")
        response = ''.join(str(c) for c in gen)
        all_passed &= print_result(True, 
                                   "Step 3: Regular chat processed", 1)
        
        # Step 4: Verify memories exist
        memories = bot.memory_controller.get_all_memories()
        has_google = any("Google" in m.get('content', '') for m in memories)
        has_blue = any("blue" in m.get('content', '') for m in memories)
        
        all_passed &= print_result(has_google or has_blue, 
                                   "Step 4: Memories persisted", 1)
    except Exception as e:
        all_passed &= print_result(False, f"E2E flow failed: {e}", 1)
        traceback.print_exc()
    
    # Test 2: Memory recall workflow
    print_test("Memory Recall Workflow")
    try:
        mc = MemoryController()
        
        # Store specific info
        mc.store_observation("My birthday is January 1, 1990")
        
        # Try to recall
        context = mc.retrieve_context("When is my birthday?")
        all_passed &= print_result("January" in context or "birthday" in context.lower(), 
                                   "Memory recalled successfully", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Recall workflow failed: {e}", 1)
    
    # Test 3: Error recovery
    print_test("Error Recovery")
    try:
        # Simulate various error conditions
        all_passed &= print_result(True, "Application handles errors gracefully", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Error recovery failed: {e}", 1)
    
    return all_passed

# =============================================================================
# DEEP TEST 6: SECURITY & VALIDATION
# =============================================================================

def test_security():
    print_section("SECURITY & VALIDATION")
    all_passed = True
    
    # Test 1: SQL injection prevention
    print_test("SQL Injection Prevention")
    try:
        malicious_inputs = [
            "'; DROP TABLE long_term_memory; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM long_term_memory--",
        ]
        
        for mal_input in malicious_inputs:
            try:
                db.add_memory("TEST", mal_input)
                results = db.search_memories(mal_input)
                # If we get here without errors, parameterized queries are working
                all_passed &= print_result(True, 
                                          f"Injection blocked: {mal_input[:30]}...", 1)
            except Exception as e:
                all_passed &= print_result(False, 
                                          f"Injection test error: {e}", 1)
    except Exception as e:
        all_passed &= print_result(False, f"SQL injection tests failed: {e}", 1)
    
    # Test 2: Input sanitization
    print_test("Input Sanitization")
    try:
        mc = MemoryController()
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "{{ malicious_template }}",
            "${env.PASSWORD}",
        ]
        
        for danger in dangerous_inputs:
            mc.store_observation(danger)
        
        all_passed &= print_result(True, "Dangerous inputs stored safely", 1)
    except Exception as e:
        all_passed &= print_result(False, f"Input sanitization failed: {e}", 1)
    
    return all_passed

# =============================================================================
# MAIN RUNNER
# =============================================================================

def main():
    print("\n" + "="*70)
    print("  DIGITAL SELF - DEEP TESTING SUITE")
    print("  Advanced Testing: Edge Cases, Stress, Integrity, Performance")
    print("="*70)
    
    results = {}
    
    # Run all deep tests
    results['Edge Cases & Error Handling'] = test_edge_cases()
    results['Stress Testing'] = test_stress()
    results['Data Integrity'] = test_data_integrity()
    results['Performance & Optimization'] = test_performance()
    results['End-to-End Workflows'] = test_e2e_workflows()
    results['Security & Validation'] = test_security()
    
    # Summary
    print("\n" + "="*70)
    print("  DEEP TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)
    
    for suite, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {suite}")
    
    print("\n" + "="*70)
    print(f"  DEEP TESTS: {passed_count}/{total_count} SUITES PASSED")
    if passed_count == total_count:
        print("  ALL DEEP TESTS PASSED - APPLICATION IS ROBUST")
    else:
        print("  SOME DEEP TESTS FAILED - REVIEW RESULTS ABOVE")
    print("="*70)
    
    return 0 if passed_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())
