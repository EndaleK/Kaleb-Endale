import streamlit as st
import pandas as pd
import plotly.express as px
from database import (
    init_connection, create_table, insert_data, fetch_data, 
    update_data, delete_data, rename_contractor_to_service_provider, reorder_columns
)
from utils import validate_data, generate_unique_id
from datetime import datetime
from pandas.api.types import is_bool_dtype

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
st.sidebar.title("Data QC Tracker")
st.sidebar.markdown("---")
st.sidebar.subheader("Job Management")
job_number = st.sidebar.text_input("Enter Job Number")
add_job_button = st.sidebar.button("Set Job Number")

if add_job_button and job_number:
    st.session_state.current_job_number = job_number

# Main content
st.title("Data QC Tracker")
st.markdown("---")

if 'current_job_number' in st.session_state:
    st.subheader(f"Current Job: {st.session_state.current_job_number}")

# Tabs
tab1, tab2 = st.tabs(["Data Input and View", "Analysis"])

with tab1:
    st.header("Data Input and View")
    st.markdown("---")
    
    # Input Data Section
    with st.expander("Input New Data", expanded=False):
        with st.form("data_input_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date")
                pad_name = st.text_input("Pad Name")
                well_name = st.text_input("Well Name")
                stage = st.number_input("Stage", min_value=1, step=1)
                job_type = st.selectbox("Job Type", ["Fracturing", "Wireline", "Pump Down"])
            
            with col2:
                operation = st.selectbox("Operation", ["Frac", "Wireline", "Pump Down", "Coiled Tubing", "Perforating", "Logging", "Well Testing", "Slickline"])
                service_provider = st.text_input("Service Provider")
                client = st.text_input("Client")
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
            
            comments = st.text_area("Comments")
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                xml_received = st.radio("XML Rec'd", ["Yes", "No"])
                full_timeblock = st.radio("Full Timeblock", ["Yes", "No"])
            
            with col4:
                asr_calculated = st.radio("ASR Calculated", ["Yes", "No"])
                sub_activities = st.radio("Sub Activities", ["Yes", "No"])
            
            with col5:
                data_completeness = st.slider("Data Completeness (%)", 0, 100, 50)
            
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
                "service_provider": service_provider,
                "client": client,
                "start_time": start_time,
                "end_time": end_time,
                "comments": comments,
                "operation": operation,
                "submitted_at": datetime.now(),
                "xml_received": xml_received == "Yes",
                "asr_calculated": asr_calculated == "Yes",
                "full_timeblock": full_timeblock == "Yes",
                "sub_activities": sub_activities == "Yes",
                "data_completeness": data_completeness,
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

    # View Data Section
    st.subheader("View Data")
    st.markdown("---")
    
    @st.cache_data(ttl=300)
    def load_data():
        data = fetch_data(conn)
        df = pd.DataFrame(data)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["duration"] = (pd.to_datetime(df["end_time"].astype(str)) - pd.to_datetime(df["start_time"].astype(str))).dt.total_seconds() / 3600
            
            # Ensure boolean columns are properly typed
            bool_columns = ['xml_received', 'asr_calculated', 'full_timeblock', 'sub_activities']
            for col in bool_columns:
                if col in df.columns:
                    df[col] = df[col].astype(bool)
        
        return df

    df = load_data()

    if df.empty:
        st.warning("No data available. Please add some data using the Input Data section above.")
    else:
        # Filtering options
        with st.expander("Filter Data", expanded=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                pad_filter = st.multiselect("Pad Name", options=df["pad_name"].unique())
                well_filter = st.multiselect("Well Name", options=df["well_name"].unique())
            
            with col2:
                date_range = st.date_input("Date Range", value=(df["date"].min().date(), df["date"].max().date()), key="date_range")
            
            with col3:
                operation_filter = st.multiselect("Operation", options=df["operation"].unique())
            
            with col4:
                xml_filter = st.multiselect("XML Rec'd", options=["Yes", "No"])
                asr_filter = st.multiselect("ASR Calculated", options=["Yes", "No"])
            
            with col5:
                job_numbers = ["All"] + sorted(df["job_number"].unique().tolist())
                job_number_filter = st.selectbox("Job Number", options=job_numbers)

        # Apply filters
        mask = pd.Series(True, index=df.index)
        if pad_filter:
            mask &= df["pad_name"].isin(pad_filter)
        if well_filter:
            mask &= df["well_name"].isin(well_filter)
        if date_range:
            mask &= (df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])
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
            # Convert boolean columns to 'Yes'/'No' strings
            bool_columns = ['xml_received', 'asr_calculated', 'full_timeblock', 'sub_activities']
            for col in bool_columns:
                if is_bool_dtype(filtered_df[col]):
                    filtered_df[col] = filtered_df[col].map({True: 'Yes', False: 'No'})

            # Define a function to color the cells
            def color_yes_no(val):
                if val == 'Yes':
                    return 'background-color: #C8E6C9; color: #1B5E20;'
                elif val == 'No':
                    return 'background-color: #FFCDD2; color: #B71C1C;'
                else:
                    return ''

            # Apply the styling
            styled_df = filtered_df.style.applymap(color_yes_no, subset=bool_columns)

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
    st.markdown("---")
    
    if df.empty:
        st.warning("No data available for analysis. Please add some data using the Input Data tab.")
    else:
        # Calculate KPIs
        total_jobs = len(filtered_df)
        avg_duration = filtered_df["duration"].mean() if "duration" in filtered_df.columns else 0
        unique_wells = filtered_df["well_name"].nunique()
        unique_pads = filtered_df["pad_name"].nunique()
        avg_completeness = filtered_df["data_completeness"].mean()
        
        # Convert 'xml_received' and 'asr_calculated' to boolean if they're not already
        filtered_df['xml_received'] = filtered_df['xml_received'].map({'Yes': True, 'No': False}) if filtered_df['xml_received'].dtype == 'object' else filtered_df['xml_received']
        filtered_df['asr_calculated'] = filtered_df['asr_calculated'].map({'Yes': True, 'No': False}) if filtered_df['asr_calculated'].dtype == 'object' else filtered_df['asr_calculated']
        
        xml_received_pct = (filtered_df["xml_received"].sum() / total_jobs) * 100 if total_jobs > 0 else 0
        asr_calculated_pct = (filtered_df["asr_calculated"].sum() / total_jobs) * 100 if total_jobs > 0 else 0

        # Display KPIs
        st.subheader("Key Performance Indicators")
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
            <div class="stMetric kpi-primary">
                <div class="label">Total Jobs</div>
                <div class="value">{total_jobs}</div>
            </div>
        """, unsafe_allow_html=True)

        col1.markdown(f"""
            <div class="stMetric kpi-info">
                <div class="label">Unique Wells</div>
                <div class="value">{unique_wells}</div>
            </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
            <div class="stMetric kpi-success">
                <div class="label">Average Job Duration</div>
                <div class="value">{avg_duration:.2f} hours</div>
            </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
            <div class="stMetric kpi-warning">
                <div class="label">Unique Pads</div>
                <div class="value">{unique_pads}</div>
            </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
            <div class="stMetric kpi-danger">
                <div class="label">Avg Data Completeness</div>
                <div class="value">{avg_completeness:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
            <div class="stMetric kpi-primary">
                <div class="label">XML Received</div>
                <div class="value">{xml_received_pct:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
            <div class="stMetric kpi-success">
                <div class="label">ASR Calculated</div>
                <div class="value">{asr_calculated_pct:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

        # Job Distribution by Operation Type
        st.subheader("Job Distribution by Operation Type")
        job_distribution = filtered_df["operation"].value_counts()
        fig_distribution = px.pie(
            values=job_distribution.values,
            names=job_distribution.index,
            title="Job Distribution by Operation Type",
            hole=0.3,  # Donut chart
        )
        fig_distribution.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_distribution, use_container_width=True)

        # Job Durations Over Time
        st.subheader("Job Durations Over Time")
        fig_duration = px.scatter(
            filtered_df,
            x="date",
            y="duration",
            color="operation",
            size="data_completeness",  # Adds another dimension
            hover_data=["id"],  # Shows job_id on hover (assuming 'id' is the job_id column)
            title="Job Durations Over Time",
            labels={
                "date": "Date",
                "duration": "Duration (hours)",
                "operation": "Operation",
                "data_completeness": "Data Completeness (%)"
            }
        )
        fig_duration.update_layout(legend_title_text='Operation')
        st.plotly_chart(fig_duration, use_container_width=True)

        # Data Completeness by Operation
        st.subheader("Data Completeness by Operation")
        fig_completeness = px.box(
            filtered_df,
            x="operation",
            y="data_completeness",
            color="operation",
            points="all",  # Shows all points
            title="Data Completeness by Operation",
            labels={
                "operation": "Operation",
                "data_completeness": "Data Completeness (%)"
            }
        )
        fig_completeness.update_layout(showlegend=False)  # Hide legend as it's redundant
        st.plotly_chart(fig_completeness, use_container_width=True)

        # New chart: Average Duration by Operation
        st.subheader("Average Duration by Operation")
        avg_duration = filtered_df.groupby("operation")["duration"].mean().reset_index()
        fig_avg_duration = px.bar(
            avg_duration,
            x="operation",
            y="duration",
            title="Average Duration by Operation",
            labels={
                "operation": "Operation",
                "duration": "Average Duration (hours)"
            }
        )
        st.plotly_chart(fig_avg_duration, use_container_width=True)

# Editing form (outside of tabs to maintain state)
if st.session_state.get("editing", False):
    st.subheader("Edit Data")
    with st.form("edit_form"):
        row = st.session_state.editing_row
        
        # (Include all form fields here, similar to the input form)
        
        update_button = st.form_submit_button("Update")
    
    if update_button:
        # (Include update logic here)
        pass

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Data QC Tracker v1.0")