import requests
import time

API_URL = "http://127.0.0.1:52415/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}

def get_llm_response(messages):
    payload = {
        "model": "lama3",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return None

def swap_roles(history):
    swapped = []
    for msg in history:
        swapped.append({
            "role": "assistant" if msg["role"] == "user" else "user",
            "content": msg["content"]
        })
    return swapped

# System prompts for each LLM
SYSTEM_LLM1 = "You are LLM1. You're debating with another AI. Respond concisely as the USER."
SYSTEM_LLM2 = "You are LLM2. You're debating with another AI. Respond concisely as the ASSISTANT."

# Initial setup
conversation_history = [
    {"role": "user", "content": "Should AI development be open-sourced or proprietary?"}
]

# Conversation loop
for turn in range(4):  # 4 turns (2 each)
    # LLM2's turn (assistant response)
    if turn % 2 == 0:
        messages = [{"role": "system", "content": SYSTEM_LLM2}] + conversation_history
        response = get_llm_response(messages)
        if response:
            print(f"LLM2: {response}")
            conversation_history.append({"role": "assistant", "content": response})
    
    # LLM1's turn (user response)
    else:
        swapped_history = swap_roles(conversation_history)
        messages = [{"role": "system", "content": SYSTEM_LLM1}] + swapped_history
        response = get_llm_response(messages)
        if response:
            print(f"LLM1: {response}")
            conversation_history.append({"role": "user", "content": response})
    
    time.sleep(1)  # Avoid rate limiting