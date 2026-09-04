import os
import streamlit as st
from db import connection

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
st.title("Settings")
st.subheader("Database connection")
st.info("Keep the PostgreSQL password out of the source code. Set it as an environment variable before starting Streamlit.")
st.code('$env:LOGSENSE_DB_PASSWORD = "your-postgres-password"\nstreamlit run app.py', language="powershell")
st.write("Host: " + os.getenv("LOGSENSE_DB_HOST", "localhost") + " | Database: " + os.getenv("LOGSENSE_DB_NAME", "postgres"))
if st.button("Test database connection", type="primary"):
    try:
        connection().cursor().execute("SELECT 1")
        st.success("Database connection successful.")
    except Exception as error: st.error("Connection failed: " + str(error))
st.subheader("Log configuration")
st.write("This project uses: logs(timestamp, severity, application, message, source_file, line_number).")

