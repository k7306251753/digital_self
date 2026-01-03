import sys
import os

# Ensure we can import from the brain module
sys.path.append(os.getcwd())

def check_step(name, status, details=""):
    status_str = "OK" if status else "FAIL"
    print(f"[{status_str}] {name} {details}")

print("Verifying Digital Self Setup...")

# 1. Check Python
check_step("Python Version", sys.version_info >= (3, 10), f"({'.'.join(map(str, sys.version_info[:3]))})")

# 2. Check Memory (PostgreSQL)
print("\n-- Check Memory --")
try:
    from brain import db
    db.init_db()
    check_step("PostgreSQL Connection", True)
    
    # Try to add a test memory
    try:
        mem_id = db.add_memory("FACT", "Testing verification")
        if mem_id:
            check_step("Add Memory", True)
            db.delete_memory(mem_id)
        else:
            check_step("Add Memory", False, "(Failed to get memory ID)")
    except Exception as e:
        check_step("Memory Logic", False, f"({e})")
except Exception as e:
    check_step("PostgreSQL Connection", False, f"({e})")

# 3. Check LLM (Ollama)
print("\n-- Check LLM --")
try:
    from brain.llm_interface import LLMInterface
    brain = LLMInterface()
    
    if brain.is_ollama_connected():
        check_step("Ollama Connection", True)
        
        # Simple chat
        try:
            resp = brain.chat("Hello")
            # Handle object/dict
            content = ""
            if hasattr(resp, 'message'): content = resp.message.content
            elif isinstance(resp, dict) and 'message' in resp: content = resp['message']['content']
            elif isinstance(resp, str): content = resp
            
            if content and "Error" not in content:
                 check_step("Basic Chat", True, f"(Response: {content[:30]}...)")
            else:
                 check_step("Basic Chat", False, f"(Invalid content: {content})")
        except Exception as e:
            check_step("Chat Exception", False, f"({e})")
    else:
        check_step("Ollama Connection", False, "(Ensure `ollama serve` is running)")

except ImportError:
    check_step("LLM Module Import", False)
except Exception as e:
    check_step("LLM Check Crash", False, f"({e})")

# 4. Check Voice
print("\n-- Check Voice --")
try:
    from brain.voice_engine import VoiceEngine
    ve = VoiceEngine()
    check_step("Voice Engine Init", True)
except Exception as e:
    check_step("Voice Engine Init", False, f"({e})")

print("\nVerification Complete.")

