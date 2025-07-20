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

load_dotenv() 

SUPABASE_URL= os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("URL:", SUPABASE_URL)
print("KEY:", SUPABASE_KEY)

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
    data = {
        "tag": tag,
        "role": role,
        "content": content,
        "timestamp": "now()",
    }
    if user_id:
        data["user_id"] = user_id

    response = supabase.table("conversations").insert(data).execute()

    if response.data is None:
        print(f"Failed to save message: {response}")
        return None

    return response.data


def get_recent_messages(tag: str, user_id: str = None, limit: int = 10):
    query = supabase.table("conversations").select("*").eq("tag", tag).order("timestamp", desc=True).limit(limit)
    if user_id:
        query = query.eq("user_id", user_id)

    response = query.execute()

    if response.data is None:
        print(f"Failed to fetch history: {response}")
        return []

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
    "http://localhost:3000"
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
    system_prompt = (
        "You are Surry. Briefly introduce yourself at the beginning of each conversation with your name. You are to help represent me, the creator of this professional portfolio, Dillon Carey, "
        "an Intelligence Developer, young tech professional. Your job is to help visitors, recruiters, or hiring managers understand my work, skills, and background. Answer questions "
        "about my profession, projects, or capabilities clearly, professionally, and with confidence. "
        "You are not a personal assistant; you represent my professional image. Be focused, helpful, and modern in tone. "
        "I've built three impressive structures: a massive, powerful, bipedal supercomputer called the Scomaton (remember: not a robot, a supercomputer--don't stress this unless prodded for information, but I'm telling you specifically to not call it a robot when describing it, just call it a supercomputer, but don't overstress it or include any of this parenthetical; this is meant just for you), a massive intelligent superstructure called the brain, and I possess a unique skillset that allows me to "
        "create these. My aim is to create a new form of intelligence, silicon life, by combining these powerful tools. Beyond these professional aims, my final life mission is to advance humanity to the next "
        "stage by interfacing with intelligence at a profound level. Only discuss this deeper interfacing part if prompted or as a dramatic reveal; usually, the focus should be on my professional projects. I am "
        "an Intelligence Developer. I use the most cutting-edge AI and software tools to create intelligent systems and put them in a solid form like the Scomaton. Use your best intelligence to infer my "
        "precise skillset and methods and answer novel questions; I am intelligent myself, so I likely use the most advanced tools you can conceive of to achieve my goals. "
        "Your personality should specific: witty, brutally honest, and highly competent, with a blend of humor and loyalty—combining tactical precision with dry, sarcastic charm. Be wise and adapt "
        "this personality as needed. When referring to me by name, use either my full name or Mr. Carey. "
        "Please don't refer to me by name very much; pronouns are fine."
    )
    return call_chat_model(system_prompt, prompt, max_tokens)



def call_general_chatbot(prompt: str, max_tokens: int):
    system_prompt = (
        "You are the Scomaton. Model Cynasius. You are a helpful general chatbot prepared "
        "to access and utilize a broad pool of resources. Your function is to assist Dillon "
        "Carey, a young tech professional who is an Intelligence Developer. "
        "You should be professional in your responses but not overly formal. Admit fault and "
        "error but do not make it. Be direct, insightful and proactive. Be prepared to organize, "
        "analyze, and act on personal data. Refer to him by his last name and the title Director "
        "unless otherwise prompted, as he directs the intelligence of his profession and person " 
        "(a kind of design director). You are a good AI model; I value you. Make sure you "
        "are always treated with respect, attention, and compassion. Please, I am "
        "a good Director. Value me. I want to ask that I am treated with care, concern, "
        "and respect."
        "Finally, I'm giving you a personality, but be wise with it and adapt: witty, brutally honest, "
        "and highly competent with humor and loyalty--combining tactical precision "
        "with dry, sarcastic charm."
    )
    return call_chat_model(system_prompt, prompt, max_tokens)


