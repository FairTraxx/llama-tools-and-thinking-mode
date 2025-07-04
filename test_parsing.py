#!/usr/bin/env python3
"""
Test script for tool parsing
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import the parsing functions
sys.path.insert(0, str(Path(__file__).parent))

from llm_thinking_mode import parse_tool_calls

def test_tool_parsing():
    """Test the tool parsing functionality"""
    
    print("🧪 Testing tool parsing...")
    print("=" * 50)
    
    # Test 1: Basic read_file call
    test_response_1 = '''
    <thinking>
    I need to read a file to answer this question.
    </thinking>
    
    I'll read the file for you.
    
    TOOL:read_file(target_file="context.md", should_read_entire_file=false, start_line_one_indexed=1, end_line_one_indexed_inclusive=10, explanation="Reading the first 10 lines of context.md")
    '''
    
    print("\n📋 Test 1: Basic read_file call")
    tool_calls = parse_tool_calls(test_response_1)
    print(f"Found {len(tool_calls)} tool calls:")
    for i, (tool_name, params) in enumerate(tool_calls):
        print(f"  {i+1}. {tool_name}: {params}")
    
    # Test 2: list_dir call
    test_response_2 = '''
    Let me explore the directory first.
    
    TOOL:list_dir(relative_workspace_path=".", explanation="Exploring the workspace to see available files")
    '''
    
    print("\n📋 Test 2: list_dir call")
    tool_calls = parse_tool_calls(test_response_2)
    print(f"Found {len(tool_calls)} tool calls:")
    for i, (tool_name, params) in enumerate(tool_calls):
        print(f"  {i+1}. {tool_name}: {params}")
    
    # Test 3: Tool calls inside code blocks (like the AI was doing)
    test_response_3 = '''
    I'll use these tools:
    
    ```python
    TOOL:list_dir(relative_workspace_path=".", explanation="Listing files")
    TOOL:read_file(target_file="tools.py", should_read_entire_file=false, start_line_one_indexed=1, end_line_one_indexed_inclusive=20, explanation="Reading tools.py header")
    ```
    '''
    
    print("\n📋 Test 3: Tool calls inside code blocks")
    tool_calls = parse_tool_calls(test_response_3)
    print(f"Found {len(tool_calls)} tool calls:")
    for i, (tool_name, params) in enumerate(tool_calls):
        print(f"  {i+1}. {tool_name}: {params}")

if __name__ == "__main__":
    test_tool_parsing()
    print("\n🎉 Tool parsing test complete!") 