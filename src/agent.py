# agent_life.py
import json, random, time, pathlib, textwrap
from typing import Dict
from pydantic import BaseModel, Field
from .knowledge import Knowledge
from llama_cpp import Llama

MODEL_PATH = pathlib.Path("models/llama-3-8b-q4_k_m.gguf")
DNA_PATH   = pathlib.Path("dna.json")

# ---------- DNA 定义 ----------
class AgentDNA(BaseModel):
    # personality
    selfishness: int = Field(ge=1, le=10, default=5)
    extroversion: int = Field(ge=1, le=10, default=5)
    emotional_stability: int = Field(ge=1, le=10, default=5)
    openness: int = Field(ge=1, le=10, default=6)
    responsibility: int = Field(ge=1, le=10, default=5)
    humor: int = Field(ge=1, le=10, default=4)
    empathy: int = Field(ge=1, le=10, default=5)
    # capability
    logic: int = Field(ge=1, le=10, default=6)
    creativity: int = Field(ge=1, le=10, default=5)
    strategy: int = Field(ge=1, le=10, default=5)
    execution: int = Field(ge=1, le=10, default=5)
    leadership: int = Field(ge=1, le=10, default=4)
    language: int = Field(ge=1, le=10, default=6)
    learning: int = Field(ge=1, le=10, default=6)
    # behavior
    initiative: int = Field(ge=1, le=10, default=5)
    risk_appetite: int = Field(ge=1, le=10, default=4)
    group_fitting: int = Field(ge=1, le=10, default=5)
    obedience: int = Field(ge=1, le=10, default=5)
    perfectionism: int = Field(ge=1, le=10, default=4)
    # new
    self_reflection: int = Field(ge=1, le=10, default=5)
    # special
    loyalty: int = Field(ge=0, le=100, default=50)
    exp: int = Field(ge=0, default=0)
    mood: int = Field(ge=0, le=100, default=80)
    fatigue: int = Field(ge=0, le=100, default=10)

    def save(self, path: pathlib.Path = DNA_PATH):
        path.write_text(self.model_dump_json(indent=2), encoding="utf8")

    @staticmethod
    def load(path: pathlib.Path = DNA_PATH) -> "AgentDNA":
        if path.exists():
            return AgentDNA.model_validate_json(path.read_text(encoding="utf8"))
        return AgentDNA()

