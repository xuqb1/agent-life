"""Auth utilities | 登录校验工具"""
from knowledge import Knowledge

def is_master(email: str) -> bool:
    """Check if email matches master_email in KB | 邮箱是否为主人"""
    kb = Knowledge()
    return email.lower() == kb.get("master_email", "").lower()
