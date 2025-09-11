# Tools Reference (v0.7+)

This server exposes a small, agent-friendly surface optimized for data analysis.

## Notebook (single surface)

`notebook(action=..., ...)` — one tool that handles cells, datasets, and export.

- Actions
  - `run`: Execute a code cell. Captures stdout, stderr, figures (PNG/SVG), JSON displays, and a workspace diff. Writes a per‑cell manifest to `outputs/notebooks/<id>/` and updates `index.json`.
  - `cells`: List executed cells (from index.json).
  - `cell`: Fetch a single cell’s manifest.
  - `export`: Emit `.ipynb` (and `.html` if nbconvert is available) for handoff.
  - `reset`: Clear manifests/counters for the same `notebook_id` (kernel not restarted).
  - `datasets.register`: Create/update a DuckDB VIEW over CSV/Parquet files (paths or globs). Uses DuckDB’s Python engine safely (quoted literals).
  - `datasets.list`: Show registered datasets and backing paths.
  - `datasets.describe`: Return schema + head(50).
  - `datasets.drop`: Remove a VIEW and its registry entry.
  - `datasets.sql`: Run SQL across registered views; returns a JSON preview and writes the full result to `outputs/data/<id>/*.parquet`.

## Core Execution

- `run_python_code`: Execute Python code with rich-display capture. Saves figures to `outputs/` and returns artifact paths.
- `restart_kernel`: Restart the active kernel; optional state preservation.

## Files

- `list_files`: Flat or tree view of the workspace. Supports recursion and depth limits.
- `read_file` / `write_file` / `delete_file`: Safe, sandboxed file operations.

## Packages

- `install_dependencies`: Install packages into the current interpreter/venv. Prefers `uv`, falls back to `python -m pip`.
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
