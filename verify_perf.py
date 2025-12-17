import time
from brain import db

def verify_performance():
    print("Initializing DB...")
    start = time.time()
    db.init_db()
    print(f"DB Init took: {time.time() - start:.4f}s")

    # Measure Write Speed (should reuse connection)
    print("\nWriting 50 memories...")
    start = time.time()
    for i in range(50):
        db.add_memory("FACT", f"Perf test memory item {i} - checking indexing capability")
    duration = time.time() - start
    print(f"Write 50 items took: {duration:.4f}s (Avg: {duration/50:.4f}s/item)")

    # Measure Read Speed
    print("\nReading recent memories...")
    start = time.time()
    mems = db.get_memories(limit=50)
    print(f"Read 50 items took: {time.time() - start:.4f}s")
    print(f"Retrieved {len(mems)} items.")

    # Measure Search Speed
    print("\nSearching memories (expecting fast retrieval via index)...")
    start = time.time()
    results = db.search_memories("indexing capability")
    print(f"Search took: {time.time() - start:.4f}s")
    print(f"Found {len(results)} matches.")

    print("\nClosing Pool...")
    db.close_pool()
    print("Done.")

if __name__ == "__main__":
    verify_performance()
