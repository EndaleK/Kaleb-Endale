import streamlit as st
import pandas as pd
import plotly.express as px
from database import (
    init_connection, create_table, insert_data, fetch_data, 
    update_data, delete_data, rename_contractor_to_service_provider, reorder_columns, delete_job,
    job_number_exists, fetch_job_info, fetch_job_data, update_job_details, fetch_grafana_alerts  # Add fetch_grafana_alerts here
)
from utils import validate_data, generate_unique_id
from datetime import datetime
from pandas.api.types import is_bool_dtype
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Data QC Tracker", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&family=Poppins:wght@100;200;300;400;500;600;700;800;900&display=swap');
    </style>
    """, unsafe_allow_html=True)

try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Initialize database connection
@st.cache_resource
def get_connection():
    try:
        conn = init_connection()
        create_table(conn)
        rename_contractor_to_service_provider(conn)
        reorder_columns(conn)
        return conn
    except Exception as e:
        st.error(f"Failed to connect to the database: {str(e)}")
        st.error("Please check your database configuration and ensure the PostgreSQL server is running.")
        return None

conn = get_connection()

if not conn:
    st.error("Unable to proceed without a database connection.")
    st.stop()

# Sidebar
st.sidebar.image("https://your-logo-url.com", width=200)  # Add your company logo
st.sidebar.title("Data QC Tracker")
st.sidebar.markdown("---")

# Job Management Section
st.sidebar.subheader("Job Management")

job_management_tab = st.sidebar.radio("Select Action", ["Create New Job", "Select Existing Job", "Delete Job"])

if job_management_tab == "Create New Job":
    new_job_number = st.sidebar.text_input("Enter New Job Number")
    create_new_job = st.sidebar.button("Create New Job")

    if create_new_job and new_job_number:
        if job_number_exists(conn, new_job_number):
            st.sidebar.error(f"Job number {new_job_number} already exists.")
        else:
            st.session_state.new_job_number = new_job_number
            st.session_state.show_new_job_form = True
            st.rerun()

elif job_management_tab == "Select Existing Job":
    print("Entering Select Existing Job section")
    existing_job_numbers = ["Select a job"] + [row['job_number'] for row in fetch_data(conn)]
    print(f"Existing job numbers: {existing_job_numbers}")
    selected_job_number = st.sidebar.selectbox("Select Existing Job", options=existing_job_numbers)
    print(f"Selected job number: {selected_job_number}")

    if selected_job_number != "Select a job":
        try:
            print(f"Fetching job info for job number: {selected_job_number}")
            job_info = fetch_job_info(conn, selected_job_number)
            print(f"Fetched job info: {job_info}")
            if job_info:
                st.session_state.current_job_number = selected_job_number
                st.session_state.current_job_info = {
                    "pad_name": job_info['pad_name'],
                    "client": job_info['client'],
                    "well_names": job_info['well_names'],
                    "job_type": job_info['job_type']
                }
                print(f"Updated session state: {st.session_state}")
                st.sidebar.success(f"Loaded job: {selected_job_number}")

                # Display job details with edit form
                st.subheader(f"Job Details: {selected_job_number}")
                with st.form("edit_job_details"):
                    new_pad_name = st.text_input("Pad Name", value=job_info['pad_name'])
                    new_client = st.text_input("Client", value=job_info['client'])
                    new_job_type = st.selectbox("Job Type", ["Frac", "Coil Tubing", "Snubbing"], index=["Frac", "Coil Tubing", "Snubbing"].index(job_info['job_type']))
                    
                    st.write("Well Names:")
                    for well in job_info['well_names']:
                        st.write(f"- {well}")
                    
                    if st.form_submit_button("Update Job Details"):
                        if update_job_details(conn, selected_job_number, new_pad_name, new_client, new_job_type):
                            st.success("Job details updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update job details.")

                # Fetch and display all data for this job
                job_data = fetch_job_data(conn, selected_job_number)
                if job_data:
                    st.subheader("Job Data")
                    df = pd.DataFrame(job_data)
                    st.dataframe(df)
                else:
                    st.info("No data entries found for this job.")

            else:
                st.sidebar.error(f"No information found for job number {selected_job_number}")
        except Exception as e:
            print(f"Error in Select Existing Job: {str(e)}")
            st.sidebar.error(f"An error occurred while fetching job info: {str(e)}")

elif job_management_tab == "Delete Job":
    job_to_delete = st.sidebar.selectbox("Select Job to Delete", options=["Select a job"] + [row['job_number'] for row in fetch_data(conn)])
    delete_job_button = st.sidebar.button("Delete Selected Job")

    if delete_job_button and job_to_delete != "Select a job":
        confirm_delete = st.sidebar.checkbox("Are you sure you want to delete this job? This action cannot be undone.")
        if confirm_delete:
            try:
                rows_deleted = delete_job(conn, job_to_delete)
                if rows_deleted > 0:
                    st.sidebar.success(f"Job number {job_to_delete} and all associated data deleted successfully.")
                    if 'current_job_number' in st.session_state and st.session_state.current_job_number == job_to_delete:
                        del st.session_state.current_job_number
                        if 'current_job_info' in st.session_state:
                            del st.session_state.current_job_info
                    st.rerun()
                else:
                    st.sidebar.warning(f"No data found for job number {job_to_delete}.")
            except Exception as e:
                st.sidebar.error(f"Failed to delete job: {str(e)}")
        else:
            st.sidebar.warning("Please confirm deletion by checking the box.")

# Display current job info
if 'current_job_number' in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Job Info")
    st.sidebar.info(f"Job Number: {st.session_state.current_job_number}")
    if 'current_job_info' in st.session_state:
        st.sidebar.write(f"Pad Name: {st.session_state.current_job_info['pad_name']}")
        st.sidebar.write(f"Client: {st.session_state.current_job_info['client']}")
        st.sidebar.write(f"Job Type: {st.session_state.current_job_info['job_type']}")
        st.sidebar.write("Well Names:")
        for well in st.session_state.current_job_info['well_names']:
            st.sidebar.write(f"- {well}")

# Main content
st.title("Data QC Tracker")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Data Input and View", "📉 Analysis", "Grafana Alerts"])

with tab1:
    st.header("Data Input and View")
    
    # New Job Form
    if st.session_state.get('show_new_job_form', False):
        with st.expander("New Job Setup", expanded=True):
            st.subheader(f"New Job Setup: {st.session_state.new_job_number}")
            with st.form("new_job_form"):
                col1, col2 = st.columns(2)
                with col1:
                    pad_name = st.text_input("Pad Name")
                    client = st.text_input("Client")
                with col2:
                    job_type = st.selectbox("Job Type", ["Frac", "Coil Tubing", "Snubbing"])
                    new_well = st.text_input("Add Well Name")
                
                if 'well_names' not in st.session_state:
                    st.session_state.well_names = []

                st.write("Current Well Names:")
                for i, well in enumerate(st.session_state.well_names):
                    st.write(f"- {well}")

                col3, col4 = st.columns([3, 1])
                with col3:
                    add_well = st.form_submit_button("Add Well")
                with col4:
                    submit_new_job = st.form_submit_button("Submit New Job")
            
            if add_well and new_well and new_well not in st.session_state.well_names:
                st.session_state.well_names.append(new_well)
                st.success(f"Added Well: {new_well}")
                st.rerun()

            if submit_new_job:
                new_job_data = {
                    "job_number": st.session_state.new_job_number,
                    "pad_name": pad_name,
                    "client": client,
                    "job_type": job_type,
                    "well_names": st.session_state.well_names
                }
                st.session_state.current_job_number = st.session_state.new_job_number
                st.session_state.current_job_info = new_job_data
                del st.session_state.new_job_number
                del st.session_state.show_new_job_form
                del st.session_state.well_names
                
                # Display success message with job details
                st.success("New job information saved successfully!")
                st.write("Job Details:")
                st.write(f"- Pad Name: {pad_name}")
                st.write(f"- Job Type: {job_type}")
                st.write(f"- Client: {client}")
                st.write("- Well Names:")
                for well in new_job_data['well_names']:
                    st.write(f"  • {well}")
                
                st.rerun()

    # Input Data Section
    with st.expander("Input New Data", expanded=False):
        if 'current_job_number' not in st.session_state:
            st.warning("Please set a job number first.")
        else:
            st.markdown('<div id="input-new-data"></div>', unsafe_allow_html=True)
            if 'current_job_info' in st.session_state:
                well_name = st.selectbox("Select Well", options=st.session_state.current_job_info.get('well_names', []), key="select-well")
                
                with st.form("data_input_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        date = st.date_input("Date")
                        pad_name = st.text_input("Pad Name", value=st.session_state.get('current_job_info', {}).get('pad_name', ''))
                        stage = st.number_input("Stage", min_value=1, step=1)
                        job_type = st.selectbox("Job Type", ["Frac", "Coil Tubing", "Snubbing"], 
                                                index=["Frac", "Coil Tubing", "Snubbing"].index(
                                                    st.session_state.get('current_job_info', {}).get('job_type', 'Frac')
                                                ))
                    
                    with col2:
                        operation = st.selectbox("Operation", ["Frac", "Wireline", "Pump Down", "Coil Tubing", "Perforating", "Logging", "Well Testing", "Slickline"])
                        client = st.text_input("Client", value=st.session_state.get('current_job_info', {}).get('client', ''))
                    
                    comments = st.text_area("Comments")
                    
                    col3, col4, col5 = st.columns(3)
                    
                    with col3:
                        xml_received = st.radio("XML Rec'd", ["Yes", "No"], key="xml_received")
                        full_timeblock = st.radio("Full Timeblock", ["Yes", "No"], key="full_timeblock")
                    
                    with col4:
                        asr_calculated = st.radio("ASR Calculated", ["Yes", "No"], key="asr_calculated")
                        sub_activities = st.radio("Sub Activities", ["Yes", "No"], key="sub_activities")
                    
                    with col5:
                        st.write("Data Completeness")
                        data_completeness_options = [25, 50, 75, 100]
                        data_completeness = st.radio("", data_completeness_options, format_func=lambda x: f"{x}%", horizontal=True)
                    
                    submit_button = st.form_submit_button("Submit")

                if submit_button:
                    data = {
                        "id": generate_unique_id(),
                        "job_number": st.session_state.get('current_job_number'),
                        "date": date,
                        "pad_name": pad_name,
                        "well_name": well_name,
                        "stage": stage,
                        "job_type": job_type,
                        "client": client,
                        "comments": comments,
                        "operation": operation,
                        "submitted_at": datetime.now().strftime('%H:%M:%S'),
                        "xml_received": xml_received == "Yes",
                        "asr_calculated": asr_calculated == "Yes",
                        "full_timeblock": full_timeblock == "Yes",
                        "sub_activities": sub_activities == "Yes",
                        "data_completeness": int(data_completeness),
                    }
                    
                    if validate_data(data):
                        try:
                            insert_data(conn, data)
                            st.success("Data submitted successfully!")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Error inserting data: {str(e)}")
                    else:
                        st.error("Please fill in all required fields.")
            else:
                st.warning("Please set a job number first.")

    # Database Section
    st.subheader("Database")
    
    @st.cache_data(ttl=300)
    def load_data():
        data = fetch_data(conn)
        df = pd.DataFrame(data)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["data_completeness"] = df["data_completeness"].astype(int)
            df["submitted_at"] = pd.to_datetime(df["submitted_at"]).dt.time
            
            bool_columns = ['xml_received', 'asr_calculated', 'full_timeblock', 'sub_activities']
            for col in bool_columns:
                if col in df.columns:
                    df[col] = df[col].astype(bool)
        
        return df

    df = load_data()

    if df.empty:
        st.warning("No data available in the database. Please add some data using the Input Data section above.")
    else:
        # Filtering options
        with st.expander("Filter Data", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pad_filter = st.multiselect("Pad Name", options=df["pad_name"].unique())
                well_filter = st.multiselect("Well Name", options=df["well_name"].unique())
            
            with col2:
                date_range = st.date_input("Date Range", value=(min(df["date"]), max(df["date"])), key="date_range")
                operation_filter = st.multiselect("Operation", options=df["operation"].unique())
            
            with col3:
                xml_filter = st.multiselect("XML Rec'd", options=["Yes", "No"])
                asr_filter = st.multiselect("ASR Calculated", options=["Yes", "No"])
                job_numbers = ["All"] + sorted(df["job_number"].unique().tolist())
                job_number_filter = st.selectbox("Job Number", options=job_numbers)

        # Apply filters
        mask = pd.Series(True, index=df.index)
        if pad_filter:
            mask &= df["pad_name"].isin(pad_filter)
        if well_filter:
            mask &= df["well_name"].isin(well_filter)
        if date_range:
            mask &= (df["date"] >= date_range[0]) & (df["date"] <= date_range[1])
        if operation_filter:
            mask &= df["operation"].isin(operation_filter)
        if xml_filter:
            mask &= df["xml_received"].isin([x == "Yes" for x in xml_filter])
        if asr_filter:
            mask &= df["asr_calculated"].isin([x == "Yes" for x in asr_filter])
        if job_number_filter != "All":
            mask &= df["job_number"] == job_number_filter

        filtered_df = df[mask]

        # Display filtered data
        if not filtered_df.empty:
            # Define a function to color the cells
            def color_cells(val, column):
                if column in ['xml_received', 'asr_calculated', 'full_timeblock', 'sub_activities']:
                    return 'background-color: #C8E6C9; color: #1B5E20;' if val else 'background-color: #FFCDD2; color: #B71C1C;'
                elif column == 'data_completeness':
                    return 'background-color: #C8E6C9' if val == 100 else 'background-color: #FFCDD2'
                return ''

            # Apply the styling
            styled_df = filtered_df.style.apply(lambda x: [color_cells(v, x.name) for v in x])

            # Display the styled dataframe
            st.dataframe(styled_df)
        else:
            st.warning("No data available based on the current filters.")

        # Edit Data
        with st.expander("Edit Data", expanded=False):
            st.subheader("Edit or Delete Data")
            row_to_edit = st.selectbox("Select a row to edit or delete", filtered_df.index)
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Edit Selected Row"):
                    st.session_state.editing = True
                    st.session_state.editing_row = filtered_df.loc[row_to_edit]
            
            with col2:
                if st.button("Delete Selected Row"):
                    try:
                        delete_data(conn, filtered_df.loc[row_to_edit]["id"])
                        st.success("Row deleted successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting data: {str(e)}")

with tab2:
    st.header("Data Analysis")
    
    if df.empty:
        st.warning("No data available for analysis. Please add some data using the Data Input tab.")
    else:
        # Calculate KPIs
        total_jobs = len(filtered_df)
        unique_wells = filtered_df["well_name"].nunique()
        unique_pads = filtered_df["pad_name"].nunique()
        avg_completeness = filtered_df["data_completeness"].mean()
        
        filtered_df['xml_received'] = filtered_df['xml_received'].map({True: 1, False: 0})
        filtered_df['asr_calculated'] = filtered_df['asr_calculated'].map({True: 1, False: 0})
        
        xml_received_pct = (filtered_df["xml_received"].mean() * 100) if total_jobs > 0 else 0
        asr_calculated_pct = (filtered_df["asr_calculated"].mean() * 100) if total_jobs > 0 else 0

        # Display KPIs
        st.subheader("Key Performance Indicators")
        
        # Wrap KPIs in a container
        st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Jobs", total_jobs)
        col1.metric("Unique Wells", unique_wells)
        col2.metric("Unique Pads", unique_pads)
        col2.metric("Avg Data Completeness", f"{avg_completeness:.1f}%")
        col3.metric("XML Received", f"{xml_received_pct:.1f}%")
        col3.metric("ASR Calculated", f"{asr_calculated_pct:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

        # Charts
        st.subheader("Job Distribution by Operation Type")
        job_distribution = filtered_df["operation"].value_counts()
        fig_distribution = px.pie(values=job_distribution.values, names=job_distribution.index, title="Job Distribution by Operation Type")
        st.plotly_chart(fig_distribution, use_container_width=True)

        st.subheader("Data Completeness by Operation")
        fig_completeness = px.box(filtered_df, x="operation", y="data_completeness",
                                  title="Data Completeness by Operation",
                                  labels={"operation": "Operation", "data_completeness": "Data Completeness (%)"})
        st.plotly_chart(fig_completeness, use_container_width=True)

with tab3:
    st.header("Grafana Alerts")

    grafana_url = os.getenv("GRAFANA_URL")
    grafana_api_key = os.getenv("GRAFANA_API_KEY")

    if grafana_url and grafana_api_key:
        alerts = fetch_grafana_alerts(grafana_url, grafana_api_key)
        if alerts:
            for alert in alerts:
                alert_color = "red" if alert["state"] == "alerting" else "green"
                st.markdown(f"<div style='padding: 10px; background-color: {alert_color}; color: white; border-radius: 5px; margin-bottom: 10px;'>"
                            f"<strong>{alert['name']}</strong>: {alert['message']}</div>", 
                            unsafe_allow_html=True)
        else:
            st.info("No alerts found or unable to fetch alerts.")
    else:
        st.warning("Grafana URL or API key not configured. Please check your .env file.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Data QC Tracker v1.0")