#!/usr/bin/env python3
"""
Test script for the tools integration
Tests the read_file tool functionality
"""

import os
from pathlib import Path
from tools import create_tools

# Dynamic workspace detection - use the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
WORKSPACE_ROOT = str(SCRIPT_DIR)

def test_read_file():
    """Test the read_file tool with various scenarios"""
    tools = create_tools(WORKSPACE_ROOT)
    
    print(f"🧪 Testing read_file tool...")
    print(f"📁 Workspace: {WORKSPACE_ROOT}")
    print("=" * 50)
    
    # Test 1: Read entire file
    print("\n📋 Test 1: Reading entire context.md file")
    result = tools.read_file(
        target_file="context.md",
        should_read_entire_file=True,
        start_line_one_indexed=1,
        end_line_one_indexed_inclusive=100,
        explanation="Testing reading entire file"
    )
    
    if result.success:
        print("✅ Success!")
        print(result.content[:200] + "..." if len(result.content) > 200 else result.content)
    else:
        print(f"❌ Failed: {result.error}")
    
    # Test 2: Read specific lines
    print("\n📋 Test 2: Reading lines 1-10 of context.md")
    result = tools.read_file(
        target_file="context.md",
        should_read_entire_file=False,
        start_line_one_indexed=1,
        end_line_one_indexed_inclusive=10,
        explanation="Testing reading specific line range"
    )
    
    if result.success:
        print("✅ Success!")
        print(result.content)
    else:
        print(f"❌ Failed: {result.error}")
    
    # Test 3: Read non-existent file
    print("\n📋 Test 3: Reading non-existent file")
    result = tools.read_file(
        target_file="nonexistent.txt",
        should_read_entire_file=False,
        start_line_one_indexed=1,
        end_line_one_indexed_inclusive=10,
        explanation="Testing file not found error"
    )
    
    if result.success:
        print("✅ Success!")
        print(result.content)
    else:
        print(f"❌ Expected failure: {result.error}")
    
    # Test 4: Using execute_tool method
    print("\n📋 Test 4: Using execute_tool method")
    result = tools.execute_tool(
        "read_file",
        target_file="tools.py",
        should_read_entire_file=False,
        start_line_one_indexed=1,
        end_line_one_indexed_inclusive=5,
        explanation="Testing execute_tool method"
    )
    
    if result.success:
        print("✅ Success!")
        print(result.content)
    else:
        print(f"❌ Failed: {result.error}")

if __name__ == "__main__":
    test_read_file()
    print("\n🎉 Tool testing complete!") 