# Agent-Life 🧬🤖  养成型本地智能人

[中文说明](README_zh.md)

## Overview
Agent-Life is a **local & private** raise-your-AI project.  
Give your AI a **DNA** (personality + capabilities) and a **knowledge base** (name, gender, age, master, any key-value).  
It loads automatically on every run, remembers forever, and grows through self-review.

## Features
- 🧬 18-dimension DNA (selfishness, humor, logic, leadership, self-reflection …)  
- 🧠 Persistent knowledge: static facts + dynamic `remember(key, value)`  
- 🔄 Self-review after each chat: chance = self_reflection/10, may increase weak skills  
- 🏠 100% offline: based on llama-cpp-python, any GGUF model  
- 🪶 Single-file CLI, <300 lines core code, easy to hack

## Quick Start
1. Clone & enter repo
   ```bash
   git clone https://github.com/yourname/agent-life.git
   cd agent-life
   ```

## download model
   ```bash
   wget https://huggingface.co/lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf \
     -O models/llama-3-8b-q4_k_m.gguf
   ```
## Install dependence
   ```bash
   pip install -r requirements.txt
   ```
## Run
   Cli
   ```bash
   python -m src.cli
   ```
   Teach your agent in natural language or use shortcuts:
   ```
      !name 小星
      !gender 女
      !age 18
      !master 张三
      !remember 喜欢的颜色 紫色
    ```
    Then chat normally.
    Type  exit  to quit; all memories and DNA growth are automatically saved to  data/ .
   Web
   ```bash
   streamlit run src/app.py
   ```
   web browser use: http://localhost:8501

## HTTP server
   ```bash
   uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
   ```
   document: http://localhost:8000/docs

## invoke example
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"who am I"}'
    ```

## start script
# 1. server end
   ```bash
   uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
   ```
# 2. client end (new open)
   ```bash
   streamlit run src/client.py --server.port 8501
   ```
# 3. admin end (new open)
   ```bash
   streamlit run src/admin.py --server.port 8502
   ```
