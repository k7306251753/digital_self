"""
Clean up old dirty memories from the database
"""
from brain import db

print("Cleaning up old messy memories...")

conn = db.get_db_connection()
if conn:
    c = conn.cursor()
    
    # Delete memories that look like they were stored verbatim with command words
    patterns_to_clean = [
        "%just remember%",
        "%ok remember%",
        "%ok just remember%",
        "%I already told you%",
        "%no when is my%",
        "%when I got my%",
        "%how do you know who%",
        "%ok tell me anything%",
        "%when I actually got%",
        "%got my t-shirt%",
        "%who are you actually%",
        "%yeah yes do you know%",
        "%it's so hard%",
        "%ok do you remember%",
        "%I got%",
        "%what do you know about%",
        "%who is actually%",
        "%ok leave it%",
    ]
    
    deleted_count = 0
    for pattern in patterns_to_clean:
        c.execute("DELETE FROM long_term_memory WHERE content LIKE %s", (pattern,))
        deleted_count += c.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"Deleted {deleted_count} messy memories")
    print("Database cleaned!")
else:
    print("Could not connect to database")

# Show remaining memories
print("\nRemaining memories:")
import sys
sys.path.insert(0, '.')
from debug_memory import *
