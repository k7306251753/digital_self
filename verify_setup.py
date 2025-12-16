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

# 2. Check Memory (ChromaDB)
print("\n-- Check Memory --")
try:
    from brain.memory import Memory
    mem = Memory(collection_name="test_verification")
    if mem.collection:
        check_step("ChromaDB Initialization", True)
        try:
            mem.add_memory("test_memory")
            check_step("Add Memory", True)
            res = mem.retrieve_context("test")
            check_step("Retrieve Memory", True, f"(found {len(res)} results)" if res else "")
        except Exception as e:
            check_step("Memory Logic", False, f"({e})")
    else:
        check_step("ChromaDB Initialization", False, "(Returned None)")
except ImportError:
    check_step("Brain Module Import", False)
except Exception as e:
    check_step("Memory Check Crash", False, f"({e})")

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
            if isinstance(resp, str) and "Error" not in resp:
                 check_step("Basic Chat", True, f"(Response len: {len(resp)})")
            else:
                 check_step("Basic Chat", False, f"(Error in response: {resp})")
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

