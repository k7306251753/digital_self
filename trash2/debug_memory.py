from brain import db
import time

def check():
    db.init_db()
    print("--- Current Memories ---")
    memories = db.get_memories(limit=50)
    for m in memories:
        print(f"[{m['id']}] ({m['category']}): {m['content']}")
    print("------------------------")

if __name__ == "__main__":
    check()
