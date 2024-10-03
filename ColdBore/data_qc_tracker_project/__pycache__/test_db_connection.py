import psycopg2
from psycopg2 import OperationalError

def create_connection():
    try:
        connection = psycopg2.connect(
            database="your_database_name",
            user="your_username",
            password="your_password",
            host="127.0.0.1",
            port="5433"  # Change to 5432 if using the default port
        )
        print("Connection to PostgreSQL DB successful")
        return connection
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None

if __name__ == "__main__":
    conn = create_connection()
    if conn:
        conn.close()
