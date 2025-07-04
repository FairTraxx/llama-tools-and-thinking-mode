import requests
import time
import re
import os
from pathlib import Path
from tools import create_tools, ToolResult

# Config
API_URL = "http://127.0.0.1:52415/v1/chat/completions"
MODEL_NAME = "llama-3.2-3b"  # Replace with your actual model name if needed

# Dynamic workspace detection - use the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
WORKSPACE_ROOT = str(SCRIPT_DIR)

# Context file configuration
CONTEXT_FILE = "context.md"  # Markdown file to append to system prompt

# Context monitoring configuration
CONTEXT_LIMITS = {
    "llama-3.2-1b": 8192,      # 8K context window
    "llama-3.2-3b": 32768,     # 32K context window  
    "llama-3.2-8b": 131072,    # 128K context window
    "llama-3.2": 32768,        # Default assumption for generic name
}

# Get context limit for current model
MAX_CONTEXT_TOKENS = CONTEXT_LIMITS.get(MODEL_NAME, 32768)
WARNING_THRESHOLD = 0.8  # Warn when 80% of context is used
CRITICAL_THRESHOLD = 0.9  # Critical warning at 90%

# Thinking mode configuration
thinking_config = {
    "temperature": 0.7,        # Balanced creativity for reasoning
    "top_p": 0.9,             # Broad vocabulary for thinking process
    "max_tokens": 400,        # Longer responses to allow for thinking + answer
    "presence_penalty": 0.3,   # Encourage exploring different aspects
    "frequency_penalty": 0.2,  # Avoid repetitive reasoning patterns
}

# Initialize tools system with dynamic workspace
tools = create_tools(WORKSPACE_ROOT)

