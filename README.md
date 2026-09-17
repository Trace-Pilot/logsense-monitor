# LogSense Monitor

LogSense Monitor is a Python-based log monitoring project that imports structured application logs into PostgreSQL and visualizes them through a Streamlit dashboard.

## Features

- Imports structured log files into PostgreSQL
- Masks Aadhaar and PAN values before storing logs
- Tracks log severity, application name, timestamp, source file, and line number
- Dashboard with log statistics and charts
- Search logs by date, severity, application, and keyword
- Export filtered logs as CSV
- Configure alert rules in the dashboard

## Project structure

```text
LogSense Project/
├── LogAgent/
│   ├── agent.py
│   └── Logs/
├── DashBoard/
│   └── LogSense-Dashboard/
│       ├── app.py
│       ├── db.py
│       ├── requirements.txt
│       └── pages/
├── .gitignore
└── Project_Workflow.docx
```

## Log format

Log files must use this format:

```text
timestamp|severity|application|message
```

Example:

```text
2026-09-01 17:00:10|INFO|CustomerService|Customer Aadhaar 123456789012 verified successfully
```

## Prerequisites

- Python 3
- PostgreSQL
- A PostgreSQL database named `postgres`

## Configure the database password

Never store the database password in source code.

Set it in PowerShell before running the log agent or dashboard:

```powershell
$env:LOGSENSE_DB_PASSWORD = "your-postgres-password"
```

## Run the log agent

Place log files in:

```text
LogAgent/Logs/
```

Then run:

```powershell
cd LogAgent
python -m pip install psycopg2-binary
python agent.py
```

The agent creates the `logs` table if it does not exist and imports valid log records.

## Run the dashboard

```powershell
cd DashBoard/LogSense-Dashboard
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Security

- Do not commit PostgreSQL passwords.
- Do not upload `.env`, `.venv`, log files, or Streamlit secret files.
- Store database credentials only in environment variables or local secret files.
- Change passwords immediately if they are exposed.

## Team setup

Each developer should use their own local PostgreSQL password and set:

```powershell
$env:LOGSENSE_DB_PASSWORD = "their-own-password"
```

No database password needs to be shared through GitHub.

## Organization

Developed under the Trace-Pilot organization.
