# Tools Reference

Complete reference for all 20 MCP tools provided by the Python MCP Server v0.6.0. These tools work seamlessly with FastMCP clients and follow MCP protocol specifications.

## Core Execution Tools

### `run_python_code`
Execute Python code in the current session's kernel.

**Parameters:**
- `code` (str): Python code to execute
- `timeout` (float, optional): Execution timeout in seconds

**Returns:**
- `stdout` (str): Standard output from execution
- `stderr` (str): Error output (if any)  
- `execution_time` (float): Time taken in seconds
- `outputs` (list): Generated output files (plots, etc.)
- `new_files` (list): New files created during execution

**Example:**
```python
result = await client.call_tool("run_python_code", {
    "code": """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave')
plt.savefig('sine_wave.png')
plt.show()

print("Plot saved as sine_wave.png")
"""
})
```

### `code_completion`
Get intelligent code completions using IPython.

**Parameters:**
- `code` (str): Code context for completion
- `cursor_pos` (int): Cursor position in the code

**Returns:**
- `matches` (list): List of completion suggestions
- `cursor_start` (int): Start position for replacement
- `cursor_end` (int): End position for replacement

**Example:**
```python
result = await client.call_tool("code_completion", {
    "code": "import numpy as np\nnp.lin",
    "cursor_pos": 23
})
# Returns matches like ['linspace', 'linalg', ...]
```

### `inspect_object`
Inspect Python objects for detailed information.

**Parameters:**
- `code` (str): Object/expression to inspect
- `cursor_pos` (int): Position in the code
- `detail_level` (int, optional): 0=signature, 1=full details

**Returns:**
- `found` (bool): Whether object was found
- `data` (dict): Inspection results (signature, docstring, source, etc.)

**Example:**
```python
result = await client.call_tool("inspect_object", {
    "code": "numpy.linspace",
    "cursor_pos": 13,
    "detail_level": 1
})
```

### `restart_kernel`
Restart the current session's kernel.

**Parameters:** None

**Returns:**
- `restarted` (bool): Whether restart was successful
- `session_id` (str): ID of restarted session

**Example:**
```python
result = await client.call_tool("restart_kernel")
# All variables and imports are lost after restart
```

## File System Tools

### `list_files`
List files and directories in the workspace.

**Parameters:**
- `path` (str, optional): Directory to list (default: workspace root)
- `recursive` (bool, optional): Include subdirectories  
- `tree` (bool, optional): Show as tree structure
- `max_depth` (int, optional): Maximum recursion depth

**Returns:**
- `files` (list): List of file paths
- `tree` (str): Tree representation (if requested)

**Example:**
```python
result = await client.call_tool("list_files", {
    "path": "outputs",
    "recursive": True,
    "tree": True,
    "max_depth": 3
})
```

### `read_file`
Read contents of a file.

**Parameters:**
- `path` (str): File path relative to workspace

**Returns:**
- `text` (str): File contents
- `binary` (bool): Whether file was read as binary
- `encoding` (str): Character encoding used

**Example:**
```python
result = await client.call_tool("read_file", {
    "path": "data/results.csv"
})
content = result.data["text"]
```

### `write_file`
Write content to a file.

**Parameters:**
- `path` (str): File path relative to workspace
- `content` (str): Content to write
- `encoding` (str, optional): Character encoding (default: utf-8)

**Returns:**
- `path` (str): Full path where file was written
- `size` (int): Size of written file in bytes

**Example:**
```python
await client.call_tool("write_file", {
    "path": "results/analysis.txt", 
    "content": "Analysis complete\nAccuracy: 95.2%"
})
```

### `delete_file`
Delete a file or directory.

**Parameters:**
- `path` (str): Path to delete

**Returns:**
- `deleted` (bool): Whether deletion was successful
- `path` (str): Path that was deleted

**Example:**
```python
await client.call_tool("delete_file", {
    "path": "temp/old_results.csv"
})
```

## Script Management Tools

### `save_script`
Save Python code as a script file.

**Parameters:**
- `name` (str): Script name (without .py extension)
- `content` (str): Python code content

**Returns:**
- `script` (str): Relative path to saved script
- `full_path` (str): Absolute path to script

**Example:**
```python
await client.call_tool("save_script", {
    "name": "data_processor",
    "content": """
import pandas as pd

def process_data(filename):
    df = pd.read_csv(filename)
    return df.describe()

if __name__ == "__main__":
    result = process_data("data.csv")  
    print(result)
"""
})
```

### `run_script`
Execute a saved Python script.

**Parameters:**
- `path` (str): Path to script file (relative to workspace)

**Returns:**
- `returncode` (int): Script exit code (0 = success)
- `stdout` (str): Standard output
- `stderr` (str): Error output
- `execution_time` (float): Time taken in seconds
- `new_files` (list): Files created by script

**Example:**
```python
result = await client.call_tool("run_script", {
    "path": "scripts/data_processor.py"
})
```

