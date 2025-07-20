# ☁️ Void: The Cloud Intelligence Structure

**Void** is a Python-based backend platform designed to operate as a cloud-resident intelligence system. It is not an AGI brain emulator but rather a *repository of intelligent capability*—a modular structure built for dynamic routing of queries, tool use, and intelligent function through cloud-deployed language models and services.

Void serves as the centralized router and executor of intelligent behavior. It operates via FastAPI and is built to support modular intelligent functions, including inference, routing, external API use, memory management, and tool invocation. It is model-agnostic, fine-tune–ready, and structured for extension.

* * *

## ✨ Overview

Void is a cloud intelligence node with the following goals:

- Provide structured access to LLMs and intelligence tools.
    
- Route tasks to the appropriate handlers or model agents.
    
- Act as a foundation for a network of cloud-resident intelligent processes.
    
- Serve as an evolving intelligence backend for custom frontend clients.
    

It integrates principles from AGI system design—modular decomposition, memory layering, tool usage, and multi-agent interfacing—without claiming AGI itself.

* * *

## ⚙️ Core Features

- 🧠 **Intelligent routing layer** for structured prompt handling and role/task management
    
- 🌐 **FastAPI backend** with full CORS support for cross-origin deployment
    
- 📡 **External model integration** (e.g., Together AI, OpenAI, local models)
    
- 💾 **Lightweight memory tracking** (non-persistent or plugin-extensible)
    
- 🧰 **Tool invocation modules** (coming soon: code, search, math, etc.)
    
- 📊 **Token usage tracking** via `token_log.jsonl`
    
- 🔐 **Environment-based API key management**
    

* * *

## 📦 Requirements

Create a virtual environment:

bash

CopyEdit

`python -m venv .venvsource .venv/bin/activate # or .venv\Scripts\Activate.ps1 on Windows`

Install dependencies:

bash

CopyEdit

`pip install -r requirements.txt`

Create a `.env` file:

ini

CopyEdit

`TOGETHER_API_KEY=your_together_api_key`

* * *

## 🚀 Local Development

Start the server locally:

bash

CopyEdit

`uvicorn main:app --reload`

Test an endpoint:

json

CopyEdit

`POST /chat{ "prompt": "What is the Void?", "max_tokens": 1000}`

* * *

## 🧪 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/chat` | Routes prompt through the intelligent core |
| GET | `/usage-stats` | Returns total token usage |
| GET | `/daily-tokens` | Returns today's token usage |
| POST | `/reset-memory` | Clears current conversation memory |
| GET | `/okcheck` | Health check endpoint |

* * *

## 🧾 Token Logging

Token usage is logged in `token_log.jsonl` as newline-delimited JSON:

json

CopyEdit

`{ "timestamp": "2025-07-20T00:00:00Z", "prompt_tokens": 120, "completion_tokens": 100, "total_tokens": 220}`

* * *

## ☁️ Deployment (Render Example)

Include the following files:

- `main.py`
    
- `requirements.txt`
    
- `start.sh`
    

### Example `start.sh`:

bash

CopyEdit

`#!/usr/bin/env bashgunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app`

### Render Setup:

- Push project to GitHub
    
- Go to Render → New → Web Service
    
- Set environment: Python
    
- Build command: *(leave blank)*
    
- Start command: `./start.sh`
    
- Add `.env` values manually
    

* * *

## 🔒 Security Notes

- API key is stored securely in `.env`
    
- CORS is restricted to authorized origins
    
- Development use is local-only by default
    
- Planned: JWT auth, route protection, memory persistence
    

* * *

## 👨‍💻 Author

**Dillon Carey**  
Director of Personal AI Systems  
https://dilloncarey.com

* * *

Let me know if you'd like to add sections for submodules, future roadmap, memory persistence, multi-agent planning, or frontend integration.

Ask ChatGPT
