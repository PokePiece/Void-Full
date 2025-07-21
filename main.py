import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from fastapi import FastAPI, Request
#from llama_cpp import Llama
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from typing import Optional
from prompts import portfolio_prompt, scomaton_prompt, void_interface_prompt, portfolio_accomplishments_prompt, portfolio_masterpiece_prompt, portfolio_skills_prompt, portfolio_reach_prompt, void_general_prompt
from noises import run_noises


load_dotenv() 

SUPABASE_URL= os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

#print("URL:", SUPABASE_URL)
#print("KEY:", SUPABASE_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



#llm = Llama(
    #model_path="models/tinyllama-1.1b-chat-v0.3.Q4_K_M.gguf",
    #n_ctx=2048,
   # n_threads=4,
    #n_batch=32,
    #verbose=False
#)


def build_prompt(instruction: str) -> str:
    return (
        "You are a task classifier. Given an instruction, return one of the following task types:\n"
        "- summarize\n"
        "- tool_logic\n"
        "- visual\n"
        "- other\n\n"
        f"Instruction: {instruction}\n"
        "Task type:"
    )


def get_today_token_usage():
    total = 0
    today = datetime.utcnow().date()

    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                entry = json.loads(line)
                timestamp = datetime.fromisoformat(entry["timestamp"])
                if timestamp.date() == today:
                    total += entry.get("total_tokens", 0)
    except FileNotFoundError:
        pass

    return total

#Implementing Supabase message fetching and saving

def save_message(tag: str, role: str, content: str, user_id: str = None):
    
    #assert user_id, "user_id must not be None or empty"
    
    timestamp = "now()"
    
    # Insert into conversations
    convo_data = {
        "tag": tag,
        "role": role,
        "content": content,
        "timestamp": timestamp,
        "user_id": user_id,
    }
    if user_id:
        convo_data["user_id"] = user_id
    convo_response = supabase.table("conversations").insert(convo_data).execute()
    if convo_response.data is None:
        print(f"Failed to save to conversations: {convo_response}")

    # Insert into intelligence_entries
    entry_data = {
        "tags": [tag],
        "content_type": role,
        "content_text": content,
        "created_at": timestamp,
        "user_id": user_id,
    }
    if user_id:
        entry_data["user_id"] = user_id
    entry_response = supabase.table("intelligence_entries").insert(entry_data).execute()
    if entry_response.data is None:
        print(f"Failed to save to intelligence_entries: {entry_response}")

    return convo_response.data



def get_recent_messages(tag: str, user_id: str = None, limit: int = 10):
    query = supabase.table("conversations").select("*").eq("tag", tag).order("timestamp", desc=True).limit(limit)
    #query = supabase.table("intelligence_entries").select("*").eq("tags", tag).order("created_at", desc=True).limit(limit)
    if user_id:
        query = query.eq("user_id", user_id)

    response = query.execute()

    if response.data is None:
        print(f"Failed to fetch history: {response}")
        return []
    
    #print(list(reversed(response.data)))
    return list(reversed(response.data))  # oldest first






def summarize_messages(messages):
    summary = "Earlier: "
    for msg in messages:
        if msg["role"] == "user":
            summary += f"User asked about '{msg['content'][:30]}...', "
        elif msg["role"] == "assistant":
            summary += f"Assistant replied with '{msg['content'][:30]}...', "
    return {"role": "system", "content": summary.strip(", ")}


app = FastAPI()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.ai/v1/chat/completions"
LOG_FILE = "token_log.jsonl"

SCOMATON_PASSWORD = os.getenv("SCOMATON_PASSWORD")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",  # Vite dev server
    "https://scomaton.dilloncarey.com",  # If you ever serve frontend here
    "https://dilloncarey.com",
    "https://www.dilloncarey.com",
    "https://brain.dilloncarey.com",
    "http://localhost:3000",
    "https://windmatrix.dilloncarey.com",
],  # Or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow POST, OPTIONS, etc.
    allow_headers=["*"],
    
)



class ChatInput(BaseModel):
    prompt: str
    max_tokens: int = 1000
    tag: str = "default"
    user_id: Optional[str] = None
    



def os_ai_route(prompt: str, tag: str) -> str:
    if tag == "portfolio-general-chat":
        return "portfolio_general_chatbot"
    elif tag == "scomaton-general-chat":
        return "general_chatbot"
    elif tag =='brain_interface':
        return 'brain_interface'
    elif tag=='portfolio_accomplishments':
        return 'portfolio_accomplishments'
    elif tag=='portfolio_skills':
        return 'portfolio_skills'
    elif tag=='portfolio_reach':
        return 'portfolio_reach'
    elif tag=='portfolio_masterpiece':
        return 'portfolio_masterpiece'
    elif tag=='void_general':
        return 'void_general'
    else:
        return "general_chatbot"



