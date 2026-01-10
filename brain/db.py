import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
import time

# PostgreSQL Credentials
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "antigravity"
DB_USER = "postgres"
DB_PASS = "root"

# Global Connection Pool
connection_pool = None

def init_pool():
    global connection_pool
    if connection_pool:
        return
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        print("Database connection pool initialized.")
    except Exception as e:
        print(f"Error initializing connection pool: {e}")

def get_db_connection():
    global connection_pool
    if not connection_pool:
        init_pool()
    
    if not connection_pool:
        return None
        
    try:
        return connection_pool.getconn()
    except Exception as e:
        print(f"Error getting connection from pool: {e}")
        return None

def return_connection(conn):
    if connection_pool and conn:
        connection_pool.putconn(conn)

def close_pool():
    if connection_pool:
        connection_pool.closeall()

def init_db():
    conn = get_db_connection()
    if not conn:
        print("Could not connect to DB to initialize.")
        return

    c = None
    try:
        c = conn.cursor()
        
        # 0. Extensions for performance
        try:
            c.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
        except Exception as e:
            print(f"Warning: Could not create pg_trgm extension. Search optimization might be limited. Error: {e}")
            conn.rollback() 
        
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
                user_id INTEGER,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence_score REAL DEFAULT 1.0,
                source TEXT DEFAULT 'user_interaction',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP
            )
        ''')

        # Add user_id column if it doesn't exist (migration)
        try:
            c.execute('ALTER TABLE long_term_memory ADD COLUMN IF NOT EXISTS user_id INTEGER;')
        except Exception:
            conn.rollback()
            c = conn.cursor()

        # Add Generalized Inverted Index (GIN) for fast text search
        try:
            c.execute('CREATE INDEX IF NOT EXISTS idx_memory_content ON long_term_memory USING GIN (content gin_trgm_ops);')
        except Exception:
            pass
        
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

        # 5. Chat History Organization
        c.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY, 
                user_id INTEGER,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                session_id TEXT REFERENCES chat_sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Error initializing DB schema: {e}")
        conn.rollback()
    finally:
        if c: c.close()
        return_connection(conn)
        
    ensure_default_identity()

def ensure_default_identity():
    conn = get_db_connection()
    if not conn: return
    c = None
    try:
        c = conn.cursor()
        c.execute("SELECT count(*) FROM identity_profile")
        count = c.fetchone()[0]
        
        if count == 0:
            # HUMAN-LIKE IDENTITY
            name = "Krishna" 
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
    except Exception as e:
        print(f"Error ensuring identity: {e}")
    finally:
        if c: c.close()
        return_connection(conn)

# --- Memory Access ---

def add_memory(category, content, user_id=None, confidence=1.0, source="user_interaction"):
    conn = get_db_connection()
    if not conn: return None
    c = None
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO long_term_memory (user_id, category, content, confidence_score, source, last_accessed)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        ''', (user_id, category, content, confidence, source))
        memory_id = c.fetchone()[0]
        conn.commit()
        return memory_id
    except Exception as e:
        print(f"Error adding memory: {e}")
        return None
    finally:
        if c: c.close()
        return_connection(conn)

def get_memories(user_id=None, limit=10):
    conn = get_db_connection()
    if not conn: return []
    c = None
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        if user_id:
            c.execute('SELECT * FROM long_term_memory WHERE user_id = %s ORDER BY created_at DESC LIMIT %s', (user_id, limit))
        else:
            c.execute('SELECT * FROM long_term_memory ORDER BY created_at DESC LIMIT %s', (limit,))
        memories = [dict(row) for row in c.fetchall()]
        # Convert timestamp to str for JSON serialization
        for m in memories:
            if m.get('created_at'): m['created_at'] = str(m['created_at'])
            if m.get('last_accessed'): m['last_accessed'] = str(m['last_accessed'])
        return memories
    finally:
        if c: c.close()
        return_connection(conn)

def delete_memory(memory_id):
    conn = get_db_connection()
    if not conn: return
    c = None
    try:
        c = conn.cursor()
        c.execute('DELETE FROM long_term_memory WHERE id = %s', (memory_id,))
        conn.commit()
    finally:
        if c: c.close()
        return_connection(conn)

