import uuid
from datetime import datetime

def validate_data(data):
    required_fields = ["date", "well_name", "pad_name", "stage", "job_type", "service_provider", "client", "start_time", "end_time", "operation", "xml_received", "asr_calculated"]
    return all(data.get(field) is not None for field in required_fields) and isinstance(data.get("submitted_at"), datetime)

def generate_unique_id():
    return str(uuid.uuid4())