def call_portfolio_general_chatbot(prompt: str, max_tokens: int):
    return call_chat_model(portfolio_prompt, prompt, max_tokens)

def call_general_chatbot(prompt: str, max_tokens: int):
    return call_chat_model(scomaton_prompt, prompt, max_tokens)


def call_brain_interface(prompt: str, max_tokens: int):
    return call_chat_model(void_interface_prompt, prompt, max_tokens)

def call_portfolio_accomplishments(prompt: str, max_tokens: int):
    return call_chat_model(portfolio_accomplishments_prompt, prompt, max_tokens)

def call_portfolio_masterpiece(prompt: str, max_tokens: int):
    return call_chat_model(portfolio_masterpiece_prompt, prompt, max_tokens)

def call_portfolio_skills(prompt: str, max_tokens: int):
    return call_chat_model(portfolio_skills_prompt, prompt, max_tokens)

def call_portfolio_reach(prompt: str, max_tokens: int):
    return call_chat_model(portfolio_reach_prompt, prompt, max_tokens)

def call_void_general(prompt: str, max_tokens: int, user_id: str):
    return call_chat_model(void_general_prompt, prompt, max_tokens, "void_general", user_id)



# pass tag, user id
def call_chat_model(system_prompt: str, prompt: str, max_tokens: int, tag: str, user_id: str):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    history = get_recent_messages(tag, user_id, limit=10)  # get last 10 messages

    conversation_history = [{"role": "system", "content": system_prompt}]
    for msg in history:
        conversation_history.append({"role": msg["role"], "content": msg["content"]})
        #conversation_history.append({"content_type": msg["role"], "content_text": msg["content"]})
    
    # Add current user prompt
    conversation_history.append({"role": "user", "content": prompt})

    data = {
        "model": "meta-llama/Llama-3-70b-chat-hf",
        "messages": conversation_history,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    print("Sending to TogetherAI:", data)
    response = requests.post(TOGETHER_API_URL, headers=headers, json=data)

    if not response.ok:
        print("TogetherAI error:", response.status_code, response.text)
        raise HTTPException(status_code=500, detail=response.text)

    res_json = response.json()
    ai_response = res_json["choices"][0]["message"]["content"].strip()
    
    # Save current prompt and response
    save_message(tag, "user", prompt, user_id)
    save_message(tag, "assistant", ai_response, user_id)

    return ai_response, res_json.get("usage", {})




@app.post("/chat")
def chat(input: ChatInput):
    print("💬 CHAT RECEIVED:", input)
    print("Prompt:", input.prompt)
    print("Max Tokens:", input.max_tokens)
    
    route = os_ai_route(input.prompt, input.tag)
    print(f"Routing decision: {route}")

    if route == "general_chatbot":
        ai_response, usage = call_general_chatbot(input.prompt, input.max_tokens, tag=input.tag, user_id=input.user_id)
        # ADD THIS RETURN BLOCK:
        today_total = get_today_token_usage()
        daily_limit = 33000
        warning = None
        total_tokens = usage.get("total_tokens", 0)
        if today_total > daily_limit:
            warning = f"⚠️ You’ve used {today_total} tokens today — over your soft daily limit of {daily_limit}."
        return {
            "response": ai_response,
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": total_tokens,
                "daily_total": today_total,
                "warning": warning
            }
        }
    elif route == "portfolio_general_chatbot":
        ai_response, usage = call_portfolio_general_chatbot(input.prompt, input.max_tokens)

        # Return response with usage data as before
        today_total = get_today_token_usage()
        daily_limit = 33000
        warning = None
        total_tokens = usage.get("total_tokens", 0)
        if today_total > daily_limit:
            warning = f"⚠️ You’ve used {today_total} tokens today — over your soft daily limit of {daily_limit}."

        return {
            "response": ai_response,
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": total_tokens,
                "daily_total": today_total,
                "warning": warning
            }
        }
    elif route == "brain_interface":
        ai_response, usage = call_brain_interface(input.prompt, input.max_tokens)

        # Return response with usage data as before
        today_total = get_today_token_usage()
        daily_limit = 33000
        warning = None
        total_tokens = usage.get("total_tokens", 0)
        if today_total > daily_limit:
            warning = f"⚠️ You’ve used {today_total} tokens today — over your soft daily limit of {daily_limit}."

        return {
            "response": ai_response,
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": total_tokens,
                "daily_total": today_total,
                "warning": warning
            }
        }
    elif route == "portfolio_accomplishments":
        ai_response, usage = call_portfolio_accomplishments(input.prompt, input.max_tokens)

        # Return response with usage data as before
        today_total = get_today_token_usage()
        daily_limit = 33000
        warning = None
        total_tokens = usage.get("total_tokens", 0)
        if today_total > daily_limit:
            warning = f"⚠️ You’ve used {today_total} tokens today — over your soft daily limit of {daily_limit}."

        return {
            "response": ai_response,
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": total_tokens,
                "daily_total": today_total,
                "warning": warning
            }
        }
    elif route == "portfolio_masterpiece":
        ai_response, usage = call_portfolio_masterpiece(input.prompt, input.max_tokens)

        # Return response with usage data as before
        today_total = get_today_token_usage()
        daily_limit = 33000
        warning = None
        total_tokens = usage.get("total_tokens", 0)
        if today_total > daily_limit:
            warning = f"⚠️ You’ve used {today_total} tokens today — over your soft daily limit of {daily_limit}."

        return {
            "response": ai_response,
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": total_tokens,
                "daily_total": today_total,
                "warning": warning
            }
        }
    elif route == "portfolio_skills":
        ai_response, usage = call_portfolio_skills(input.prompt, input.max_tokens)

        # Return response with usage data as before
        today_total = get_today_token_usage()
        daily_limit = 33000
        warning = None
        total_tokens = usage.get("total_tokens", 0)
        if today_total > daily_limit:
            warning = f"⚠️ You’ve used {today_total} tokens today — over your soft daily limit of {daily_limit}."

        return {
            "response": ai_response,
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": total_tokens,
                "daily_total": today_total,
                "warning": warning
            }
        }
    elif route == "portfolio_reach":
        ai_response, usage = call_portfolio_reach(input.prompt, input.max_tokens)

        # Return response with usage data as before
        today_total = get_today_token_usage()
        daily_limit = 33000
        warning = None
        total_tokens = usage.get("total_tokens", 0)
        if today_total > daily_limit:
            warning = f"⚠️ You’ve used {today_total} tokens today — over your soft daily limit of {daily_limit}."

        return {
            "response": ai_response,
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": total_tokens,
                "daily_total": today_total,
                "warning": warning
            }
        }
    elif route == "void_general":
        ai_response, usage = call_void_general(input.prompt, input.max_tokens, input.user_id)
        print(f"INPUT USER_ID: {input.user_id!r}")

        # Return response with usage data as before
        today_total = get_today_token_usage()
        daily_limit = 33000
        warning = None
        total_tokens = usage.get("total_tokens", 0)
        if today_total > daily_limit:
            warning = f"⚠️ You’ve used {today_total} tokens today — over your soft daily limit of {daily_limit}."

        return {
            "response": ai_response,
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": total_tokens,
                "daily_total": today_total,
                "warning": warning
            }
        }

    # Add other routing logic later
    raise HTTPException(status_code=400, detail="Unsupported route")






