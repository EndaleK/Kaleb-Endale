import psycopg2
import os
from datetime import datetime, timedelta
import random

def add_sample_data():
    conn = psycopg2.connect(
        host=os.environ["PGHOST"],
        database=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        port=os.environ["PGPORT"]
    )
    
    cur = conn.cursor()
    
    # Check if there's existing data
    cur.execute("SELECT COUNT(*) FROM qc_data")
    count = cur.fetchone()[0]
    
    if count == 0:
        # Add sample data
        operations = ["Frac", "Wireline", "Pump Down"]
        service_providers = ["Provider A", "Provider B", "Provider C"]
        
        for i in range(20):
            date = datetime.now() - timedelta(days=i)
            data = {
                "id": f"sample_{i}",
                "job_number": f"JOB{i:03d}",
                "date": date.date(),
                "pad_name": f"Pad{i%5 + 1}",
                "well_name": f"Well{i%10 + 1}",
                "stage": random.randint(1, 10),
                "job_type": random.choice(["Fracturing", "Wireline", "Pump Down"]),
                "service_provider": random.choice(service_providers),
                "client": f"Client{i%3 + 1}",
                "start_time": datetime.now().time(),
                "end_time": (datetime.now() + timedelta(hours=random.randint(1, 5))).time(),
                "comments": f"Sample comment {i}",
                "operation": random.choice(operations),
                "submitted_at": datetime.now(),
                "xml_received": random.choice([True, False]),
                "asr_calculated": random.choice([True, False]),
                "full_timeblock": random.choice([True, False]),
                "sub_activities": random.choice([True, False]),
                "data_completeness": random.randint(50, 100)
            }
            
            cur.execute("""
                INSERT INTO qc_data (id, job_number, date, pad_name, well_name, stage, job_type, service_provider, client, start_time, end_time, comments, operation, submitted_at, xml_received, asr_calculated, full_timeblock, sub_activities, data_completeness)
                VALUES (%(id)s, %(job_number)s, %(date)s, %(pad_name)s, %(well_name)s, %(stage)s, %(job_type)s, %(service_provider)s, %(client)s, %(start_time)s, %(end_time)s, %(comments)s, %(operation)s, %(submitted_at)s, %(xml_received)s, %(asr_calculated)s, %(full_timeblock)s, %(sub_activities)s, %(data_completeness)s)
            """, data)
        
        conn.commit()
        print("Sample data added successfully.")
    else:
        print(f"Database already contains {count} records. No sample data added.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    add_sample_data()
