import os
from typing import Tuple, Optional

class ToolResult:
    """Container for tool execution results"""
    def __init__(self, success: bool, content: str, error: Optional[str] = None):
        self.success = success
        self.content = content
        self.error = error

class Tools:
    """
    Tool implementation for the AI assistant
    Starting with read_file tool, more tools will be added incrementally
    """
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root
    
    def read_file(self, target_file: str, should_read_entire_file: bool, 
                  start_line_one_indexed: int, end_line_one_indexed_inclusive: int,
                  explanation: str) -> ToolResult:
        """
        Read the contents of a file within specified line ranges
        
        Args:
            target_file: Path to file (relative to workspace or absolute)
            should_read_entire_file: Whether to read the entire file
            start_line_one_indexed: Starting line number (1-indexed)
            end_line_one_indexed_inclusive: Ending line number (1-indexed, inclusive)
            explanation: Explanation of why this tool is being used
            
        Returns:
            ToolResult with file contents and metadata
        """
        try:
            # Handle relative vs absolute paths
            if os.path.isabs(target_file):
                file_path = target_file
            else:
                file_path = os.path.join(self.workspace_root, target_file)
            
            # Check if file exists
            if not os.path.exists(file_path):
                return ToolResult(False, "", f"File not found: {target_file}")
            
            # Read file contents
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            if should_read_entire_file:
                # Read entire file
                content = ''.join(lines)
                result_content = f"Contents of {target_file}, lines 1-{total_lines} (entire file):\n```\n{content.rstrip()}\n```"
            else:
                # Validate line numbers
                if start_line_one_indexed < 1:
                    return ToolResult(False, "", "Start line must be >= 1")
                if end_line_one_indexed_inclusive < start_line_one_indexed:
                    return ToolResult(False, "", "End line must be >= start line")
                
                # Adjust for 0-based indexing
                start_idx = start_line_one_indexed - 1
                end_idx = min(end_line_one_indexed_inclusive, total_lines)
                
                # Check if reading more than 250 lines
                lines_to_read = end_idx - start_idx
                if lines_to_read > 250:
                    return ToolResult(False, "", "Cannot read more than 250 lines at once")
                
                # Extract requested lines
                requested_lines = lines[start_idx:end_idx]
                content = ''.join(requested_lines)
                
                # Create summary of lines outside the range
                lines_before = start_line_one_indexed - 1
                lines_after = total_lines - end_line_one_indexed_inclusive
                
                summary_parts = []
                if lines_before > 0:
                    summary_parts.append(f"Lines 1-{lines_before} not shown")
                if lines_after > 0:
                    summary_parts.append(f"Lines {end_line_one_indexed_inclusive + 1}-{total_lines} not shown")
                
                summary = " | ".join(summary_parts) if summary_parts else "Complete file section shown"
                
                # Handle edge cases for display
                actual_end = min(end_line_one_indexed_inclusive, total_lines)
                if end_line_one_indexed_inclusive > total_lines:
                    result_content = f"Requested to read lines {start_line_one_indexed}-{end_line_one_indexed_inclusive}, but returning lines {start_line_one_indexed}-{total_lines} (end of file).\n"
                else:
                    result_content = f"Contents of {target_file}, lines {start_line_one_indexed}-{actual_end}:\n"
                
                result_content += f"```\n{content.rstrip()}\n```"
                
                if summary_parts:
                    result_content += f"\n\nSummary: {summary}"
            
            return ToolResult(True, result_content)
            
        except UnicodeDecodeError:
            return ToolResult(False, "", f"Cannot read file {target_file}: File contains non-UTF-8 content")
        except PermissionError:
            return ToolResult(False, "", f"Permission denied reading file: {target_file}")
        except Exception as e:
            return ToolResult(False, "", f"Error reading file {target_file}: {str(e)}")
    
    def list_dir(self, relative_workspace_path: str, explanation: str) -> ToolResult:
        """
        List the contents of a directory
        
        Args:
            relative_workspace_path: Path relative to workspace root
            explanation: Explanation of why this tool is being used
            
        Returns:
            ToolResult with directory contents
        """
        try:
            # Handle relative paths
            if relative_workspace_path == ".":
                dir_path = self.workspace_root
            else:
                dir_path = os.path.join(self.workspace_root, relative_workspace_path)
            
            # Check if directory exists
            if not os.path.exists(dir_path):
                return ToolResult(False, "", f"Directory not found: {relative_workspace_path}")
            
            if not os.path.isdir(dir_path):
                return ToolResult(False, "", f"Path is not a directory: {relative_workspace_path}")
            
            # List directory contents
            items = []
            try:
                for item in sorted(os.listdir(dir_path)):
                    item_path = os.path.join(dir_path, item)
                    if os.path.isdir(item_path):
                        items.append(f"📁 {item}/")
                    else:
                        # Get file size
                        size = os.path.getsize(item_path)
                        if size < 1024:
                            size_str = f"{size}B"
                        elif size < 1024*1024:
                            size_str = f"{size//1024}KB"
                        else:
                            size_str = f"{size//(1024*1024)}MB"
                        items.append(f"📄 {item} ({size_str})")
            except PermissionError:
                return ToolResult(False, "", f"Permission denied accessing directory: {relative_workspace_path}")
            
            if not items:
                content = f"Directory '{relative_workspace_path}' is empty."
            else:
                content = f"Contents of '{relative_workspace_path}':\n" + "\n".join(items)
            
            return ToolResult(True, content)
            
        except Exception as e:
            return ToolResult(False, "", f"Error listing directory {relative_workspace_path}: {str(e)}")

    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool by name with given parameters
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with execution outcome
        """
        if tool_name == "read_file":
            required_params = ["target_file", "should_read_entire_file", 
                             "start_line_one_indexed", "end_line_one_indexed_inclusive", "explanation"]
            
            # Check for required parameters
            missing_params = [param for param in required_params if param not in kwargs]
            if missing_params:
                return ToolResult(False, "", f"Missing required parameters: {', '.join(missing_params)}")
            
            return self.read_file(**kwargs)
        elif tool_name == "list_dir":
            required_params = ["relative_workspace_path", "explanation"]
            
            # Check for required parameters  
            missing_params = [param for param in required_params if param not in kwargs]
            if missing_params:
                return ToolResult(False, "", f"Missing required parameters: {', '.join(missing_params)}")
            
            return self.list_dir(**kwargs)
        else:
            return ToolResult(False, "", f"Unknown tool: {tool_name}")

# Convenience function for quick usage
def create_tools(workspace_root: str = ".") -> Tools:
    """Create a Tools instance with specified workspace root"""
    return Tools(workspace_root) 