import psycopg2
from psycopg2.extras import RealDictCursor

# Local PostgreSQL Credentials matching application.properties
DB_DSN = "postgres://postgres:root@localhost:5432/antigravity"

def connect():
    try:
        conn = psycopg2.connect(DB_DSN)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def seed_users():
    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Ensure 5 participants with distinct identities
        participants = [
            ("user1", "Alice Alisson", "Engineering", "USER", 1111111111, "pass1"),
            ("user2", "Bob Robertson", "Sales", "USER", 2222222222, "pass2"),
            ("user3", "Charlie Chapman", "HR", "USER", 3333333333, "pass3"),
            ("user4", "David Davidson", "Marketing", "USER", 4444444444, "pass4"),
            ("user5", "Eve Evenson", "Design", "USER", 5555555555, "pass5")
        ]
        
        for username, name, dept, ptype, bank, pwd in participants:
            # Check if user exists
            cur.execute("SELECT user_id FROM participant WHERE user_name = %s", (username,))
            existing = cur.fetchone()
            
            if not existing:
                print(f"Creating user: {username}")
                cur.execute("""
                    INSERT INTO participant (user_name, full_name, department, user_type, bank_account_number, password, points)
                    VALUES (%s, %s, %s, %s, %s, %s, 1000)
                    RETURNING user_id
                """, (username, name, dept, ptype, bank, pwd))
                
                user_id = cur.fetchone()['user_id']
                
                # Add Email
                cur.execute("""
                    INSERT INTO participant_email (email, type, participant_id)
                    VALUES (%s, %s, %s)
                """, (f"{username}@example.com", "WORK", user_id))
            else:
                print(f"User {username} already exists.")
                
        conn.commit()
        print("Seeding completed successfully.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        conn.rollback()
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == "__main__":
    seed_users()
