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
