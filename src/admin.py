"""Admin Streamlit | 管理端（DNA 在线调整）"""
import streamlit as st, requests
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Agent-Life Admin", layout="wide")
st.title("🔧 Agent-Life Admin")

email = st.text_input("Admin Email")
if st.button("Login"):
    res = requests.post(API_URL+"/chat", json={"message": "hi"},
                        headers={"user-email": email}).json()
    if not res.get("is_master", False):
        st.error("You are not the master!")
        st.stop()
    st.success("Welcome Master!")
    st.session_state.master = True

if st.session_state.get("master"):
    dna = requests.get(API_URL+"/facts").json()
    st.json(dna)
    with st.form("dna_form"):
        new_logic = st.slider("logic", 1, 10, dna.get("logic", 5))
        submitted = st.form_submit_button("Update DNA")
        if submitted:
            resp = requests.post(API_URL+"/admin/dna", json={"logic": new_logic},
                                 headers={"user-email": email}).json()
            st.write(resp)
