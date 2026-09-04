import streamlit as st
from db import options

st.set_page_config(page_title="Alerts", page_icon="🚨", layout="wide")
st.title("Alert rules")
st.caption("Rules are kept for the current session. Add email, Slack, or Teams delivery once you choose a notification channel.")
if "rules" not in st.session_state: st.session_state.rules = []
choices = options()
with st.form("rule"):
    name = st.text_input("Rule name")
    severity = st.selectbox("Minimum severity", ["WARNING", "ERROR", "CRITICAL"])
    threshold = st.number_input("Events within 15 minutes", min_value=1, value=1)
    keyword = st.text_input("Message contains (optional)")
    apps = st.multiselect("Applications (optional)", choices["apps"])
    save = st.form_submit_button("Save rule", type="primary")
if save:
    if name.strip():
        st.session_state.rules.append({"Name": name, "Severity": severity, "Threshold": threshold, "Keyword": keyword or "Any", "Applications": ", ".join(apps) or "Any"})
        st.success("Rule saved.")
    else: st.warning("Enter a rule name.")
if st.session_state.rules: st.dataframe(st.session_state.rules, use_container_width=True, hide_index=True)
else: st.info("No alert rules configured.")

