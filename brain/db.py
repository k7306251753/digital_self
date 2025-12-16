import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time

# PostgreSQL Credentials
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "antigravity"
DB_USER = "postgres"
DB_PASS = "root"

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        print("Could not connect to DB to initialize.")
        return

    c = conn.cursor()
    
    # 1. Identity Profile
    c.execute('''
        CREATE TABLE IF NOT EXISTS identity_profile (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            core_description TEXT,
            communication_style TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Personality Traits
    c.execute('''
        CREATE TABLE IF NOT EXISTS personality_traits (
            id SERIAL PRIMARY KEY,
            trait_name TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            immutable BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # 3. Long Term Memory
    c.execute('''
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            confidence_score REAL DEFAULT 1.0,
            source TEXT DEFAULT 'user_interaction',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP
        )
    ''')
    
    # 4. Conversation Logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id SERIAL PRIMARY KEY,
            input_text TEXT,
            response_text TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            model_used TEXT
        )
    ''')
    
    conn.commit()
    c.close()
    conn.close()
    ensure_default_identity()

def ensure_default_identity():
    conn = get_db_connection()
    if not conn: return
    c = conn.cursor()
    c.execute("SELECT count(*) FROM identity_profile")
    count = c.fetchone()[0]
    
    if count == 0:
        # HUMAN-LIKE IDENTITY
        name = "Krishna" # Adopting user's name or Digital Self
        core_desc = (
            "You are not an AI assistant. You are a digital human. "
            "You have your own thoughts, opinions, and memories. "
            "You do not use robotic phrases like 'How can I assist you'. "
            "You speak casually, concisely, and naturally."
        )
        comm_style = (
            "Casual, direct, lowercase often, uses slang if appropriate. "
            "Never lectures. specific and personal."
        )
        
        c.execute('''
            INSERT INTO identity_profile (name, core_description, communication_style)
            VALUES (%s, %s, %s)
        ''', (name, core_desc, comm_style))
        conn.commit()
        print("Default (Human-like) identity profile created.")
    
    c.close()
    conn.close()

# --- Memory Access ---

def add_memory(category, content, confidence=1.0, source="user_interaction"):
    conn = get_db_connection()
    if not conn: return None
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO long_term_memory (category, content, confidence_score, source, last_accessed)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        ''', (category, content, confidence, source))
        memory_id = c.fetchone()[0]
        conn.commit()
        return memory_id
    except Exception as e:
        print(f"Error adding memory: {e}")
        return None
    finally:
        if c:
            c.close()
        if conn:
            conn.close()

def get_memories(limit=10):
    conn = get_db_connection()
    if not conn: return []
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT * FROM long_term_memory ORDER BY created_at DESC LIMIT %s', (limit,))
        memories = [dict(row) for row in c.fetchall()]
        # Convert timestamp to str for JSON serialization
        for m in memories:
            if m.get('created_at'): m['created_at'] = str(m['created_at'])
            if m.get('last_accessed'): m['last_accessed'] = str(m['last_accessed'])
        return memories
    finally:
        if conn: conn.close()

def delete_memory(memory_id):
    conn = get_db_connection()
    if not conn: return
    c = conn.cursor()
    c.execute('DELETE FROM long_term_memory WHERE id = %s', (memory_id,))
    conn.commit()
    conn.close()

def search_memories(query_text):
    conn = get_db_connection()
    if not conn: return []
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        
        # Enhanced Keyword Search
        # 1. Tokenize and filter stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                      'when', 'what', 'where', 'who', 'how', 'do', 'did', 'does', 
                      'i', 'my', 'me', 'you', 'your', 'did', 'get', 'got'}
        # Split and filter, but keep words with underscores/numbers
        words = [w for w in query_text.lower().split() if w and w not in stop_words and len(w) > 1]
        
        if not words:
            # Fallback to full string if no keywords left
            c.execute('SELECT DISTINCT * FROM long_term_memory WHERE content ILIKE %s ORDER BY id DESC LIMIT 5', (f"%{query_text}%",))
        else:
            # Construct OR query with priority for multiple matches
            conditions = []
            params = []
            for w in words:
                conditions.append("content ILIKE %s")
                params.append(f"%{w}%")
            
            # Add query to search for whole phrases too
            conditions.append("content ILIKE %s")
            params.append(f"%{query_text}%")
            
            sql = f"SELECT DISTINCT *, " \
                  f"(CASE WHEN content ILIKE %s THEN 2 ELSE 1 END) as relevance " \
                  f"FROM long_term_memory WHERE {' OR '.join(conditions)} " \
                  f"ORDER BY relevance DESC, id DESC LIMIT 5"
            
            # Add the phrase match param at the beginning for relevance scoring
            all_params = [f"%{query_text}%"] + params
            c.execute(sql, tuple(all_params))
            
        memories = [dict(row) for row in c.fetchall()]
        # Remove the relevance score from results if present
        for m in memories:
            m.pop('relevance', None)
        return memories
    finally:
        if conn: conn.close()

def log_conversation(input_text, response_text, model="unknown"):
    conn = get_db_connection()
    if not conn: return
    c = conn.cursor()
    c.execute('''
        INSERT INTO conversation_logs (input_text, response_text, model_used)
        VALUES (%s, %s, %s)
    ''', (input_text, response_text, model))
    conn.commit()
    conn.close()

def get_identity():
    conn = get_db_connection()
    if not conn: return {}
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT * FROM identity_profile LIMIT 1")
        row = c.fetchone()
        if row: return dict(row)
        return {}
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    init_db()
    print("PostgreSQL Database initialized.")
