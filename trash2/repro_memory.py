from brain.memory_controller import MemoryController

def test_repro():
    mc = MemoryController()
    
    # Case 1: Punctuation after key word
    input1 = "Remember, my birthday was 27th December."
    is_cmd1, _ = mc.process_input(input1)
    print(f"Input: '{input1}' -> Is Command? {is_cmd1}")
    
    # Case 2: Phrased as question
    input2 = "Can you remember my birthday was 27th December?"
    # Check if process_input catches it
    is_cmd2, _ = mc.process_input(input2)
    print(f"Input: '{input2}' -> Is Command? {is_cmd2}")
    
    # Check if store_observation would catch input2
    # We mock db.add_memory to see if it gets called
    import brain.db as db
    original_add = db.add_memory
    db.add_memory = lambda cat, content: print(f"   [DB SAVE] Category: {cat}, Content: {content}")
    
    print(f"Input: '{input2}' -> Checking store_observation...")
    mc.store_observation(input2)
    
    db.add_memory = original_add

if __name__ == "__main__":
    test_repro()
