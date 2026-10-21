"""Local Streamlit dashboard for FB-OSINT Investigator Pro."""
import streamlit as st
from fbosint.storage import Store
from fbosint.reports import export_case

st.set_page_config(page_title="FB-OSINT Investigator Pro", page_icon="🔎", layout="wide")
st.title("🔎 FB-OSINT Investigator Pro")
st.caption("Coded by mr sabaz ali khan")
st.warning("Authorized, public-source case management only. This app does not scrape Facebook or access private data.")
store = Store()
with st.sidebar:
    st.header("Create case")
    with st.form("create_case", clear_on_submit=True):
        title = st.text_input("Case title")
        owner = st.text_input("Analyst / authorized owner")
        create = st.form_submit_button("Create case")
    if create:
        try:
            new_id = store.create_case(title, owner)
            st.success(f"Created case #{new_id}")
        except ValueError as e: st.error(str(e))

cases = store.list_cases()
if not cases:
    st.info("No cases yet. Create one in the sidebar or use the CLI.")
    st.stop()
options = {f"#{c['id']} — {c['title']}": c["id"] for c in cases}
selected = st.selectbox("Select case", list(options))
case_id = options[selected]
case = store.get_case(case_id)
left, right = st.columns(2)
with left:
    st.subheader("Record a public Facebook URL")
    with st.form("add_url", clear_on_submit=True):
        url = st.text_input("HTTPS Facebook URL", placeholder="https://www.facebook.com/publicpage")
        label = st.text_input("Label", value="Public URL")
        submit_url = st.form_submit_button("Add URL")
    if submit_url:
        try:
            store.add_url(case_id, url, label); st.success("URL recorded."); st.rerun()
        except ValueError as e: st.error(str(e))
    st.subheader("Add investigation note")
    with st.form("add_note", clear_on_submit=True):
        note = st.text_area("Note (avoid unnecessary personal data)")
        submit_note = st.form_submit_button("Save note")
    if submit_note:
        try:
            store.add_note(case_id, note); st.success("Note saved."); st.rerun()
        except ValueError as e: st.error(str(e))
with right:
    st.subheader("Hash local evidence file")
    st.caption("Only metadata and hash are stored; file contents are not uploaded or copied.")
    with st.form("add_evidence", clear_on_submit=True):
        path = st.text_input("Local file path")
        description = st.text_input("Evidence description")
        submit_ev = st.form_submit_button("Hash and record")
    if submit_ev:
        try:
            store.add_evidence(case_id, path, description); st.success("Evidence metadata recorded."); st.rerun()
        except (ValueError, FileNotFoundError, OSError) as e: st.error(str(e))

case = store.get_case(case_id)
st.divider()
st.subheader(f"Case #{case['id']}: {case['title']}")
st.caption(f"Owner: {case['owner']} · Created: {case['created_at']}")
c1,c2,c3 = st.columns(3)
c1.metric("Public URLs", len(case["urls"])); c2.metric("Notes", len(case["notes"])); c3.metric("Evidence records", len(case["evidence"]))
for section, title in [("urls","Public URLs"),("notes","Notes"),("evidence","Evidence metadata")]:
    with st.expander(title, expanded=True):
        st.dataframe(case[section], use_container_width=True, hide_index=True)
st.subheader("Export report")
col1, col2 = st.columns(2)
for col, fmt in [(col1,"json"),(col2,"csv")]:
    with col:
        try:
            report_path = export_case(case, fmt)
            st.download_button(f"Download {fmt.upper()} report", report_path.read_bytes(),
                               file_name=report_path.name, mime="application/json" if fmt=="json" else "text/csv")
        except OSError as e: st.error(str(e))
