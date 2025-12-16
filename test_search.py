"""Quick test of search"""
from brain import db

print("Testing search for 'birthday':")
results = db.search_memories("when is test_memory_birthday")
print(f"Found {len(results)} results")
for r in results:
    print(f"  - {r['content']}")

print("\nDirect search for 'test_memory':")
results = db.search_memories("test_memory")
print(f"Found {len(results)} results")
for r in results:
    print(f"  - {r['content']}")
