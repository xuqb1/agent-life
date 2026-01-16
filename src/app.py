"""
Streamlit Web UI for Agent-Life | 图形界面入口
Author: Agent-Life Team
"""
import streamlit as st
from agent import Agent  # 同级导入
from knowledge import Knowledge

st.set_page_config(page_title="Agent-Life", layout="wide")
st.title("🧬🤖 Agent-Life 养成型智能人")

# -------------- 侧边栏教学 | Sidebar Teaching --------------
with st.sidebar:
    st.header("Teach Your Agent")
    kb = Knowledge()  # 实例仅用于保存
    name = st.text_input("Name", value=kb.get("name"))
    gender = st.selectbox("Gender", ["unknown", "male", "female", "other"])
    age = st.number_input("Age", min_value=0, max_value=120, value=kb.get("age", 0))
    master_name = st.text_input("Master Name", value=kb.get("master_name"))
    master_gender = st.selectbox("Master Gender", ["unknown", "male", "female", "other"])
    master_age = st.number_input("Master Age", min_value=0, max_value=120, value=kb.get("master_age", 0))
    master_email = st.text_input("Master Email", value=kb.get("master_email"))
    master_idcard = st.text_input("Master ID Card", value=kb.get("master_idcard"), type="password")
    if st.button("Save Static Facts"):
        kb.remember("name", name)
        kb.remember("gender", gender)
        kb.remember("age", age)
        kb.remember("master_name", master_name)
        kb.remember("master_gender", master_gender)
        kb.remember("master_age", master_age)
        kb.remember("master_email", master_email)
        kb.remember("master_idcard", master_idcard)
        st.success("Saved! 已保存")

# -------------- 聊天界面 | Chat Area --------------
@st.cache_resource(show_spinner=False)  # 全局单例 | global singleton
def get_agent():
    return Agent()

agent = get_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 展示历史 | show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入 | user input
if prompt := st.chat_input("Talk to your AI"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""
        # 流式体验：一次性返回后填充
        full_reply = agent.chat(prompt)
        placeholder.markdown(full_reply)
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
