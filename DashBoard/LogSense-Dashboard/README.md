# LogSense Dashboard

This dashboard is built for the actual table created by your importer: logs(timestamp, severity, application, message, source_file, line_number).

## Run

Copy all files into C:\Documents\LogSense Project\DashBoard, then run:

    pip install -r requirements.txt
    $env:LOGSENSE_DB_PASSWORD = "your-postgres-password"
    streamlit run app.py

Open the local link Streamlit displays, usually http://localhost:8501.