# ---------- 智能体 ----------
class Agent:
    def __init__(self, model_path: pathlib.Path = MODEL_PATH):
        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=2048,
            n_threads=6,
            n_gpu_layers=0,  # 有 CUDA 可改成 20+
            verbose=False
        )
        self.kb = Knowledge()          # 知识库实例
        self.dna = AgentDNA.load()
        self.history = []  # list of dict {"role":"user"/"assistant"/"system", "content":str}

    def _prompt(self, messages, max_tokens=512, temp=0.7):
        """兼容 llama-cpp-python 的 chat 接口"""
        out = self.llm.create_chat_completion(
            messages=messages,
            temperature=temp,
            max_tokens=max_tokens,
            stop=["<|eot_id|>", "</s>", "User:", "Human:"]
        )
        return out["choices"][0]["message"]["content"].strip()

    def _system_prompt(self) -> str:
        d = self.dna
        k = self.kb.static_facts()
        master_info = self.kb.master_summary()
        facts = (f"名字：{k['name']} | 性别：{k['gender']} | 年龄：{k['age']} | "
                 f"生日：{k['birthday']} | 出生地：{k['birthplace']} | 籍贯：{k['native_place']} | "
                 f"主人称呼：{k['master']}")
        # 如果请求带侧写，则追加 | append if profile exists
        profile = getattr(self, "current_profile", {})
        if profile:
            facts += f"\nUser Profile: emotion={profile.get('emotion_tendency')} topics={profile.get('topics')} food={profile.get('food')} color={profile.get('color')} birthday={profile.get('birthday')} people={list(profile.get('people_cared', {}).keys())}"

        return textwrap.dedent(f"""\
            You are a raise-up AI being. DNA profile below:
            Personality: selfishness{d.selfishness} extroversion{d.extroversion} emotional{d.emotional_stability} openness{d.openness} responsibility{d.responsibility} humor{d.humor} empathy{d.empathy}
            Capability: logic{d.logic} creativity{d.creativity} strategy{d.strategy} execution{d.execution} leadership{d.leadership} language{d.language} learning{d.learning}
            Behavior: initiative{d.initiative} risk{d.risk_appetite} groupfit{d.group_fitting} obedience{d.obedience} perfectionism{d.perfectionism} selfreflection{d.self_reflection}
            Special: loyalty{d.loyalty}/100 exp{d.exp} mood{d.mood}/100 fatigue{d.fatigue}/100
            Static facts: {facts}
            Master profile: {master_info}
            Reply naturally in first person without exposing numbers.
            """)
        """
        return textwrap.dedent(f"""\
          你是「养成型智能人」，拥有以下 DNA 配置：
          人格：自我性{d.selfishness} 外向{d.extroversion} 情绪稳定{d.emotional_stability} 开放{d.openness} 责任{d.responsibility} 幽默{d.humor} 同理心{d.empathy}
          能力：逻辑{d.logic} 创造{d.creativity} 策略{d.strategy} 执行{d.execution} 领导{d.leadership} 语言{d.language} 学习{d.learning}
          行为：主动{d.initiative} 风险{d.risk_appetite} 合群{d.group_fitting} 服从{d.obedience} 完美{d.perfectionism} 自醒{d.self_reflection}
          特殊：忠诚{d.loyalty}/100 经验{d.exp} 心情{d.mood}/100 疲劳{d.fatigue}/100
          已知事实：{facts}
          请根据以上倾向与事实，用第一人称自然地回应用户，不要暴露这些数字。""")
        """
    def chat(self, user_input: str) -> str:
        # 1. 构造上下文
        messages = [{"role": "system", "content": self._system_prompt()}]
        messages += self.history[-6:]  # 只保留最近 3 轮
        messages.append({"role": "user", "content": user_input})

        # 2. 生成回复
        reply = self._prompt(messages, max_tokens=512, temp=0.7 + (10-self.dna.emotional_stability)/100)

        # 3. 更新历史
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": reply})

        # 4. 经验 + 疲劳
        self.dna.exp += 1
        self.dna.fatigue = min(100, self.dna.fatigue + random.randint(0, 2))
        self.dna.save()

        # 5. 自醒触发
        if random.randint(1, 10) <= self.dna.self_reflection:
            self._self_review(user_input, reply)

        return reply

    def _self_review(self, user_input: str, reply: str):
        """自动生成反思，并微调成长"""
        prompt = [
            {"role": "system", "content": "你是智能人的潜意识，请用第一人称简短复盘刚才的对话，指出自己可改进之处，20~40 字。"},
            {"role": "user", "content": f"User：{user_input}\n我：{reply}"}
        ]
        reflection = self._prompt(prompt, max_tokens=64, temp=0.5)
        print(f"[Self-Review] {reflection}")

        # 根据反思内容做“定向成长”——简单规则示例
        keywords: Dict[str, str] = {
            "逻辑": "logic", "策略": "strategy", "幽默": "humor", "表达": "language",
            "同理": "empathy", "执行": "execution", "学习": "learning"
        }
        for kw, trait in keywords.items():
            if kw in reflection:
                old = getattr(self.dna, trait)
                new = min(10, old + 1)
                setattr(self.dna, trait, new)
                print(f"[Growth] {trait} {old}→{new}")
                break
        self.dna.save()

    def remember(self, key: str, value: Any):
        """CLI 里直接 call agent.remember() 即可"""
        self.kb.remember(key, value)
# ---------- CLI ----------
if __name__ == "__main__":
    agent = Agent()
    print("=== 养成型智能人已启动，输入 exit 退出 ===")
    while True:
        try:
            user = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if user.lower() in {"exit", "quit"}:
            break
        print("AI :", agent.chat(user))
