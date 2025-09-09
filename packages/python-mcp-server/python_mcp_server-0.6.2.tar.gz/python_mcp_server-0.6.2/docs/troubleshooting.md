# Troubleshooting

Common issues and solutions when using the Python MCP Server v0.6.0 with FastMCP integration.

## Installation Issues

### Package Installation Fails
**Problem:** `pip install python-mcp-server` fails

**Solutions:**
```bash
# Update pip and try again
python -m pip install --upgrade pip
pip install python-mcp-server

# Use uvx for isolated installation
uvx install python-mcp-server

# Use FastMCP CLI for Claude Desktop
fastmcp install claude-desktop python-mcp-server

# Install from source if PyPI fails
git clone https://github.com/deadmeme5441/python-mcp-server.git
cd python-mcp-server
uv sync
```

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'python_mcp_server'`

**Solutions:**
```bash
# Ensure proper installation
pip show python-mcp-server

# Reinstall if needed
pip uninstall python-mcp-server
pip install python-mcp-server

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Test CLI command
python-mcp-server --help
```

## Server Startup Issues

### Port Already in Use
**Problem:** `OSError: [Errno 98] Address already in use`

**Solutions:**
```bash
# Check what's using the port
netstat -an | grep 8000
lsof -i :8000

# Use different port
python-mcp-server --port 8080
# Or with FastMCP
fastmcp run --transport http --port 8080

# Kill process using the port
kill $(lsof -ti:8000)
```

### Permission Denied
**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solutions:**
```bash
# Check workspace permissions
ls -la workspace/
chmod 755 workspace/

# Set environment variable for custom workspace
export MCP_WORKSPACE_DIR="/tmp/mcp_workspace"
python-mcp-server --workspace /tmp/mcp_workspace --port 8000

# Or with FastMCP
fastmcp run --transport http --port 8000

# Run with different user (if needed)
sudo -u username python-mcp-server --port 8000
```

### Dependencies Missing
**Problem:** Server fails to start with import errors

**Solutions:**
```bash
# Install all dependencies
uv sync

# Check requirements
cat pyproject.toml

# Install specific missing packages
pip install fastmcp jupyter-client matplotlib

# Verify installation
python -c "import fastmcp, jupyter_client, matplotlib; print('All imports successful')"
```

## Connection Issues

### Client Can't Connect
**Problem:** `ConnectionError: Could not connect to MCP server`

**Solutions:**
```python
# Check if server is running
import requests
try:
    response = requests.get("http://localhost:8000/docs")
    print(f"Server status: {response.status_code}")
except requests.ConnectionError:
    print("Server not running")

# Verify MCP endpoint
try:
    response = requests.post("http://localhost:8000/mcp", json={
        "jsonrpc": "2.0",
        "method": "ping",
        "id": 1
    })
    print(f"MCP endpoint: {response.status_code}")
except Exception as e:
    print(f"MCP error: {e}")
```

**Debugging steps:**
```bash
# Check server logs
python-mcp-server --port 8000
# Or with FastMCP debug mode
fastmcp dev

# Test with curl
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"ping","arguments":{}},"id":1}'

# Check firewall settings
sudo ufw status
```

### Timeout Errors
**Problem:** `TimeoutError: Tool call timed out`

**Solutions:**
```python
# Increase timeout for long operations
result = await client.call_tool("run_python_code", {
    "code": "# Long running operation",
    "timeout": 300  # 5 minutes
})

# Check if kernel is responsive
health = await client.call_tool("get_kernel_health")
if health.data["status"] != "healthy":
    await client.call_tool("restart_kernel")
```

## Kernel Issues

### Kernel Won't Start
**Problem:** Jupyter kernel fails to start

**Solutions:**
```bash
# Check Jupyter installation
jupyter --version
jupyter kernelspec list

# Install/reinstall kernel
python -m ipykernel install --user

