"""
FastAPI HTTP Server for Agent-Life | 接口服务
POST /chat  {"message": "hi"}
"""
from fastapi import FastAPI, Header
from pydantic import BaseModel
from agent import Agent
from knowledge import Knowledge

from memory_store import store_session, load_profile, save_profile
from profile_engine import build_profile
import datetime

app = FastAPI(title="Agent-Life API", version="1.0.0")

agent = Agent()  # 全局单例 | singleton


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str

chat_turns: Dict[str, int] = {}  # 内存轮次计数 | turn counter

def _gen_summary_and_emotion(messages: List[Dict]) -> (str, str):
    """Generate summary & emotion via LLM | 生成摘要与情绪"""
    corpus = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-6:]])
    prompt = "Summarize above chat in 20 Chinese words, then give emotion: positive/neutral/negative. Format: summary | emotion"
    res = agent._prompt([{"role": "user", "content": prompt}], max_tokens=80, temp=0.3)
    try:
        summary, emotion = res.split("|", 1)
    except Exception:
        summary, emotion = "聊天摘要", "neutral"
    return summary.strip(), emotion.strip()
    
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, user_email: str = Header(default="")):
    global chat_turns
    # 挂载侧写
    agent.current_profile = load_profile(username)
    # 1. 正常回复
    reply = agent.chat(req.message)
    master_flag = is_master(user_email)
    # 2. 摘要 & 存储
    username = user_email.split("@")[0] or "guest"
    chat_turns[username] = chat_turns.get(username, 0) + 1
    summary, emotion = _gen_summary_and_emotion(agent.history[-2:])  # 最新一轮
    store_session(username, agent.history[-2:], summary, emotion)
    # 3. 侧写触发
    if chat_turns[username] >= 3 and chat_turns[username] % 3 == 0:
        profile = build_profile(username)
        save_profile(username, profile)
    return ChatResponse(reply=reply, is_master=master_flag)


@app.get("/facts")
def get_facts():
    """Return static facts | 获取静态事实"""
    kb = Knowledge()
    return kb.static_facts()


@app.post("/remember")
def remember(payload: dict):
    """Dynamic remember | 动态记忆"""
    kb = Knowledge()
    for k, v in payload.items():
        kb.remember(k, v)
    return {"status": "saved"}


# 健康检查 | health check
@app.get("/health")
def health():
    return {"status": "ok"}

# 新增 response model
class ChatResponse(BaseModel):
    reply: str
    is_master: bool = False

# 依赖：从 Header 取邮箱（简化 demo，生产请用 JWT）
from fastapi import Header
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, user_email: str = Header(default="")):
    reply = agent.chat(req.message)
    master_flag = is_master(user_email)
    return ChatResponse(reply=reply, is_master=master_flag)

# 额外：管理员接口
@app.post("/admin/dna")
def update_dna(payload: dict, user_email: str = Header(default="")):
    if not is_master(user_email):
        return {"error": "Permission denied"}
    dna = AgentDNA.load()
    for k, v in payload.items():
        if hasattr(dna, k):
            setattr(dna, k, v)
    dna.save()
    return {"status": "dna updated"}
