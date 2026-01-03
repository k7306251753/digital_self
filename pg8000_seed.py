import pg8000.native
import ssl

# Credentials
host = "dpg-d23qi063jp1c73a8ta10-a.oregon-postgres.render.com"
database = "userdb_uzyn"
user = "general"
password = "rECxD46Fyl2zjHo7BUx9Y3XoiVSXDZUc"

def check_and_seed():
    try:
        # Create an SSL context
        # Render usually uses a certificate that is valid for the hostname
        ssl_context = ssl.create_default_context()
        # If standard verification fails, we might need to adjust this, 
        # but let's try standard first.
        
        print(f"Connecting to {host} via pg8000 with SSL...")
        db = pg8000.native.Connection(
            user=user,
            password=password,
            host=host,
            database=database,
            port=5432,
            ssl_context=ssl_context
        )
        
        print("Connected successfully!")
        
        # Check count
        res = db.run("SELECT COUNT(*) FROM participant")
        count = res[0][0]
        print(f"Current participant count: {count}")
        
        if count == 0:
            print("Seeding dummy data...")
            participants = [
                ("admin_user", "Admin Administrator", "Engineering", "ADMIN", 1234567890, "password123"),
                ("john_doe", "John Doe", "Sales", "USER", 9876543210, "paxpass"),
                ("jane_smith", "Jane Smith", "HR", "USER", 5554443332, "securepass")
            ]
            
            for username, name, dept, ptype, bank, pwd in participants:
                # In pg8000.native, we use :1, :2 etc for parameters
                db.run("""
                    INSERT INTO participant (user_name, full_name, department, user_type, bank_account_number, password)
                    VALUES (:username, :name, :dept, :ptype, :bank, :pwd)
                """, username=username, name=name, dept=dept, ptype=ptype, bank=bank, pwd=pwd)
                
                # Get the last ID
                res_id = db.run("SELECT user_id FROM participant WHERE user_name = :username", username=username)
                user_id = res_id[0][0]
                
                # Add Address
                db.run("""
                    INSERT INTO participant_address (street, city, state, country, zip_code, participant_id)
                    VALUES (:street, :city, :state, :country, :zip, :pid)
                """, street="123 Main St", city="Tech City", state="Digital", country="Internet", zip="10101", pid=user_id)
                
                # Add Phone
                db.run("""
                    INSERT INTO participant_phonenumber (number, type, participant_id)
                    VALUES (:num, :type, :pid)
                """, num="555-0101", type="WORK", pid=user_id)
                
                # Add Email
                db.run("""
                    INSERT INTO participant_email (email, type, participant_id)
                    VALUES (:email, :type, :pid)
                """, email=f"{username}@example.com", type="WORK", pid=user_id)
                
            print("Seeding completed successfully.")
        else:
            print("Data already exists. Skipping seeding.")
            res_users = db.run("SELECT user_id, user_name, full_name FROM participant LIMIT 5")
            print("\nExisting Users:")
            for row in res_users:
                 print(f"ID: {row[0]} | Username: {row[1]} | Name: {row[2]}")
                 
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_and_seed()
