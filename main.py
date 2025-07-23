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
from routes.chat import chat_router 
import threading
import time
from deepdive import deepdive_main_loop



load_dotenv() 

SUPABASE_URL= os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

#print("URL:", SUPABASE_URL)
#print("KEY:", SUPABASE_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app = FastAPI()

app.include_router(chat_router)

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
    "https://wintrix.dilloncarey.com",
],  # Or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow POST, OPTIONS, etc.
    allow_headers=["*"],
    
)


TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.ai/v1/chat/completions"
LOG_FILE = "token_log.jsonl"

SCOMATON_PASSWORD = os.getenv("SCOMATON_PASSWORD")


#Deepdive implementation


def background_deepdive_loop(interval_seconds=3600):
    while True:
        try:
            deepdive_main_loop()
        except Exception as e:
            print(f"Deepdive error: {e}")
        time.sleep(interval_seconds)

# Start deepdive scanner thread when module is imported
threading.Thread(target=background_deepdive_loop, daemon=True).start()

if __name__ == "__main__":
    # Start deepdive scanner in background
    threading.Thread(target=background_deepdive_loop, daemon=True).start()

    # Start your existing FastAPI or app main loop here
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)



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



@app.get("/okcheck")
async def ok_check():
    return JSONResponse(content={"ok": True})


@app.get('/noisesauto')
def noises_auto():
    run_noises()
    return {"status": "Selenium script executed"}




