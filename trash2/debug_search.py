"""Debug search query"""
from brain import db

query = "when is test_memory_birthday"
stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
              'when', 'what', 'where', 'who', 'how', 'do', 'did', 'does', 
              'i', 'my', 'me', 'you', 'your', 'did', 'get', 'got'}
words = [w for w in query.lower().split() if w.isalnum() and w not in stop_words]

print(f"Query: '{query}'")
print(f"Extracted keywords: {words}")
print(f"Number of keywords: {len(words)}")

if not words:
    print("No keywords extracted - would fall back to full query search")
else:
    print(f"Would search for: {words}")

# Try the actual search
results = db.search_memories(query)
print(f"\nActual search results: {len(results)}")
for r in results:
    print(f"  - {r['content']}")