def search_memories(query_text, user_id=None):
    conn = get_db_connection()
    if not conn: return []
    c = None
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        
        # Enhanced Keyword Search
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                      'when', 'what', 'where', 'who', 'how', 'do', 'did', 'does', 
                      'i', 'my', 'me', 'you', 'your', 'did', 'get', 'got'}
        # Clean punctuation from query for word extraction
        import string
        translator = str.maketrans('', '', string.punctuation)
        clean_query_words = query_text.translate(translator).lower().split()
        
        words = [w for w in clean_query_words if w and w not in stop_words and len(w) > 1]
        
        if not words:
            # Fallback to full string if no keywords left
            if user_id:
                c.execute('SELECT DISTINCT * FROM long_term_memory WHERE user_id = %s AND content ILIKE %s ORDER BY id DESC LIMIT 5', (user_id, f"%{query_text}%",))
            else:
                c.execute('SELECT DISTINCT * FROM long_term_memory WHERE content ILIKE %s ORDER BY id DESC LIMIT 5', (f"%{query_text}%",))
        else:
            # Construct OR query with priority for multiple matches
            conditions = []
            params = []
            for w in words:
                conditions.append("content ILIKE %s")
                params.append(f"%{w}%")
            
            # Add filter for user_id
            user_filter = "user_id = %s AND " if user_id else ""
            
            # Add query to search for whole phrases too
            conditions.append("content ILIKE %s")
            params.append(f"%{query_text}%")
            
            sql = f"SELECT DISTINCT *, " \
                  f"(CASE WHEN content ILIKE %s THEN 2 ELSE 1 END) as relevance " \
                  f"FROM long_term_memory WHERE {user_filter}({' OR '.join(conditions)}) " \
                  f"ORDER BY relevance DESC, id DESC LIMIT 5"
            
            all_params = [f"%{query_text}%"]
            if user_id: all_params.append(user_id)
            all_params += params
            c.execute(sql, tuple(all_params))
            
        memories = [dict(row) for row in c.fetchall()]
        for m in memories:
            m.pop('relevance', None)
        return memories
    finally:
        if c: c.close()
        return_connection(conn)

def log_conversation(input_text, response_text, model="unknown"):
    conn = get_db_connection()
    if not conn: return
    c = None
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO conversation_logs (input_text, response_text, model_used)
            VALUES (%s, %s, %s)
        ''', (input_text, response_text, model))
        conn.commit()
    finally:
        if c: c.close()
        return_connection(conn)

def get_identity():
    conn = get_db_connection()
    if not conn: return {}
    c = None
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT * FROM identity_profile LIMIT 1")
        row = c.fetchone()
        if row: return dict(row)
        return {}
    finally:
        if c: c.close()
        return_connection(conn)

# --- Chat History Management ---

def create_chat_session(session_id, user_id, title="New Chat"):
    conn = get_db_connection()
    if not conn: return
    c = None
    try:
        c = conn.cursor()
        # Upsert: if exists, just update updated_at
        c.execute('''
            INSERT INTO chat_sessions (id, user_id, title) VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
        ''', (session_id, user_id, title))
        conn.commit()
    except Exception as e:
        print(f"Error creating chat session: {e}")
    finally:
        if c: c.close()
        return_connection(conn)

def rename_chat_session(session_id, new_title):
    conn = get_db_connection()
    if not conn: return
    c = None
    try:
        c = conn.cursor()
        c.execute('UPDATE chat_sessions SET title = %s WHERE id = %s', (new_title, session_id))
        conn.commit()
    except Exception as e:
        print(f"Error renaming chat session: {e}")
    finally:
        if c: c.close()
        return_connection(conn)

def add_chat_message(session_id, role, content):
    conn = get_db_connection()
    if not conn: return
    c = None
    try:
        c = conn.cursor()
        c.execute('INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)', (session_id, role, content))
        # Update session timestamp
        c.execute('UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = %s', (session_id,))
        conn.commit()
    except Exception as e:
        print(f"Error adding chat message: {e}")
    finally:
        if c: c.close()
        return_connection(conn)

def get_user_chat_sessions(user_id):
    conn = get_db_connection()
    if not conn: return []
    c = None
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT * FROM chat_sessions WHERE user_id = %s ORDER BY updated_at DESC', (user_id,))
        sessions = [dict(row) for row in c.fetchall()]
        for s in sessions:
            if s.get('created_at'): s['created_at'] = str(s['created_at'])
            if s.get('updated_at'): s['updated_at'] = str(s['updated_at'])
        return sessions
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        return []
    finally:
        if c: c.close()
        return_connection(conn)

def get_chat_messages(session_id):
    conn = get_db_connection()
    if not conn: return []
    c = None
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute('SELECT * FROM chat_messages WHERE session_id = %s ORDER BY id ASC', (session_id,))
        msgs = [dict(row) for row in c.fetchall()]
        for m in msgs:
            if m.get('timestamp'): m['timestamp'] = str(m['timestamp'])
        return msgs
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []
    finally:
        if c: c.close()
        return_connection(conn)

def delete_chat_session(session_id):
    conn = get_db_connection()
    if not conn: return
    c = None
    try:
        c = conn.cursor()
        c.execute('DELETE FROM chat_sessions WHERE id = %s', (session_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting session: {e}")
    finally:
        if c: c.close()
        return_connection(conn)


if __name__ == "__main__":
    init_db()
    print("PostgreSQL Database initialized.")
