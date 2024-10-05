import uuid
from datetime import datetime
import streamlit as st

def validate_data(data):
    required_fields = [
        'job_number', 'date', 'well_name', 'pad_name', 'stage', 'job_type',
        'service_provider', 'client', 'operation', 'xml_received',
        'asr_calculated', 'full_timeblock', 'sub_activities', 'data_completeness'
    ]
    
    missing_fields = [field for field in required_fields if data.get(field) is None]
    
    if missing_fields:
        st.error(f"Please fill in the following required fields: {', '.join(missing_fields)}")
        return False
    
    return True

def generate_unique_id():
    return str(uuid.uuid4())