# Clear Jupyter cache
jupyter --paths
rm -rf ~/.jupyter/runtime/*

# Test kernel manually
python -m jupyter_client.kernelspecmanager --debug
```

### Kernel Becomes Unresponsive
**Problem:** Code execution hangs or times out

**Solutions:**
```python
# Check kernel responsiveness
responsive = await client.call_tool("check_kernel_responsiveness")
if not responsive.data["responsive"]:
    print("Kernel unresponsive, restarting...")
    await client.call_tool("restart_kernel")

# Monitor kernel health
health = await client.call_tool("get_kernel_health")
print(f"Status: {health.data['status']}")
print(f"Memory: {health.data.get('memory_usage', 0) / 1024**2:.1f} MB")
```

### Memory Issues
**Problem:** High memory usage or out-of-memory errors

**Solutions:**
```python
# Check memory usage
health = await client.call_tool("get_kernel_health")
memory_mb = health.data.get("memory_usage", 0) / (1024**2)
print(f"Memory usage: {memory_mb:.1f} MB")

# Clean up variables
await client.call_tool("run_python_code", {
    "code": """
import gc
# Delete large variables
# del large_dataframe, big_array
gc.collect()
print("Memory cleaned up")
"""
})

# Restart kernel if needed
if memory_mb > 1000:  # 1GB threshold
    await client.call_tool("restart_kernel")
```

## File System Issues

### Path Errors
**Problem:** `ToolError: Path is outside workspace`

**Solutions:**
```python
# Use relative paths within workspace
await client.call_tool("write_file", {
    "path": "data/results.csv",  # Good
    # path": "../outside/file.txt"  # Bad - outside workspace
    "content": "..."
})

# Check workspace info
info = await client.call_tool("get_workspace_info")
print(f"Workspace: {info.data['workspace_dir']}")
```

### File Permission Errors
**Problem:** Cannot read/write files

**Solutions:**
```bash
# Check workspace permissions
ls -la workspace/
chmod -R 755 workspace/

# Change ownership if needed
sudo chown -R username:username workspace/

# Set environment variable
export MCP_WORKSPACE_DIR="/path/with/proper/permissions"
```

### File Not Found
**Problem:** Files created in code not visible

**Solutions:**
```python
# List files to debug
files = await client.call_tool("list_files", {"recursive": True})
print("Available files:", files.data["files"])

# Check outputs directory
outputs = await client.call_tool("list_files", {"path": "outputs"})
print("Output files:", outputs.data["files"])

# Ensure proper file paths in code
await client.call_tool("run_python_code", {
    "code": """
from pathlib import Path
import os

# Check current directory
print("Current dir:", os.getcwd())

# Create file with absolute path
output_path = Path("outputs/my_file.txt")
output_path.parent.mkdir(exist_ok=True)
output_path.write_text("Hello World")

print(f"File created: {output_path.exists()}")
"""
})
```

## Session Management Issues

### Session Creation Fails
**Problem:** Cannot create new sessions

**Solutions:**
```python
# Check existing sessions
sessions = await client.call_tool("list_sessions")
print(f"Current sessions: {list(sessions.data['sessions'].keys())}")

# Ensure unique session IDs
import uuid
session_id = f"session_{uuid.uuid4().hex[:8]}"
await client.call_tool("create_session", {"session_id": session_id})

# Clean up old sessions if too many
if len(sessions.data["sessions"]) > 10:
    for old_session in list(sessions.data["sessions"].keys())[:-5]:
        if old_session != "default":
            await client.call_tool("delete_session", {"session_id": old_session})
```

### Session Switch Fails
**Problem:** Cannot switch between sessions

**Solutions:**
```python
# Verify session exists
sessions = await client.call_tool("list_sessions")
target_session = "my_session"

if target_session not in sessions.data["sessions"]:
    print(f"Session {target_session} not found")
    await client.call_tool("create_session", {"session_id": target_session})

# Then switch
await client.call_tool("switch_session", {"session_id": target_session})
```

## Package Installation Issues

### pip/uv Installation Fails
**Problem:** `install_dependencies` tool fails

**Solutions:**
```python
# Check error details
try:
    result = await client.call_tool("install_dependencies", {
        "packages": ["problematic-package"]
    })
except Exception as e:
    print(f"Installation error: {e}")

# Install with specific versions
await client.call_tool("install_dependencies", {
    "packages": ["pandas==1.5.0", "numpy>=1.20.0"]
})

# Use pip directly if uv fails
await client.call_tool("run_python_code", {
    "code": """
import subprocess
import sys

result = subprocess.run([
    sys.executable, "-m", "pip", "install", "package-name"
], capture_output=True, text=True)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
"""
})
```

### Import Errors After Installation
**Problem:** Packages install but can't be imported

**Solutions:**
```python
# Restart kernel after installation
await client.call_tool("install_dependencies", {"packages": ["new-package"]})
await client.call_tool("restart_kernel")

# Check if package is actually installed
await client.call_tool("run_python_code", {
    "code": """
import subprocess
import sys

result = subprocess.run([
    sys.executable, "-m", "pip", "list"
], capture_output=True, text=True)

print("Installed packages:")
print(result.stdout)
"""
})
```

## Performance Issues

### Slow Execution
**Problem:** Code takes too long to execute

**Solutions:**
```python
# Monitor execution time
import time
start = time.time()

result = await client.call_tool("run_python_code", {
    "code": "# Your code here"
})

duration = time.time() - start
print(f"Execution took {duration:.2f} seconds")

# Profile code performance
await client.call_tool("run_python_code", {
    "code": """
import cProfile
import pstats

def your_function():
    # Your code here
    pass

# Profile the function
profiler = cProfile.Profile()
profiler.enable()
your_function()
profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)
"""
})
```

### High CPU Usage
**Problem:** Kernel consuming too much CPU

**Solutions:**
```python
# Monitor CPU usage
health = await client.call_tool("get_kernel_health")
cpu_percent = health.data.get("cpu_percent", 0)

if cpu_percent > 80:
    print(f"High CPU usage: {cpu_percent}%")
    # Consider optimizing code or restarting kernel
    
# Check for infinite loops
await client.call_tool("run_python_code", {
    "code": """
import signal
import sys

def timeout_handler(signum, frame):
    print("Code execution timeout - possible infinite loop")
    sys.exit(1)

# Set timeout for debugging
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)  # 10 second timeout

# Your potentially problematic code here
try:
    # risky_code()
    pass
finally:
    signal.alarm(0)  # Disable timeout
"""
})
```

## Development & Debugging

### Enable Debug Logging
```bash
# Server debug mode with FastMCP
fastmcp dev  # Includes debug logging and MCP Inspector

# Or manual server startup
python-mcp-server --port 8000

# Client debug mode
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Server Health
```python
async def debug_server_health():
    async with Client("http://localhost:8000/mcp") as client:
        # Test basic connectivity
        ping = await client.call_tool("ping")
        print(f"Ping: {ping.data}")
        
        # Check kernel health
        health = await client.call_tool("get_kernel_health")
        print(f"Kernel health: {health.data}")
        
        # Test responsiveness
        responsive = await client.call_tool("check_kernel_responsiveness")
        print(f"Responsive: {responsive.data}")
        
        # List sessions
        sessions = await client.call_tool("list_sessions")
        print(f"Sessions: {sessions.data}")

asyncio.run(debug_server_health())
```

### Common Error Patterns

#### Tool Not Found
```json
{
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```
**Solution:** Check tool name spelling and server version

#### Invalid Parameters
```json
{
  "error": {
    "code": -32602,
    "message": "Invalid params"
  }
}
```
**Solution:** Verify parameter names and types match tool signature

#### Execution Timeout
```json
{
  "error": {
    "code": -32000,
    "message": "Internal error: Code execution timeout"
  }
}
```
**Solution:** Increase timeout or optimize code

## Getting Help

### Check Server Logs
```bash
# View real-time logs
tail -f /var/log/mcp-server.log

# Search for specific errors
grep -i "error" /var/log/mcp-server.log
```

### Report Issues
When reporting issues, include:

1. Server version: `python-mcp-server --version` or `pip show python-mcp-server`
2. Python version: `python --version`
3. FastMCP version: `fastmcp --version`
4. Operating system and version
5. Full error message and stack trace
6. Minimal reproduction code
7. Server logs (with sensitive data removed)
8. FastMCP configuration (`fastmcp.json` if used)

### Community Support
- **GitHub Issues**: [github.com/deadmeme5441/python-mcp-server/issues](https://github.com/deadmeme5441/python-mcp-server/issues)
- **Documentation**: [deadmeme5441.github.io/python-mcp-server](https://deadmeme5441.github.io/python-mcp-server)
- **Examples**: See [examples.md](examples.md) for working code patterns

Most issues can be resolved by checking logs, verifying installation, and ensuring proper configuration. When in doubt, restart the server and kernel to clear any transient issues.