# llama thiking mode with tools and context monitoring

A Python codebase for adding thinking mode and tools over the normal llama models, has context tracking and suppourts exo.

## Features

### 🧠 Thinking Mode
- **Transparent Reasoning**: The AI shows its step-by-step thought process before giving answers
- **Structured Responses**: Clear separation between thinking process and final answer
- **Interactive Chat**: Real-time conversation with thinking visualization

### 🔧 Tool System
- **File Operations**: Read files with line range support
- **Directory Exploration**: List directory contents with file sizes
- **Tool Parsing**: Automatic extraction and execution of tool calls from AI responses
- **Extensible Architecture**: Easy to add new tools

### 📊 Context Monitoring
- **Token Tracking**: Real-time monitoring of context usage
- **Smart Warnings**: Alerts when approaching context limits
- **Auto-Management**: Suggestions for managing conversation history
- **Model-Specific Limits**: Support for different model context windows

### 🎯 Multiple Modes
- **Interactive Chat**: Real-time conversation mode
- **Batch Processing**: Process multiple questions in sequence
- **Context Management**: Clear history, show context stats

### Model Configuration

Edit `llm_thinking_mode.py` to configure your setup:

```python
# API Configuration
API_URL = "http://127.0.0.1:52415/v1/chat/completions"
MODEL_NAME = "llama-3.2-3b"  # Your model name

# Context Limits (tokens)
CONTEXT_LIMITS = {
    "llama-3.2-1b": 8192,      # 8K context window
    "llama-3.2-3b": 32768,     # 32K context window  
    "llama-3.2-8b": 131072,    # 128K context window
}

# Thinking Mode Settings
thinking_config = {
    "temperature": 0.7,        # Creativity level
    "top_p": 0.9,             # Vocabulary breadth
    "max_tokens": 400,        # Response length
    "presence_penalty": 0.3,   # Exploration encouragement
    "frequency_penalty": 0.2,  # Repetition avoidance
}
```


## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd llmloops
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your local LLM API:**
   - Make sure you have exo or any other compaitable local or online LLM API running on `http://127.0.0.1:52415`
   - Update the `MODEL_NAME` in `llm_thinking_mode.py` if needed

## Usage

### Interactive Chat Mode

```bash
python llm_thinking_mode.py
```

The assistant will start in interactive mode where you can:
- Ask questions and see the AI's thinking process
- Use commands like `context`, `clear`, `help`, `quit`
- Watch real-time context usage monitoring

### Available Commands

- `quit` - Exit the chat
- `context` - Show detailed context information
- `clear` - Clear conversation history
- `help` - Show available commands

### Tool Usage

The AI can automatically use tools when needed:

```
👤 You: What files are in this directory?

🤖 AI is thinking...

🧠 THINKING PROCESS:
The user wants to know what files are in the current directory. I should use the list_dir tool to explore the workspace.

💡 FINAL RESPONSE:
Let me check what files are available in the current directory.

TOOL:list_dir(relative_workspace_path=".", explanation="Exploring the workspace to see available files")
```

### Batch Processing Mode

You can also process multiple questions at once by modifying the script:

```python
# Uncomment and modify the batch section in llm_thinking_mode.py
sample_questions = [
    "What is consciousness?",
    "How should AI be regulated?", 
    "What's the meaning of existence?"
]
run_batch_thinking(sample_questions)
```



### Context File

Create a `context.md` file to provide additional context to the AI:

```markdown
# Project Context

This is a development environment for...
[Add any relevant context about your project]
```

## File Structure

```
llmloops/
├── llm_thinking_mode.py    # Main interactive chat script
├── tools.py                # Tool implementation (read_file, list_dir)
├── test_parsing.py         # Tool parsing tests
├── test_tools.py           # Tool execution tests
├── context.md              # Optional context file
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── venv/                  # Virtual environment
```

## Tools Available

### read_file
Read file contents with line range support:
```
TOOL:read_file(target_file="example.py", should_read_entire_file=false, start_line_one_indexed=1, end_line_one_indexed_inclusive=20, explanation="Reading the first 20 lines")
```

### list_dir
List directory contents with file sizes:
```
TOOL:list_dir(relative_workspace_path=".", explanation="Exploring the current directory")
```

## Testing

Run the test scripts to verify functionality:

```bash
# Test tool parsing
python test_parsing.py

# Test tool execution
python test_tools.py
```

## Context Monitoring

The system provides real-time context monitoring:

- 🟢 **OK**: Normal usage, plenty of context remaining
- 🟡 **WARNING**: Approaching context limit (80%+ used)
- 🔴 **CRITICAL**: Very close to context limit (90%+ used)

## API Compatibility

The system is designed to work with OpenAI-compatible APIs. Make sure your local LLM API supports:
- `/v1/chat/completions` endpoint
- Standard message format with `role` and `content`
- Streaming or non-streaming responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Troubleshooting

### Common Issues

1. **API Connection Error**: Ensure your LLM API is running on the correct port
2. **Context Overflow**: Use the `clear` command to reset conversation history
3. **Tool Parsing Issues**: Check that tool calls follow the exact format shown in examples
4. **File Not Found**: Ensure files exist in the workspace before reading them

### Debug Mode

Add debug prints to `llm_thinking_mode.py` to trace tool parsing and execution:

```python
# Enable debug mode
DEBUG = True
```

## Future Enhancements

- [ ] Add more tools (web search, file creation, etc.)
- [ ] Support for different AI providers
- [ ] Web interface for easier interaction
- [ ] Plugin system for custom tools
- [ ] Conversation export/import
- [ ] Advanced context management strategies
