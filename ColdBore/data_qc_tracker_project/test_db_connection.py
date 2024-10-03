import psycopg2

def test_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="your_database_name",  # Replace with your actual database name
            user="Letko",  # Changed to the user shown in the lsof output
            password="your_postgres_password"  # Replace with your actual PostgreSQL password
        )
        print("Connection successful!")
        conn.close()
    except Exception as e:
        print(f"Connection failed. Error: {e}")

if __name__ == "__main__":
    test_connection()