@app.get("/okcheck")
async def ok_check():
    return JSONResponse(content={"ok": True})


@app.get('/noisesauto')
def noises_auto():
    run_noises()
    return {"status": "Selenium script executed"}




@app.get("/usage-stats")
def usage_stats():
    total_prompt = 0
    total_completion = 0
    total_total = 0
    request_count = 0

    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                entry = json.loads(line)
                total_prompt += entry.get("prompt_tokens", 0)
                total_completion += entry.get("completion_tokens", 0)
                total_total += entry.get("total_tokens", 0)
                request_count += 1
    except FileNotFoundError:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "request_count": 0
        }

    return {
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_total,
        "request_count": request_count
    }



@app.post("/reset-memory")
def reset_memory():
    #conversation_history[:] = conversation_history[:1]  # Keep system prompt only
    return {"message": "Memory cleared"}



@app.get("/daily-tokens")
def daily_tokens():
    daily_limit = 33000
    used = get_today_token_usage()
    remaining = max(daily_limit - used, 0)
    approx_responses_left = remaining // 1000

    return {
        "daily_limit": daily_limit,
        "tokens_used_today": used,
        "tokens_remaining": remaining,
        "estimated_responses_left": approx_responses_left
    }




#@app.post("/route-task")
#async def route_task(request: Request):
    #data = await request.json()
    #instruction = data.get("instruction", "")

    #prompt = build_prompt(instruction)

    #result = llm(prompt, max_tokens=10, stop=["\n"])
    #output = result["choices"][0]["text"].strip().lower()

    #return {"task_type": output}