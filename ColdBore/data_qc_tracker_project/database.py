import psycopg2
from psycopg2.extras import RealDictCursor
import os
import streamlit as st
from datetime import datetime
import time
from dotenv import load_dotenv
import requests

load_dotenv()  # This loads the variables from .env file

def init_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="your_database_name",  # Replace with your actual database name
            user="Letko",  # Changed to the user shown in the lsof output
            password="your_postgres_password"  # Replace with your actual PostgreSQL password
        )
        return conn
    except psycopg2.Error as e:
        st.error(f"Unable to connect to the database. Error: {e}")
        raise

def check_connection(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception:
        return False

def create_table(conn):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS qc_data (
                    id TEXT PRIMARY KEY,
                    job_number TEXT,
                    date DATE,
                    submitted_at TIMESTAMP,
                    well_name TEXT,
                    pad_name TEXT,
                    stage INTEGER,
                    job_type TEXT,
                    client TEXT,
                    comments TEXT,
                    operation TEXT,
                    xml_received BOOLEAN,
                    asr_calculated BOOLEAN,
                    full_timeblock BOOLEAN,
                    sub_activities BOOLEAN,
                    data_completeness INTEGER
                )
            """)
            
            # Add indexes for frequently queried columns
            cur.execute("CREATE INDEX IF NOT EXISTS idx_date ON qc_data (date)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_pad_name ON qc_data (pad_name)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_well_name ON qc_data (well_name)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_operation ON qc_data (operation)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_job_number ON qc_data (job_number)")
            
            conn.commit()
        print("Table structure and indexes updated successfully.")
    except Exception as e:
        print(f"Error creating table or adding indexes: {str(e)}")
        conn.rollback()  # Rollback the transaction if an error occurs
        raise

def insert_data(conn, data):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        # Ensure data_completeness is stored as an integer
        data['data_completeness'] = int(data['data_completeness'])
        
        # Format submitted_at to include both date and time
        current_date = datetime.now().date()
        time_obj = datetime.strptime(data['submitted_at'], '%H:%M:%S').time()
        data['submitted_at'] = datetime.combine(current_date, time_obj)
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO qc_data (id, job_number, date, submitted_at, well_name, pad_name, stage, job_type, 
                                     client, comments, operation, xml_received, asr_calculated, 
                                     full_timeblock, sub_activities, data_completeness)
                VALUES (%(id)s, %(job_number)s, %(date)s, %(submitted_at)s, %(well_name)s, %(pad_name)s, %(stage)s, 
                        %(job_type)s, %(client)s, %(comments)s, %(operation)s, %(xml_received)s, 
                        %(asr_calculated)s, %(full_timeblock)s, %(sub_activities)s, %(data_completeness)s)
            """, data)
            conn.commit()
        st.success("Data inserted successfully.")
    except Exception as e:
        st.error(f"Error inserting data: {str(e)}")
        conn.rollback()  # Rollback the transaction if an error occurs
        raise

def fetch_data(conn):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM qc_data ORDER BY submitted_at DESC")
            data = cur.fetchall()
        return data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        raise

def update_data(conn, data):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE qc_data
                SET job_number = %(job_number)s, date = %(date)s, well_name = %(well_name)s, pad_name = %(pad_name)s, stage = %(stage)s, job_type = %(job_type)s,
                    client = %(client)s, comments = %(comments)s, operation = %(operation)s, xml_received = %(xml_received)s,
                    asr_calculated = %(asr_calculated)s, full_timeblock = %(full_timeblock)s, sub_activities = %(sub_activities)s, data_completeness = %(data_completeness)s
                WHERE id = %(id)s
            """, data)
            conn.commit()
        st.success("Data updated successfully.")
    except Exception as e:
        st.error(f"Error updating data: {str(e)}")
        conn.rollback()  # Rollback the transaction if an error occurs
        raise

def delete_data(conn, id):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM qc_data WHERE id = %s", (id,))
            conn.commit()
        st.success("Data deleted successfully.")
    except Exception as e:
        st.error(f"Error deleting data: {str(e)}")
        conn.rollback()  # Rollback the transaction if an error occurs
        raise

def rename_contractor_to_service_provider(conn):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor() as cur:
            # Check if the column exists before trying to rename it
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'qc_data' AND column_name = 'contractor'
            """)
            if cur.fetchone():
                cur.execute("""
                    ALTER TABLE qc_data
                    RENAME COLUMN contractor TO service_provider
                """)
                conn.commit()
                st.success("Successfully renamed 'contractor' to 'service_provider' in the database.")
            else:
                st.info("Column 'service_provider' already exists. No renaming necessary.")
    except Exception as e:
        st.error(f"Error renaming 'contractor' to 'service_provider': {str(e)}")
        conn.rollback()  # Rollback the transaction if an error occurs
        raise

