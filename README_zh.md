# Agent-Life 🧬🤖  养成型本地智能人

## 项目简介
Agent-Life 是一个**完全本地、完全私有**的“养成 AI 娃”引擎。  
你可以给它设定一段 DNA（人格、能力、行为倾向），再告诉它名字、性别、年龄、主人是谁等任何事实；  
下次启动自动加载，永远不忘，还能通过「自醒」不断成长。

## 特色
- 🧬 18 维 DNA：自我性、幽默、逻辑、领导力、自醒性……
- 🧠 持久化知识库：静态事实 + 动态 `remember(key, value)`
- 🔄 每次聊天后概率自醒，自动生成反思并提升短板
- 🏠 100% 离线：基于 llama-cpp-python，支持任意 GGUF 模型
- 🪶 单文件 CLI，核心代码 <300 行，方便二次开发

## 快速开始
1. 克隆仓库
   ```bash
   git clone https://github.com/yourname/agent-life.git
   cd agent-life

## 下载模型 示例
   ```bash
   wget https://huggingface.co/lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf \
     -O models/llama-3-8b-q4_k_m.gguf
## 安装依赖
   ```bash
   pip install -r requirements.txt

## 运行
   Cli
   ```bash
   python -m src.cli
   
   用自然语言或以下快捷方式设置你的智能人:
      !name 小星
      !gender 女
      !age 18
      !master 张三
      !remember 喜欢的颜色 紫色
    然后开始会话。
    输入  exit  回车退出; 所有记忆与DNA都是自动调整的，保存在 data/ .
   Web
   ```bash
   streamlit run src/app.py
   web 浏览器中: http://localhost:8501

## HTTP 服务
   ```bash
   uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
   文档: http://localhost:8000/docs

# 回调示例
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"who am I"}'

## 启动脚本
# 1. 服务端
   ```bash
   uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
# 2. 客户端(新开终端)
   ```bash
   streamlit run src/client.py --server.port 8501
# 3. 管理端(新开终端)
   ```bash
   streamlit run src/admin.py --server.port 8502
