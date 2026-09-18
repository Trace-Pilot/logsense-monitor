import os
import importlib
import psycopg2

# Load pandas dynamically so static analysis does not require its source package.
pd = importlib.import_module("pandas")

try:
    cache_resource = importlib.import_module("streamlit").cache_resource
except ImportError:
    from functools import lru_cache

    def cache_resource(**_kwargs):
        def decorator(function):
            # Provide the same resource-reuse behavior when Streamlit is absent.
            return lru_cache(maxsize=1)(function)
        return decorator

@cache_resource(show_spinner=False)
def connection():
    return psycopg2.connect(
        host=os.getenv("LOGSENSE_DB_HOST", "localhost"),
        port=int(os.getenv("LOGSENSE_DB_PORT", "5432")),
        dbname=os.getenv("LOGSENSE_DB_NAME", "postgres"),
        user=os.getenv("LOGSENSE_DB_USER", "postgres"),
        password=os.getenv("LOGSENSE_DB_PASSWORD", ""),
    )

def query(sql, params=None):
    return pd.read_sql_query(sql, connection(), params=params)

def options():
    return {
        "apps": query("SELECT DISTINCT application FROM logs ORDER BY application")["application"].tolist(),
        "severities": query("SELECT DISTINCT severity FROM logs ORDER BY severity")["severity"].tolist()
    }

def clause(apps=None, severities=None, start=None, end=None, keyword=None):
    conditions, params = [], []
    if apps: conditions.append("application = ANY(%s)"); params.append(apps)
    if severities: conditions.append("severity = ANY(%s)"); params.append(severities)
    if start: conditions.append("timestamp >= %s"); params.append(start)
    if end: conditions.append("timestamp < (%s::date + INTERVAL '1 day')"); params.append(end)
    if keyword: conditions.append("message ILIKE %s"); params.append("%" + keyword + "%")
    return (" WHERE " + " AND ".join(conditions) if conditions else ""), params

def logs(apps=None, severities=None, start=None, end=None, keyword=None, limit=1000):
    where, params = clause(apps, severities, start, end, keyword)
    params.append(limit)
    return query("SELECT timestamp, severity, application, message, source_file, line_number FROM logs" + where + " ORDER BY timestamp DESC LIMIT %s", params)

