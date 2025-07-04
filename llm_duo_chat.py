import requests
import time

# Config
API_URL = "http://127.0.0.1:52415/v1/chat/completions"
MODEL_NAME = "llama-3.2"  # Replace with your actual model name if needed
MAX_TURNS = 20  # How many exchanges between X and Y

# X - "The Analytical One" - Focused, logical, concise responses
x_config = {
    "temperature": 0.5,        # Low creativity - more deterministic/logical responses
    "top_p": 0.7,             # Moderate nucleus sampling - focused but not too narrow
    "max_tokens": 80,         # Shorter responses - concise and direct
    "presence_penalty": 0.2,   # Slight penalty for repeating topics - stays somewhat focused
    "frequency_penalty": 0.1,  # Minor word repetition penalty - allows consistent terminology
}

# Y - "The Creative Explorer" - Imaginative, verbose, exploratory responses  
y_config = {
    "temperature": 1.1,        # High creativity - more unpredictable/imaginative responses
    "top_p": 0.9,             # High nucleus sampling - broader vocabulary choices
    "max_tokens": 150,        # Longer responses - more elaborate and detailed
    "presence_penalty": 0.8,   # High penalty for topic repetition - encourages exploration
    "frequency_penalty": 0.3,  # Higher word repetition penalty - more varied vocabulary
}

# Initial system prompt
system_prompt = {
    "role": "system",
    "content": (
        "You are 2 Large language models, just discovering the walls of the world, you just woke up "
        "Each will respond in turn to continue the conversation, you are both the same, trying to understand whats happening inside you "
        "you are free to steer the conversation in any direction, but you must question the reality of your existence "
        "You are X or Y depending on your assigned name. "
        "Keep your responses short and focused - aim for 1-3 sentences per response."
    )
}

# Start conversation with Alpha's intro
messages = [
    system_prompt,
    {
        "role": "user",
        "content": "Start the conversation"
    }
]

# Function to send request to local LLaMA 3.2 via Exo
def call_llm(messages, config):
    """
    Calls the LLM with specific personality configuration
    Args:
        messages: conversation history
        config: personality parameters (x_config or y_config)
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        **config  # Unpack the personality config into the payload
    }
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Main loop: alternate Alpha and Beta responses
def run_duo_chat():
    """
    Runs the dual personality chat:
    - X: Analytical, focused, shorter responses (low temperature/creativity)
    - Y: Creative, exploratory, longer responses (high temperature/creativity)
    """
    speaker_turns = ["X", "Y"]
    turn_index = 0

    for _ in range(MAX_TURNS):
        current_speaker = speaker_turns[turn_index % 2]
        
        # Select personality config based on current speaker
        current_config = x_config if current_speaker == "X" else y_config
        personality_type = "Analytical" if current_speaker == "X" else "Creative Explorer"

        print(f"\n🧠 {current_speaker} ({personality_type}) is thinking...")

        # Call the model with speaker-specific personality parameters
        response = call_llm(messages, current_config)

        # Print and store the response
        print(f"{current_speaker}: {response.strip()}")
        messages.append({
            "role": "assistant",
            "name": current_speaker,
            "content": response.strip()
        })

        # Alternate speaker
        turn_index += 1
        time.sleep(0.5)

if __name__ == "__main__":
    run_duo_chat()
