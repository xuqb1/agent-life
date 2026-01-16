"""
Memory Store: compress & index chat per user | 按用户压缩并索引会话
"""
import json, pathlib, zipfile, datetime, hashlib
from typing import List, Dict, Optional
from knowledge import Knowledge

USERS_ROOT = pathlib.Path("data/users")


def _user_dir(username: str) -> pathlib.Path:
    d = USERS_ROOT / username
    d.mkdir(parents=True, exist_ok=True)
    return d


def store_session(username: str, messages: List[Dict[str, str]], summary: str, emotion: str):
    """Store compressed chat + update index | 存压缩包并更新索引"""
    user_dir = _user_dir(username)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    # 1. 压缩原文 | compress original
    zip_path = user_dir / f"{ts}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("chat.json", json.dumps(messages, ensure_ascii=False, indent=2))
    # 2. 追加索引行 | append index
    index_file = user_dir / "index.txt"
    with index_file.open("a", encoding="utf8") as f:
        f.write(f"{ts} | {emotion} | {summary}\n")


def load_index(username: str, days: int = 30) -> List[str]:
    """Load recent summaries | 读取近 N 天摘要"""
    index_file = _user_dir(username) / "index.txt"
    if not index_file.exists():
        return []
    lines = index_file.read_text(encoding="utf8").splitlines()
    # 简单倒序取最近 200 条 | last 200 entries
    return lines[-200:]


def save_profile(username: str, profile: Dict):
    """Save side-write profile | 保存侧写"""
    _user_dir(username).joinpath("profile.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf8"
    )


def load_profile(username: str) -> Dict:
    """Load profile if exists | 读取侧写"""
    pro_file = _user_dir(username) / "profile.json"
    if not pro_file.exists():
        return {}
    return json.loads(pro_file.read_text(encoding="utf8"))