## Package Management Tools

### `install_dependencies`
Install Python packages using pip.

**Parameters:**
- `packages` (list): List of package specifications

**Returns:**
- `returncode` (int): Installation exit code
- `stdout` (str): Installation output
- `stderr` (str): Error messages (if any)
- `installed_packages` (list): Successfully installed packages

**Example:**
```python
await client.call_tool("install_dependencies", {
    "packages": ["pandas>=1.5.0", "scikit-learn", "plotly"]
})
```

### `list_variables`
List all variables in the current kernel session.

**Parameters:** None

**Returns:**
- `variables` (dict): Variable names and their types/representations

**Example:**
```python
result = await client.call_tool("list_variables")
# Returns: {"x": "int: 42", "df": "DataFrame: (100, 5)", ...}
```

## Session Management Tools

### `create_session`
Create a new isolated kernel session.

**Parameters:**
- `session_id` (str): Unique identifier for the session
- `description` (str, optional): Session description

**Returns:**
- `session_id` (str): Created session ID
- `status` (str): Creation status
- `description` (str): Session description

**Example:**
```python
await client.call_tool("create_session", {
    "session_id": "ml_experiment",
    "description": "Machine learning model training"
})
```

### `switch_session`
Switch to a different kernel session.

**Parameters:**
- `session_id` (str): Session ID to switch to

**Returns:**
- `previous_session` (str): Previous active session
- `current_session` (str): New active session

**Example:**
```python
await client.call_tool("switch_session", {
    "session_id": "ml_experiment"
})
```

### `list_sessions`
List all available kernel sessions.

**Parameters:** None

**Returns:**
- `sessions` (dict): Session details keyed by session ID
- `active_session` (str): Currently active session
- `total_sessions` (int): Total number of sessions

**Example:**
```python
result = await client.call_tool("list_sessions")
print(f"Active: {result.data['active_session']}")
print(f"Available: {list(result.data['sessions'].keys())}")
```

### `delete_session`
Delete a kernel session and clean up resources.

**Parameters:**
- `session_id` (str): Session ID to delete

**Returns:**
- `session_id` (str): Deleted session ID
- `status` (str): Deletion status

**Example:**
```python
await client.call_tool("delete_session", {
    "session_id": "old_experiment"
})
```

## Health Monitoring Tools

### `get_kernel_health`
Get comprehensive health information for the current kernel.

**Parameters:** None

**Returns:**
- `status` (str): Health status (healthy/dead/zombie)
- `pid` (int): Process ID (if alive)
- `memory_usage` (int): Memory usage in bytes
- `cpu_percent` (float): CPU usage percentage
- `num_threads` (int): Number of threads
- `uptime` (float): Uptime in seconds

**Example:**
```python
health = await client.call_tool("get_kernel_health")
if health.data["status"] != "healthy":
    await client.call_tool("restart_kernel")
```

### `check_kernel_responsiveness`
Test if the kernel responds to simple operations.

**Parameters:** None

**Returns:**
- `responsive` (bool): Whether kernel responded
- `response_time` (float): Response time in seconds
- `test_result` (str): Result of test operation

**Example:**
```python
check = await client.call_tool("check_kernel_responsiveness")
if not check.data["responsive"]:
    print("Kernel is unresponsive, consider restarting")
```

## Utility Tools

### `ping`
Simple connectivity test.

**Parameters:** None

**Returns:**
- `status` (str): Always "pong"
- `timestamp` (str): Current timestamp

**Example:**
```python
result = await client.call_tool("ping")
# Returns: {"status": "pong", "timestamp": "2024-01-15T10:30:45Z"}
```

### `get_workspace_info`
Get information about the current workspace.

**Parameters:** None

**Returns:**
- `workspace_dir` (str): Workspace directory path
- `scripts_dir` (str): Scripts directory path
- `outputs_dir` (str): Outputs directory path  
- `uploads_dir` (str): Uploads directory path

**Example:**
```python
info = await client.call_tool("get_workspace_info")
print(f"Workspace: {info.data['workspace_dir']}")
```

## Usage Patterns

### Error Handling
All tools raise `ToolError` exceptions for user-facing errors:

```python
try:
    result = await client.call_tool("run_python_code", {
        "code": "invalid syntax!"
    })
except ToolError as e:
    print(f"Execution failed: {e}")
```

### Async Operations
Most tools support timeout parameters for long-running operations:

```python
# Long-running analysis with custom timeout
result = await client.call_tool("run_python_code", {
    "code": "# Complex analysis code here",
    "timeout": 300.0  # 5 minutes
})
```

### File Output Handling
Many tools track generated files automatically:

```python
result = await client.call_tool("run_python_code", {
    "code": """
import matplotlib.pyplot as plt
plt.plot([1,2,3], [4,5,6])
plt.savefig('plot.png')
"""
})

# Check what files were created
print("Generated files:", result.data.get("outputs", []))
```