import psycopg2
from psycopg2.extras import RealDictCursor

# Remote PostgreSQL Credentials from application.properties
DB_URL = "jdbc:postgresql://dpg-d23qi063jp1c73a8ta10-a.oregon-postgres.render.com:5432/userdb_uzyn"
# psycopg2 needs a standard connection string or individual components
DB_DSN = "postgres://general:rECxD46Fyl2zjHo7BUx9Y3XoiVSXDZUc@dpg-d23qi063jp1c73a8ta10-a.oregon-postgres.render.com:5432/userdb_uzyn?sslmode=require"

def connect():
    try:
        conn = psycopg2.connect(DB_DSN)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def check_and_seed():
    conn = connect()
    if not conn:
        return

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if participants exist
        cur.execute("SELECT COUNT(*) FROM participant")
        count = cur.fetchone()['count']
        
        print(f"Current participant count: {count}")
        
        if count == 0:
            print("Database is empty. Seeding dummy data...")
            
            # Dummy Participants
            participants = [
                ("admin_user", "Admin Administrator", "Engineering", "ADMIN", 1234567890, "password123"),
                ("john_doe", "John Doe", "Sales", "USER", 9876543210, "paxpass"),
                ("jane_smith", "Jane Smith", "HR", "USER", 5554443332, "securepass")
            ]
            
            for username, name, dept, ptype, bank, pwd in participants:
                cur.execute("""
                    INSERT INTO participant (user_name, full_name, department, user_type, bank_account_number, password)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING user_id
                """, (username, name, dept, ptype, bank, pwd))
                
                user_id = cur.fetchone()['user_id']
                
                # Add Address
                cur.execute("""
                    INSERT INTO participant_address (street, city, state, country, zip_code, participant_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ("123 Main St", "Tech City", "Digital", "Internet", "10101", user_id))
                
                # Add Phone
                cur.execute("""
                    INSERT INTO participant_phonenumber (number, type, participant_id)
                    VALUES (%s, %s, %s)
                """, ("555-0101", "WORK", user_id))
                
                # Add Email
                cur.execute("""
                    INSERT INTO participant_email (email, type, participant_id)
                    VALUES (%s, %s, %s)
                """, (f"{username}@example.com", "WORK", user_id))
                
            conn.commit()
            print("Seeding completed successfully.")
        else:
            print("Database already has data. Skipping seeding.")
            
            # Show existing users
            cur.execute("SELECT user_id, user_name, full_name FROM participant LIMIT 5")
            rows = cur.fetchall()
            print("\nExisting Users (first 5):")
            for row in rows:
                print(f"ID: {row['user_id']} | Username: {row['user_name']} | Name: {row['full_name']}")

    except Exception as e:
        print(f"Error during check/seed: {e}")
        conn.rollback()
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == "__main__":
    check_and_seed()
