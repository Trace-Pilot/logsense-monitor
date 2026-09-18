try:
    from importlib import import_module

    st = import_module("streamlit")
except ModuleNotFoundError as error:
    raise RuntimeError(
        "Streamlit is required to run this dashboard. Install it with: pip install streamlit"
    ) from error
from db import clause, logs, options, query

st.set_page_config(page_title="LogSense Monitor", page_icon="📊", layout="wide")
st.title("LogSense Monitor")
st.caption("Live PostgreSQL log overview")

try:
    choices = options()
except Exception as error:
    st.error("PostgreSQL connection failed. Configure LOGSENSE_DB_PASSWORD, then try again.")
    st.exception(error)
    st.stop()

with st.sidebar:
    st.header("Filters")
    apps = st.multiselect("Applications", choices["apps"], choices["apps"])
    severities = st.multiselect("Severities", choices["severities"], choices["severities"])

where, params = clause(apps, severities)
metrics = query("SELECT COUNT(*) total, COUNT(*) FILTER (WHERE severity = 'ERROR') errors, COUNT(*) FILTER (WHERE severity = 'CRITICAL') critical, COUNT(DISTINCT application) applications FROM logs" + where, params).iloc[0]
a, b, c, d = st.columns(4)
a.metric("Total logs", int(metrics.total))
b.metric("Errors", int(metrics.errors))
c.metric("Critical", int(metrics.critical))
d.metric("Applications", int(metrics.applications))

left, right = st.columns(2)
with left:
    st.subheader("Severity distribution")
    data = query("SELECT severity, COUNT(*) logs FROM logs" + where + " GROUP BY severity ORDER BY logs DESC", params)
    st.bar_chart(data.set_index("severity"), color="#4F46E5")
with right:
    st.subheader("Top applications")
    data = query("SELECT application, COUNT(*) logs FROM logs" + where + " GROUP BY application ORDER BY logs DESC LIMIT 10", params)
    st.bar_chart(data.set_index("application"), color="#06B6D4")

st.subheader("Logs over time")
trend = query("SELECT date_trunc('minute', timestamp) log_time, COUNT(*) logs FROM logs" + where + " GROUP BY log_time ORDER BY log_time", params)
st.line_chart(trend.set_index("log_time"), color="#8B5CF6")
st.subheader("Recent logs")
st.dataframe(logs(apps, severities, limit=10), use_container_width=True, hide_index=True)

