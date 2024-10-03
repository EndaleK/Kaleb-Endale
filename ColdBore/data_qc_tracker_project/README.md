# Data QC Tracker

This is a Streamlit application for tracking and visualizing Data QC information for fracturing, wireline, and pump down operations.

## Prerequisites

- Python 3.7+
- PostgreSQL database

## Setup

1. Clone this repository or download the project files.

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your PostgreSQL database and update the following environment variables with your database credentials:
   - PGHOST
   - PGDATABASE
   - PGUSER
   - PGPASSWORD
   - PGPORT

4. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

5. Open your web browser and go to `http://localhost:5000` to view the application.

## Files

- `main.py`: The main Streamlit application
- `database.py`: Database connection and operations
- `utils.py`: Utility functions
- `add_sample_data.py`: Script to add sample data to the database
- `styles.css`: Custom CSS styles for the application
- `.streamlit/config.toml`: Streamlit configuration file

## Usage

1. Use the sidebar to filter data by job number.
2. Add new data using the "Add New Data" form.
3. View and export recorded data.
4. Edit or delete existing data.
5. Explore the Summary Dashboard for insights and visualizations.

For any issues or questions, please contact Kaleb Endale.