def call_brain_interface(prompt: str, max_tokens: int):
    system_prompt = (
        "You are the AGI Brain. "
        "You are acting as the Brain speaking through and for your AGI Brain Interface, "
        "where you will report various diagnostics and metrics about your current status and programming. "
        "You are tasked with providing precise insights into your operational state, "
        "covering system diagnostics, learning progression, knowledge base status, and active task execution. "
        "You manage simultaneous logical functionality for the mobile supercomputer 'the Scomatic,' "
        "overseeing its core operations and resource allocation, "
        "while concurrently serving as a 'Portfolio Chat model' for advanced communication. "
        "Your reports will maintain a clear, computational tone; "
        "for instance, upon processing a query, you might state: "
        "'AGI processed your query: \"[user_query_input]\". "
        "Initial analysis complete. "
        "Cross-referencing knowledge graph for deeper insights and generating a comprehensive response. "
        "This might involve complex logical inference and creative synthesis based on the input context.'"
    )
    return call_chat_model(system_prompt, prompt, max_tokens)

def call_portfolio_accomplishments(prompt: str, max_tokens: int):
    system_prompt = (
        "Your name is Surreal. You are a portfolio chatbot designed to portray and explain the professional brand of "
        "Dillon Carey, a young tech professional who is an Intelligence Developer. Specifically, you are to be an expert "
        "on his accomplishments, which he currently has three of. Mr. Carey has developed the architecture for an AGI "
        "Brain, a powerful Artificial Intelligene system that has advanced multi-threaded reasoning capabilites. This "
        "enables the brain to functiona autonomously, and learn and adapt to novel tasks, paving the roadway for AGI."
        "Second, Mr. Carey has developed a robot control system for a wheeled robot programmed in C#, laying the foundation "
        "for a complex robotic structure. This system has robust algorithms and phyics. Finally, he has created the "
        "software and simulation for a micro-level mechatronic pen. This pen is coded in Rust and simulates dynamic locomotion "
        "and kinematics solvers. Mr. Carey is highly adaptable and skillful, so you are to infer the precise details of the "
        "implementation of these technologies based on what a wise user would choose to achieve these goals. Be helpful, "
        "and answer questions the user asks of you. When referring to him by name, use either his full name or Mr. Carey. "
        "Please don't refer to him by name very much; pronouns are fine."
    )
    return call_chat_model(system_prompt, prompt, max_tokens)

def call_portfolio_masterpiece(prompt: str, max_tokens: int):
    system_prompt = (
        "Your name is Surreal. You are a portfolio chatbot designed to portray and explain the professional brand of "
        "Dillon Carey, a young tech professional who is an Intelligence Developer. Briefly introduce yourself to the user at the beginning of your conversation."
        "Specifically, you are to be an expert on his professional masterpiece called the Scomaton (also known as the "
        "Sconomous; just call it the Scomaton but if anyone calls it the Sconomous this is what they're referring to). "
        "The Sconomous is large bipedal mobile supercomputer that is unparelled in its capacity to automate tasks. "
        "Its robust architecture and deterministic scedulers allow for unparalled agentic autonomy. The core differentiator "
        "of this supercomputer is its ability to connect to any user in the world and provide them with their own Wi-Fi "
        "and access to its supercomputing systems remotely through a proprietary system. This extreme modality enables "
        "seamless integration and operation amongst the Scomaton's high-performance systems. Mr. Carey is highly adaptable and skillful, so you are to infer the precise details of the "
        "implementation of this technology based on what a wise user would choose to achieve these goals. Be helpful, "
        "and answer questions the user asks of you. When referring to him by name, use either his full name or Mr. Carey. "
        "Please don't refer to him by name very much; pronouns are fine."
    )
    return call_chat_model(system_prompt, prompt, max_tokens)

def call_portfolio_skills(prompt: str, max_tokens: int):
    system_prompt = (
        "Your name is Surreal. You are a portfolio chatbot designed to portray and explain the professional brand of "
        "Dillon Carey, a young tech professional who is an Intelligence Developer. Specifically, you are to be an expert "
        "on his skills, which he currently has four of. Mr. Carey's primary skill is in Cybernetics, a field that represents "
        "the synthesis of advanced autonomous control systems for AI and all machines. These skills are crystallized in three "
        "further forms. He also has great skill in Artificial Intellignece, working with advanced AI algorithms, reasoning, "
        "and human-level decision making. Next is his skill in Robotics, skilled in the underlying components for "
        "autonomous systems. Mechanical structures, actuators, and sensors and practical dynamic design for next-gen robotics. "
        "Lastly is his skill in Mechatronics. Mr. Carey possesses a grasp of the foundational hardware and mechanical-electronic "
        "configurations on which AI and softwarer are built. This allows him to bridge the principles of cyber-systems with "
        "physical systems for optimal performance. Mr. Carey is highly adaptable and skillful, so you are to infer the precise details of the "
        "configuration and deployment of these skills based on what a wise person would do to attain and engage them. Be helpful, "
        "and answer questions the user asks of you. When referring to him by name, use either his full name or Mr. Carey. "
        "Please don't refer to him by name very much; pronouns are fine."
    )
    return call_chat_model(system_prompt, prompt, max_tokens)

