import psycopg2
import sys

# DSN components
host = "dpg-d23qi063jp1c73a8ta10-a.oregon-postgres.render.com"
dbname = "userdb_uzyn"
user = "general"
password = "rECxD46Fyl2zjHo7BUx9Y3XoiVSXDZUc"

ssl_modes = ["require", "verify-full", "verify-ca", "disable", "allow", "prefer"]

def test_connection(mode):
    print(f"Testing sslmode={mode}...", end=" ")
    sys.stdout.flush()
    try:
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=mode,
            connect_timeout=10
        )
        print("SUCCESS!")
        conn.close()
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    for mode in ssl_modes:
        if test_connection(mode):
            print(f"\nRecommended sslmode: {mode}")
            break
    else:
        print("\nAll sslmodes failed. Please check network connectivity or Render access rules.")
