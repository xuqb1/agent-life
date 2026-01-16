import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from agent import Agent

USAGE = """\
快捷教学语法（一行）：
  !name 小星
  !gender 女
  !age 18
  !birthday 2006-03-16
  !birthplace 杭州
  !native 浙江绍兴
  !master 张三
  !remember 喜欢的颜色 紫色
  

正常对话直接输入即可，exit 退出。
"""

MASTER_SHORTCUTS = """
  !master_name    Wang Daming
  !master_gender  male
  !master_age     30
  !master_email   wang@example.com
  !master_idcard  110105199401011234
"""

agent = Agent()
print(USAGE)
while True:
    try:
        user = input("You: ").strip()
    except (KeyboardInterrupt, EOFError):
        break
    if user.lower() in {"exit", "quit"}:
        break
    # 快捷教学指令
    if user.startswith("!"):
        parts = user[1:].split(" ", 1)
        if len(parts) == 2:
            key, value = parts
            agent.remember(key, value)
            print(f"AI : 已记住 {key} = {value}")
        continue
    print("AI :", agent.chat(user))
