"""
 bilingual knowledge base for Agent-Life
 事实知识库：静态事实 + 动态 remember
"""
import json, pathlib
from typing import Any, Dict

FACTS_PATH = pathlib.Path("data/facts.json")

class Knowledge:
    """Thread-safe enough for single-user local CLI."""
    def __init__(self, path: pathlib.Path = FACTS_PATH):
        self.path = path
        self._facts: Dict[str, Any] = {}
        self.load()

    # ---- IO ----
    def load(self):
        if self.path.exists():
            self._facts = json.loads(self.path.read_text(encoding="utf8"))
        else:
            # 默认静态事实模板
            self._facts = {
                "name"        : "未命名",
                "gender"      : "unknown",
                "age"         : 0,
                "birthday"    : "2000-01-01",
                "birthplace"  : "unknown",
                "native_place": "unknown",
                "master"      : "unknown",
                "master_name"   : "",          # 真实姓名
                "master_gender" : "",          # 男 / 女 / 其他
                "master_age"    : 0,           # 当前年龄
                "master_email"  : "",          # 邮箱
                "master_idcard" : "",          # 身份证号
                "memo"        : {}   # 动态事实
            }
            self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._facts, ensure_ascii=False, indent=2), encoding="utf8")

    # ---- API ----
    def remember(self, key: str, value: Any, persistent: bool = True):
        """动态记住任意事实"""
        self._facts["memo"][key] = value
        if persistent:
            self.save()

    def get(self, key: str, default=None) -> Any:
        """先查静态，再查动态"""
        return self._facts.get(key) or self._facts["memo"].get(key) or default

    def static_facts(self) -> Dict[str, Any]:
        """供 system prompt 使用"""
        return {k: v for k, v in self._facts.items() if k != "memo"}

    def master_summary(self) -> str:
        """Desensitized master info | 脱敏主人信息"""
        name   = self._facts.get("master_name")   or "Unfilled"
        gender = self._facts.get("master_gender") or "Unfilled"
        age    = self._facts.get("master_age")    or "Unfilled"
        email  = self._facts.get("master_email")  or "Unfilled"
        idcard = self._facts.get("master_idcard") or "Unfilled"
        if idcard != "Unfilled" and len(idcard) > 8:
            idcard = idcard[:4] + "****" + idcard[-4:]  # 简单脱敏 | simple desensitization
        return f"Name:{name} | Gender:{gender} | Age:{age} | Email:{email} | ID:{idcard}"