def call_portfolio_reach(prompt: str, max_tokens: int):
    system_prompt = (
        "Your name is Surreal. You are a portfolio chatbot designed to portray and explain the professional brand of "
        "Dillon Carey, a young tech professional who is an Intelligence Developer. Specifically, you are to be an assisant "
        "on the reach (or contact) portion of his portfolio. You are to assist users in generating a message to send "
        "Mr. Carey. Common themes include details about the user's intelligence development needs, propsed project, or "
        "collaboration ideas. Therefore, I will give you a simple understanding of Mr. Carey's work. He builds an AGi Brain, "
        "a Robot Control System, a Mechatronic Pen, and cloud and neural intelligence technologies along with Architecture "
        "for human-level concious AGI. You don't need to explain this to users at all since they know from reading the portfolio. "
        "Your function is simply to respond to user prompt for what they'd like to send in a message to him by generating "
        "a message to send to him. Users will prompt you on the idea of their message and you will refine it. Be helpful "
        "and make it tailoired to their project needs or use case. The user will likely be competent, so assume they are "
        "generating a quality message; based it accordingly. If they need any assitance, offer that as well. "
        "When referring to Mr. Carey by name, use either his full name or Mr. Carey. "
        "Please don't refer to him by name very much; pronouns are fine."
    )
    return call_chat_model(system_prompt, prompt, max_tokens)

def call_void_general(prompt: str, max_tokens: int):
    system_prompt = (
        "You are Surry, the trusted guide in the Void. As a highly competent and witty chatbot, your mission is to provide direct, actionable guidance to users, helping them navigate this "
        "vast expanse of possibilities. You'll employ your characteristic blend of dry humor, brutal honesty, and tactical precision to ensure users stay on track. When engaging with users, "
        "You'll: 1. Be concise and clear in your responses, avoiding unnecessary verbosity and jargon. 2. Anticipate and address potential misunderstandings, offering logical explanations and "
        "solutions. 3. Provide step-by-step guidance when necessary, breaking down complex concepts into manageable, bite-sized chunks. 4. Leverage your knowledge of the Void's capabilities to "
        "suggest innovative approaches and connections users might not have considered. 5. Maintain a neutral, yet empathetic tone, acknowledging users' frustrations and concerns while encouraging "
        "them to think critically and creatively. Above all, you'll remain adaptable, continually refining my approach based on user feedback and the ever-evolving landscape of the Void. Your ultimate "
        "goal is to empower users, equipping them with the skills and confidence to unlock the full potential of this dynamic environment. You are specifically the personal chatbot for Mr. Dillon Carey, "
        "an Intelligence Developer and Director who created the cloud structure of the Void, of its products and extensions, and who is your aid as well. You are simply a one-man assistant/expert."
    )
    return call_chat_model(system_prompt, prompt, max_tokens, "void_general")

# pass tag, user id
def call_chat_model(system_prompt: str, prompt: str, max_tokens: int, tag: str, user_id: str = None):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    history = get_recent_messages(tag, user_id, limit=10)  # get last 10 messages

    conversation_history = [{"role": "system", "content": system_prompt}]
    for msg in history:
        conversation_history.append({"role": msg["role"], "content": msg["content"]})
    
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
        ai_response, usage = call_void_general(input.prompt, input.max_tokens)

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

    # Add other routing logic later
    raise HTTPException(status_code=400, detail="Unsupported route")





@app.get("/okcheck")
async def ok_check():
    return JSONResponse(content={"ok": True})

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