"""Client Streamlit | 客户端（主人/普通用户双身份）"""
import streamlit as st, requests
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Agent-Life Client", layout="wide")
st.title("🤖 Agent-Life Client")

# -------------- 登录区 | Login --------------
if "email" not in st.session_state:
    st.session_state.email = ""
if "is_master" not in st.session_state:
    st.session_state.is_master = False

with st.sidebar:
    email = st.text_input("Email（唯一身份）", value=st.session_state.email)
    if st.button("Login"):
        st.session_state.email = email
        # 用空消息试探身份
        res = requests.post(API_URL+"/chat", json={"message": "hi"},
                            headers={"user-email": email}).json()
        st.session_state.is_master = res.get("is_master", False)
        st.success(f"Logged in! Master={st.session_state.is_master}")
# 登录后加载侧写
if st.session_state.email:
    profile = requests.get(f"{API_URL}/profile", headers={"user-email": st.session_state.email}).json()
    if profile:
        st.sidebar.json(profile)  # 可选展示
        # 把侧写注入 system prompt（通过额外 header 告诉服务端）
        st.session_state.profile = profile

if not st.session_state.email:
    st.stop()

# -------------- 聊天 | Chat --------------
if "msgs" not in st.session_state:
    st.session_state.msgs = []

for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])

prompt = st.chat_input("Talk to AI")
if prompt:
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    res = requests.post(API_URL+"/chat", json={"message": prompt},
                        headers={"user-email": st.session_state.email}).json()
    reply = res["reply"]
    st.session_state.msgs.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"): st.markdown(reply)
