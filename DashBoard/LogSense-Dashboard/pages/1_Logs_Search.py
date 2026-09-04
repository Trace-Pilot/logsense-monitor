import streamlit as st
from db import logs, options

st.set_page_config(page_title="Logs / Search", page_icon="🔎", layout="wide")
st.title("Logs / Search")
choices = options()
with st.form("filters"):
    one, two, three = st.columns(3)
    dates = one.date_input("Date range", value=())
    severity = two.multiselect("Severity", choices["severities"])
    apps = three.multiselect("Application", choices["apps"])
    keyword = st.text_input("Search message")
    run = st.form_submit_button("Search", type="primary")
if run or "first_search" not in st.session_state:
    st.session_state.first_search = True
    start = end = None
    if isinstance(dates, tuple) and len(dates) == 2: start, end = dates
    result = logs(apps, severity, start, end, keyword)
    st.caption("Showing " + str(len(result)) + " result(s), maximum 1,000.")
    st.dataframe(result, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", result.to_csv(index=False).encode(), "logs_export.csv", "text/csv")

