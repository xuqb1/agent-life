"""
Profile Engine: generate user side-write | 侧写引擎
"""
import json, re
from typing import List, Dict
from memory_store import load_index
from agent import Agent  # 复用 LLM 做二次摘要

agent = Agent()  # 单例复用


def _llm_summary(text: str, prompt: str) -> str:
    """Call local llm for summary | 本地模型摘要"""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text}
    ]
    return agent._prompt(messages, max_tokens=256, temp=0.3)


def build_profile(username: str) -> Dict:
    """Build/refresh profile when turns >= 3 | 轮次>=3时刷新侧写"""
    summaries = load_index(username)
    if not summaries:
        return {}
    corpus = "\n".join(summaries)
    # 1. 主题 & 实体 | topics & entities
    prompt1 = (
        "Extract the user's main topics, interests (food, color, hobby), birthday if mentioned, "
        "and people they care about. Return JSON only: "
        '{"topics":[], "food":[], "color":[], "birthday":"", "people":[]}'
    )
    json_str = _llm_summary(corpus, prompt1)
    try:
        info = json.loads(re.search(r'\{.*\}', json_str, flags=re.S).group(0))
    except Exception:
        info = {"topics": [], "food": [], "color": [], "birthday": "", "people": []}

    # 2. 情绪倾向 | emotion tendency
    prompt2 = "Give overall emotion tendency: positive/neutral/negative, reply one word only."
    emotion = _llm_summary(corpus, prompt2).strip().lower()

    # 3. 关心的人的简介（递归摘要）| brief for cared people
    people_detail = {}
    for name in info.get("people", [])[:3]:  # max 3
        lines = [l for l in summaries if name in l]
        if lines:
            prompt3 = f"Summarize {name} in one sentence."
            people_detail[name] = _llm_summary("\n".join(lines), prompt3)

    profile = {
        "username": username,
        "emotion_tendency": emotion,
        "topics": info.get("topics", []),
        "food": info.get("food", []),
        "color": info.get("color", []),
        "birthday": info.get("birthday", ""),
        "people_cared": people_detail,
        "last_update": datetime.datetime.now().isoformat(timespec="minutes")
    }
    return profile