def reorder_columns(conn):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor() as cur:
            # Check if the job_number column exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'qc_data' AND column_name = 'job_number'
            """)
            if cur.fetchone():
                # Update null values in job_number column
                cur.execute("""
                    UPDATE qc_data
                    SET job_number = 'UNKNOWN'
                    WHERE job_number IS NULL;
                """)
                
                # Reorder columns
                cur.execute("""
                    ALTER TABLE qc_data
                    ALTER COLUMN job_number DROP DEFAULT,
                    ALTER COLUMN job_number TYPE TEXT,
                    ALTER COLUMN job_number SET NOT NULL;

                    CREATE TABLE qc_data_new (
                        id TEXT PRIMARY KEY,
                        job_number TEXT NOT NULL,
                        date DATE,
                        submitted_at TIME,
                        well_name TEXT,
                        pad_name TEXT,
                        stage INTEGER,
                        job_type TEXT,
                        client TEXT,
                        comments TEXT,
                        operation TEXT,
                        xml_received BOOLEAN,
                        asr_calculated BOOLEAN,
                        full_timeblock BOOLEAN,
                        sub_activities BOOLEAN,
                        data_completeness INTEGER
                    );

                    INSERT INTO qc_data_new
                    SELECT id, job_number, date, submitted_at::TIME, well_name, pad_name, stage, job_type, 
                           client, comments, operation, xml_received, asr_calculated,
                           full_timeblock, sub_activities, data_completeness
                    FROM qc_data;

                    DROP TABLE qc_data;
                    ALTER TABLE qc_data_new RENAME TO qc_data;

                    CREATE INDEX idx_date ON qc_data (date);
                    CREATE INDEX idx_pad_name ON qc_data (pad_name);
                    CREATE INDEX idx_well_name ON qc_data (well_name);
                    CREATE INDEX idx_operation ON qc_data (operation);
                    CREATE INDEX idx_job_number ON qc_data (job_number);
                """)
                conn.commit()
                st.success("Successfully reordered columns in the database.")
            else:
                st.warning("Column 'job_number' does not exist. No reordering necessary.")
    except Exception as e:
        st.error(f"Error reordering columns: {str(e)}")
        conn.rollback()  # Rollback the transaction if an error occurs
        raise

# Add this function to the database.py file

def fetch_row_by_id(conn, id):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM qc_data WHERE id = %s", (id,))
            return cur.fetchone()
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        raise

def fetch_job_info(conn, job_number):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT DISTINCT pad_name, client, job_type, array_agg(DISTINCT well_name) as well_names
                FROM qc_data
                WHERE job_number = %s
                GROUP BY pad_name, client, job_type
            """
            print(f"Executing query: {query} with job_number: {job_number}")
            cur.execute(query, (job_number,))
            result = cur.fetchone()
            print(f"Query result: {result}")
            if result:
                result['well_names'] = result['well_names'] or []  # Ensure well_names is always a list
            return result
    except Exception as e:
        print(f"Error in fetch_job_info: {str(e)}")
        st.error(f"Error fetching job info: {str(e)}")
        raise

def delete_job(conn, job_number):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor() as cur:
            print(f"Executing DELETE query for job number: {job_number}")
            cur.execute("DELETE FROM qc_data WHERE job_number = %s", (job_number,))
            rows_deleted = cur.rowcount
            print(f"Rows deleted: {rows_deleted}")
            conn.commit()
        return rows_deleted
    except Exception as e:
        print(f"Error in delete_job: {str(e)}")
        st.error(f"Error deleting job: {str(e)}")
        conn.rollback()
        raise

def job_number_exists(conn, job_number):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM qc_data WHERE job_number = %s)", (job_number,))
            return cur.fetchone()[0]
    except Exception as e:
        st.error(f"Error checking if job number exists: {str(e)}")
        raise

def fetch_job_data(conn, job_number):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM qc_data
                WHERE job_number = %s
                ORDER BY date, submitted_at
            """, (job_number,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error in fetch_job_data: {str(e)}")
        st.error(f"Error fetching job data: {str(e)}")
        raise

def update_job_details(conn, job_number, pad_name, client, job_type):
    if not check_connection(conn):
        st.error("Database connection is closed. Attempting to reconnect...")
        conn = init_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE qc_data
                SET pad_name = %s, client = %s, job_type = %s
                WHERE job_number = %s
            """, (pad_name, client, job_type, job_number))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error in update_job_details: {str(e)}")
        st.error(f"Error updating job details: {str(e)}")
        conn.rollback()
        return False

def fetch_grafana_alerts(grafana_url, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{grafana_url}/api/alerts", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching Grafana alerts: {str(e)}")
        return None