def load_context_from_file(filename):
    """
    Load additional context from a markdown file
    Returns the content as a string, or empty string if file doesn't exist
    """
    try:
        # Use the dynamic workspace root
        file_path = os.path.join(WORKSPACE_ROOT, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                print(f"📄 Loaded additional context from {filename} ({len(content)} characters)")
                print(f"📁 Workspace: {WORKSPACE_ROOT}")
                return f"\n\nADDITIONAL CONTEXT:\n{content}"
            else:
                print(f"📄 Context file {filename} is empty")
                return ""
    except FileNotFoundError:
        print(f"📄 Context file {filename} not found in {WORKSPACE_ROOT} - continuing without additional context")
        return ""
    except Exception as e:
        print(f"⚠️  Error reading context file {filename}: {e}")
        return ""

def create_system_prompt():
    """
    Create the system prompt with optional additional context from file
    """
    base_prompt = (
        "You are an AI assistant with advanced reasoning capabilities. "
        "When responding to any query, you must show your thinking process before giving your final answer. "
        "Structure your response EXACTLY like this:\n\n"
        "<thinking>\n"
        "Here you should show your step-by-step reasoning, consider different angles, "
        "weigh pros and cons, think through the problem, explore implications, etc. "
        "Be thorough and show your mental process.\n"
        "</thinking>\n\n"
        "Then provide your final, clear response after the thinking section. "
        "Always use this format - thinking section first, then final answer.\n\n"
        "AVAILABLE TOOLS:\n"
        "You have access to the following tools that you can call during your response:\n\n"
        "- list_dir: List contents of a directory\n"
        "  Usage: TOOL:list_dir(relative_workspace_path=\".\", explanation=\"exploring the workspace\")\n"
        "  Use this FIRST to see what files are available in the workspace.\n\n"
        "- read_file: Read contents of a file\n"
        "  Usage: TOOL:read_file(target_file=\"actual_filename.py\", should_read_entire_file=false, start_line_one_indexed=1, end_line_one_indexed_inclusive=50, explanation=\"reading the file\")\n"
        "  IMPORTANT: Only use REAL filenames that exist in the workspace. Use list_dir first to see available files.\n\n"
        "TOOL USAGE RULES:\n"
        "1. ALWAYS use list_dir first to see what files are available\n"
        "2. ONLY use real filenames that exist (like 'tools.py', 'context.md', etc.)\n"
        "3. NEVER use placeholder names like 'path_to_file', 'filename.ext', 'example.py'\n"
        "4. Use tools directly in your response (NOT inside code blocks)\n"
        "5. Example of correct usage:\n"
        "   TOOL:list_dir(relative_workspace_path=\".\", explanation=\"exploring workspace\")\n"
        "   TOOL:read_file(target_file=\"llm_thinking_mode.py\", should_read_entire_file=false, start_line_one_indexed=1, end_line_one_indexed_inclusive=20, explanation=\"reading the script header\")\n\n"
        "When a user asks about files, always start by listing the directory to see what's available, "
        "then read the specific files they're interested in using the actual filenames you discovered."
    )
    
    # Load additional context from file
    additional_context = load_context_from_file(CONTEXT_FILE)
    
    return {
        "role": "system", 
        "content": base_prompt + additional_context
    }

def estimate_tokens(text):
    """
    Rough estimation of token count (1 token ≈ 4 characters for English)
    This is approximate - real tokenizers are more complex
    """
    return len(text) // 4

def count_message_tokens(messages):
    """
    Estimate total tokens in message history
    """
    total_tokens = 0
    for message in messages:
        # Count tokens in content
        content_tokens = estimate_tokens(message["content"])
        # Add overhead for role, formatting, etc. (roughly 10 tokens per message)
        total_tokens += content_tokens + 10
    return total_tokens

def get_context_usage(messages):
    """
    Calculate context usage statistics
    Returns: (current_tokens, max_tokens, usage_percentage, status)
    """
    current_tokens = count_message_tokens(messages)
    usage_percentage = (current_tokens / MAX_CONTEXT_TOKENS) * 100
    
    if usage_percentage >= CRITICAL_THRESHOLD * 100:
        status = "CRITICAL"
    elif usage_percentage >= WARNING_THRESHOLD * 100:
        status = "WARNING"
    else:
        status = "OK"
    
    return current_tokens, MAX_CONTEXT_TOKENS, usage_percentage, status

def display_context_info(messages):
    """
    Display current context usage with color-coded status
    """
    current_tokens, max_tokens, usage_pct, status = get_context_usage(messages)
    
    # Color codes for status
    status_colors = {
        "OK": "🟢",
        "WARNING": "🟡", 
        "CRITICAL": "🔴"
    }
    
    status_icon = status_colors.get(status, "⚪")
    
    print(f"\n📊 CONTEXT USAGE: {status_icon} {status}")
    print(f"   Tokens: {current_tokens:,} / {max_tokens:,} ({usage_pct:.1f}%)")
    print(f"   Messages: {len(messages)} in history")
    
    # Show warnings
    if status == "WARNING":
        print(f"   ⚠️  Warning: Approaching context limit!")
    elif status == "CRITICAL":
        print(f"   🚨 Critical: Very close to context limit!")
        print(f"   💡 Consider clearing history soon")
    
    # Show remaining capacity
    remaining_tokens = max_tokens - current_tokens
    print(f"   📝 Estimated remaining: ~{remaining_tokens:,} tokens")
    
    return status

def call_llm_thinking(messages):
    """
    Calls the LLM with thinking mode configuration
    Returns both the thinking process and final response
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        **thinking_config
    }
    
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def parse_thinking_response(response):
    """
    Separates the thinking process from the final answer
    Returns: (thinking_process, final_answer)
    """
    # Look for <thinking> tags
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', response, re.DOTALL)
    
    if thinking_match:
        thinking_process = thinking_match.group(1).strip()
        # Everything after </thinking> is the final answer
        final_answer = re.sub(r'<thinking>.*?</thinking>\s*', '', response, flags=re.DOTALL).strip()
    else:
        # Fallback: if no tags found, treat first half as thinking, second as answer
        parts = response.split('\n\n', 1)
        thinking_process = parts[0] if len(parts) > 1 else "No explicit thinking process found"
        final_answer = parts[1] if len(parts) > 1 else response
    
    return thinking_process, final_answer

def display_thinking_response(thinking_process, final_answer):
    """
    Displays the thinking process and final answer in a formatted way
    """
    print("\n" + "="*60)
    print("🧠 THINKING PROCESS:")
    print("="*60)
    print(thinking_process)
    print("\n" + "-"*60)
    print("💡 FINAL RESPONSE:")
    print("-"*60)
    print(final_answer)
    print("="*60)

def run_thinking_chat():
    """
    Interactive chat with thinking mode enabled and context monitoring
    """
    messages = [create_system_prompt()]
    
    print("🤖 AI Thinking Mode Chat with Context Monitoring")
    print("Ask me anything and I'll show you my reasoning process!")
    print("Commands:")
    print("  'quit' - Exit the chat")
    print("  'context' - Show detailed context information")
    print("  'clear' - Clear conversation history")
    print("  'help' - Show this help message\n")
    
    # Show initial context status
    display_context_info(messages)
    
    while True:
        # Get user input
        user_input = input("\n👤 You: ").strip()
        
        # Handle commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        elif user_input.lower() == 'context':
            display_context_info(messages)
            continue
        elif user_input.lower() == 'clear':
            messages = [create_system_prompt()]  # Reset to just system prompt
            print("🧹 Conversation history cleared!")
            display_context_info(messages)
            continue
        elif user_input.lower() == 'help':
            print("\n📚 Available Commands:")
            print("  'quit' - Exit the chat")
            print("  'context' - Show detailed context information")
            print("  'clear' - Clear conversation history")
            print("  'help' - Show this help message")
            continue
        elif not user_input:
            continue
            
        # Check context before adding new message
        temp_messages = messages + [{"role": "user", "content": user_input}]
        context_status = get_context_usage(temp_messages)[3]
        
        if context_status == "CRITICAL":
            print("\n🚨 WARNING: Context is nearly full!")
            choice = input("Continue anyway? (y/n) or 'clear' to reset: ").lower()
            if choice == 'clear':
                messages = [create_system_prompt()]
                print("🧹 Conversation history cleared!")
                display_context_info(messages)
                # Re-add the current user input
                temp_messages = messages + [{"role": "user", "content": user_input}]
            elif choice != 'y':
                continue
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        print("\n🤖 AI is thinking...")
        
        try:
            # Get response with thinking process
            response = call_llm_thinking(messages)
            
            # Parse thinking vs final answer
            thinking_process, final_answer = parse_thinking_response(response)
            
            # Display formatted response
            display_thinking_response(thinking_process, final_answer)
            
            # Check for and execute any tool calls in the response
            tool_calls = parse_tool_calls(response)
            if tool_calls:
                print(f"\n🔧 Found {len(tool_calls)} tool call(s) to execute...")
                tool_results = execute_tools(tool_calls)
                
                # Add tool results to context for next response
                tool_context = "\n\nTOOL RESULTS:\n"
                for i, result in enumerate(tool_results):
                    if result.success:
                        tool_context += f"Tool {i+1} succeeded:\n{result.content}\n\n"
                    else:
                        tool_context += f"Tool {i+1} failed: {result.error}\n\n"
                
                # Add tool results to final answer for context
                final_answer_with_tools = final_answer + tool_context
            else:
                final_answer_with_tools = final_answer
            
            # Add to conversation history (final answer + any tool results)
            messages.append({
                "role": "assistant",
                "content": final_answer_with_tools
            })
            
            # Show context status after each exchange
            status = display_context_info(messages)
            
            # Auto-suggest clearing if critical
            if status == "CRITICAL":
                print("\n💡 Tip: Type 'clear' to reset conversation history")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            # Remove the failed user message
            messages.pop()

# Alternative: Batch questions mode
def run_batch_thinking(questions):
    """
    Process multiple questions in batch mode
    """
    messages = [create_system_prompt()]
    
    print("🤖 AI Thinking Mode - Batch Processing")
    print("="*60)
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 QUESTION {i}: {question}")
        
        messages_copy = messages + [{
            "role": "user", 
            "content": question
        }]
        
        try:
            response = call_llm_thinking(messages_copy)
            thinking_process, final_answer = parse_thinking_response(response)
            display_thinking_response(thinking_process, final_answer)
            
        except Exception as e:
            print(f"❌ Error processing question {i}: {e}")
        
        time.sleep(1)  # Brief pause between questions

def parse_tool_calls(response):
    """
    Parse tool calls from AI response
    Looks for patterns like: TOOL:read_file(target_file="example.py", should_read_entire_file=true, ...)
    Also handles tool calls inside Python code blocks
    
    Returns: List of (tool_name, tool_params) tuples
    """
    tool_calls = []
    
    # Look for TOOL: patterns - handle both plain text and code blocks
    # Pattern 1: Plain TOOL: calls
    tool_pattern = r'TOOL:(\w+)\((.*?)\)'
    matches = re.findall(tool_pattern, response, re.DOTALL)
    
    # Pattern 2: TOOL: calls inside code blocks
    code_block_pattern = r'```python\s*\n(.*?)\n```'
    code_blocks = re.findall(code_block_pattern, response, re.DOTALL)
    for code_block in code_blocks:
        code_matches = re.findall(tool_pattern, code_block, re.DOTALL)
        matches.extend(code_matches)
    
    # Track seen tool calls to avoid duplicates
    seen_calls = set()
    
    for tool_name, params_str in matches:
        try:
            params = {}
            
            # Handle read_file specifically
            if tool_name == "read_file":
                # Extract target_file - try multiple patterns
                target_file_match = None
                
                # Pattern 1: With quotes
                target_file_match = re.search(r'target_file\s*=\s*["\']([^"\']+)["\']', params_str)
                if not target_file_match:
                    # Pattern 2: Without quotes, up to comma or end
                    target_file_match = re.search(r'target_file\s*=\s*([^,\s)]+)', params_str)
                
                if target_file_match:
                    params['target_file'] = target_file_match.group(1).strip()
                else:
                    print(f"⚠️ Could not extract target_file from tool call: {params_str}")
                    continue
                
                # Extract should_read_entire_file
                should_read_entire_match = re.search(r'should_read_entire_file\s*=\s*(true|false)', params_str, re.IGNORECASE)
                if should_read_entire_match:
                    params['should_read_entire_file'] = should_read_entire_match.group(1).lower() == 'true'
                else:
                    # Default to false if not specified
                    params['should_read_entire_file'] = False
                
                # Extract start_line_one_indexed
                start_line_match = re.search(r'start_line_one_indexed\s*=\s*(\d+)', params_str)
                if start_line_match:
                    params['start_line_one_indexed'] = int(start_line_match.group(1))
                else:
                    # Default to 1 if not specified
                    params['start_line_one_indexed'] = 1
                
                # Extract end_line_one_indexed_inclusive
                end_line_match = re.search(r'end_line_one_indexed_inclusive\s*=\s*(\d+)', params_str)
                if end_line_match:
                    params['end_line_one_indexed_inclusive'] = int(end_line_match.group(1))
                else:
                    # Default to 50 if not specified
                    params['end_line_one_indexed_inclusive'] = 50
                
                # Extract explanation
                explanation_match = re.search(r'explanation\s*=\s*["\']([^"\']+)["\']', params_str)
                if explanation_match:
                    params['explanation'] = explanation_match.group(1)
                else:
                    # Default explanation
                    params['explanation'] = f"Reading file {params.get('target_file', 'unknown')}"
                
                # Create a unique identifier for this tool call
                call_id = f"{tool_name}:{params.get('target_file', '')}:{params.get('start_line_one_indexed', 1)}:{params.get('end_line_one_indexed_inclusive', 50)}"
                
                # Ensure all required parameters are present
                required_params = ['target_file', 'should_read_entire_file', 'start_line_one_indexed', 'end_line_one_indexed_inclusive', 'explanation']
                if all(param in params for param in required_params):
                    if call_id not in seen_calls:
                        tool_calls.append((tool_name, params))
                        seen_calls.add(call_id)
                else:
                    missing = [p for p in required_params if p not in params]
                    print(f"⚠️ Tool call {tool_name} missing required parameters: {missing}")
                    
            # Handle list_dir tool
            elif tool_name == "list_dir":
                # Extract relative_workspace_path
                path_match = re.search(r'relative_workspace_path\s*=\s*["\']([^"\']*)["\']', params_str)
                if path_match:
                    params['relative_workspace_path'] = path_match.group(1)
                else:
                    # Default to current directory
                    params['relative_workspace_path'] = "."
                
                # Extract explanation
                explanation_match = re.search(r'explanation\s*=\s*["\']([^"\']+)["\']', params_str)
                if explanation_match:
                    params['explanation'] = explanation_match.group(1)
                else:
                    # Default explanation
                    params['explanation'] = f"Listing directory {params.get('relative_workspace_path', '.')}"
                
                # Create a unique identifier for this tool call
                call_id = f"{tool_name}:{params.get('relative_workspace_path', '.')}"
                
                # Add the tool call if not seen before
                if call_id not in seen_calls:
                    tool_calls.append((tool_name, params))
                    seen_calls.add(call_id)
                
            else:
                # Generic parameter parsing for other tools
                param_pairs = re.findall(r'(\w+)\s*=\s*([^,]+)', params_str)
                
                for key, value in param_pairs:
                    value = value.strip()
                    if value.lower() == 'true':
                        params[key] = True
                    elif value.lower() == 'false':
                        params[key] = False
                    elif value.startswith('"') and value.endswith('"'):
                        params[key] = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        params[key] = value[1:-1]
                    elif value.isdigit():
                        params[key] = int(value)
                    else:
                        params[key] = value
                
                # Create a simple unique identifier
                call_id = f"{tool_name}:{str(sorted(params.items()))}"
                if call_id not in seen_calls:
                    tool_calls.append((tool_name, params))
                    seen_calls.add(call_id)
                
        except Exception as e:
            print(f"⚠️ Error parsing tool call {tool_name}: {e}")
    
    return tool_calls

def execute_tools(tool_calls):
    """
    Execute a list of tool calls and return results
    
    Args:
        tool_calls: List of (tool_name, tool_params) tuples
        
    Returns:
        List of ToolResult objects
    """
    results = []
    
    for tool_name, params in tool_calls:
        print(f"🔧 Executing tool: {tool_name}")
        
        # Execute the tool
        result = tools.execute_tool(tool_name, **params)
        results.append(result)
        
        # Display result
        if result.success:
            print(f"✅ Tool {tool_name} executed successfully")
            print(result.content)
        else:
            print(f"❌ Tool {tool_name} failed: {result.error}")
    
    return results

if __name__ == "__main__":
    # Interactive mode by default
    run_thinking_chat()
    
    # Uncomment below for batch mode example:
    # sample_questions = [
    #     "What is consciousness?",
    #     "How should AI be regulated?", 
    #     "What's the meaning of existence?"
    # ]
    # run_batch_thinking(sample_questions) 