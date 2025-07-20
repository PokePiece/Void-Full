# 🧠 The Brain

AGI Brain App

This is the FastAPI backend for **the Brain**, an AGI Brain app powered by [Together AI](https://platform.together.ai/) using the LLaMA 3 70B model. It handles chat routing, returns model responses, tracks token usage, and supports minimal in-memory conversation context.

---

## ✨ About the AGI Brain

The AGI Brain represents an advanced artificial general intelligence system, designed to execute complex logical operations simultaneously through robust asynchronous functionality. Engineered primarily in Python, its comprehensive knowledge base is currently managed by ChromaDB, with a strategic transition to Supabase planned for enhanced scalability and dynamic evolution. This architecture features distinct logical partitions, allowing for independent task routing across diverse subjects. The system is structured into three specialized modules: a forward-focused communication segment for human interaction, a powerful core module for intricate reasoning, automation, and integrated tool use, and a dedicated 'suites' module for specialized functions such as coding, research, and skill creation. This design fundamentally optimizes the Brain for rapid advancements in AI reasoning capabilities.

---

## 🚀 Features

- 🌐 **FastAPI** backend with full CORS support
- 🤖 Connects to **Together AI’s chat-completion API**
- 🔁 Modular routing logic via **Core Brain AI** interface
- 💬 Maintains lightweight conversation memory (non-persistent)
- 📊 Tracks and logs token usage (`token_log.jsonl`)
- 🔐 `.env`-based credential loading for API keys
- 🧼 Memory reset endpoint for clean session starts

---

## 📦 Requirements

Install dependencies:

```bash

python -m venv .venv
.venv\Scripts\Activate.ps1

(when done
deactivate
)

pip install -r requirements.txt
Create a .env file:

Code snippet

TOGETHER_API_KEY=your_together_api_key
🛠️ Usage
Start the server locally:

Bash

uvicorn main:app --reload
Example POST to /chat:

JSON

{
  "prompt": "What is the Brain?",
  "max_tokens": 1000
}
🧪 API Endpoints
Method

Endpoint

Description

POST

/chat

Routes prompt through Core Brain AI to Together

GET

/usage-stats

Returns total token usage

GET

/daily-tokens

Returns token usage for today

POST

/reset-memory

Clears conversation history


Export to Sheets
🧾 Token Logging
Token usage is logged to token_log.jsonl as newline-delimited JSON:

JSON

{
  "timestamp": "2025-07-03T00:00:00Z",
  "prompt_tokens": 120,
  "completion_tokens": 100,
  "total_tokens": 220
}
🚀 Deployment (Render)
Required Files:

main.py

requirements.txt

start.sh:

Bash

#!/usr/bin/env bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app
Optional: render.yaml for infrastructure config.

Render Setup:

Push project to GitHub

Go to Render

New → Web Service

Use:

Environment: Python

Build Command: (leave blank)

Start Command: ./start.sh

Manually add .env variables

🔒 Security Notes
This system connects to external AI models and may process sensitive data. Current protections include:

API key stored in .env

Local-only use recommended during development

Future features will include:

JWT-based user auth

Route-level protection

Rate limiting and per-user memory

✍️ Author
Developed by Dillon Carey
Director of Personal AI Systems
https://dilloncarey.com