# Getting Started

Get up and running with Python Interpreter MCP Server in minutes. Version 0.6.0 introduces FastMCP integration and improved package structure for better deployment and development.

## Installation

### Method 1: PyPI (Recommended)

```bash
pip install python-mcp-server
```

### Method 2: uvx (Isolated Installation)

```bash
# Install globally with uvx
uvx install python-mcp-server

# Or run directly without installation
uvx python-mcp-server --port 8000
```

### Method 3: FastMCP CLI (For Claude Desktop)

```bash
# Install and configure for Claude Desktop automatically
fastmcp install claude-desktop python-mcp-server --name "Python Interpreter"
```

### Method 4: From Source

```bash
git clone https://github.com/deadmeme5441/python-mcp-server.git
cd python-mcp-server
uv sync
```

## Quick Start

### 1. Start the Server

**Standalone Server (HTTP Mode)**
```bash
# Start HTTP server
python-mcp-server --host 127.0.0.1 --port 8000

# Custom workspace
python-mcp-server --workspace /path/to/workspace --port 8000
```

**FastMCP CLI (Recommended)**
```bash
# Run with FastMCP (auto-detects fastmcp.json)
fastmcp run

# Run with specific transport
fastmcp run --transport http --port 8000

# For development/testing
fastmcp dev
```

**From Source**
```bash
# Using the new package structure
uv run python -m python_mcp_server.server --port 8000

# Or with FastMCP
fastmcp run --transport http --port 8000
```

The server will start on `http://localhost:8000` with MCP endpoint at `/mcp`.

### 2. Connect with MCP Client (Notebook Surface)

```python
import asyncio
from fastmcp.client import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        # Run a cell
        await client.call_tool("notebook", {"action": "run", "code": "print('hello notebook')"})

        # Register Parquet files as a dataset
        await client.call_tool("notebook", {
            "action": "datasets.register",
            "dataset_name": "sales",
            "paths": ["data/sales_*.parquet"],
            "format": "parquet"
        })

        # Query with SQL (returns a small preview and saves full result to Parquet)
        res = await client.call_tool("notebook", {"action": "datasets.sql", "query": "select count(*) from sales"})
        print(res.data or res.structured_content)

asyncio.run(main())
```

### 3. Export the Notebook

```python
await client.call_tool("notebook", {"action": "export", "export_to": "ipynb"})
```

## Claude Desktop Integration

### Automatic Setup (Recommended)
```bash
# Install and configure automatically
fastmcp install claude-desktop fastmcp.json --name "Python Interpreter"
```

### Manual Setup
Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "python-interpreter": {
      "command": "python-mcp-server",
      "args": ["--workspace", "/path/to/workspace"]
    }
  }
}
```

### Alternative: Direct Python Path
```json
{
  "mcpServers": {
    "python-interpreter": {
      "command": "python", 
      "args": [
        "/path/to/src/python_mcp_server/server.py",
        "--workspace", "/path/to/workspace"
      ]
    }
  }
}
```

## Environment Setup

### Workspace Directory

The server creates a workspace with the following structure:

```
workspace/
├── scripts/     # Saved Python scripts
├── outputs/     # Generated files (plots, data, etc.)
├── uploads/     # Uploaded files via HTTP
└── (user files) # Any files created during execution
```

Set custom workspace:
```bash
export MCP_WORKSPACE_DIR="/path/to/your/workspace"
python-mcp-server --workspace /path/to/workspace
```

### FastMCP Configuration

Create a `fastmcp.json` file for advanced configuration:

```json
{
  "$schema": "https://gofastmcp.com/public/schemas/fastmcp.json/v1.json",
  "source": {
    "type": "filesystem",
    "path": "src/python_mcp_server/server.py",
    "entrypoint": "mcp"
  },
  "environment": {
    "type": "uv",
    "python": ">=3.10",
    "dependencies": [
      "fastmcp>=1.0.0",
      "jupyter_client>=8.0.0",
      "matplotlib>=3.7.0",
      "pandas>=2.0.0"
    ]
  },
  "deployment": {
    "transport": "stdio",
    "log_level": "INFO",
    "env": {
      "MCP_WORKSPACE_DIR": "workspace",
      "MPLBACKEND": "Agg",
      "PYTHONUNBUFFERED": "1"
    }
  }
}
```

Then run with:
```bash
fastmcp run  # Auto-detects fastmcp.json
```

### Python Environment

The server uses its own Python environment. Install packages dynamically:

```python
# Install packages during execution
await client.call_tool("install_dependencies", {
    "packages": ["scikit-learn", "seaborn", "plotly"]
})

# Now use them
await client.call_tool("run_python_code", {
    "code": """
import seaborn as sns
import plotly.express as px

print("Packages loaded successfully!")
"""
})
```

## Configuration Options

### Command Line Arguments

```bash
python-mcp-server \
    --port 8000 \
    --host 0.0.0.0 \
    --workspace ./custom_workspace
```

### FastMCP CLI Options

```bash
# Run with additional packages
fastmcp run --with pandas --with numpy --transport http --port 8000

# Run with custom Python version
fastmcp run --python 3.11 --transport http

# Run within project directory
fastmcp run --project /path/to/project
```

### Environment Variables

```bash
export MCP_WORKSPACE_DIR="./workspace"
export MPLBACKEND="Agg"  # For headless matplotlib
export PYTHONUNBUFFERED="1"
```

## Health Monitoring

Check server health:

```python
# Get kernel health status
health = await client.call_tool("get_kernel_health")
print("Health:", health.data)

# Check responsiveness  
responsive = await client.call_tool("check_kernel_responsiveness")
print("Responsive:", responsive.data)

# View all active sessions
sessions = await client.call_tool("list_sessions")
print("Sessions:", sessions.data)
```

## Development Workflow

### Testing Different Transports

```bash
# Test STDIO mode (for Claude Desktop)
fastmcp run --transport stdio

# Test HTTP mode (for web clients)
fastmcp run --transport http --port 8000

# Test with development server
fastmcp dev  # Includes MCP Inspector
```

### Package Development

```bash
# Install in editable mode
pip install -e .

# Run tests
uv run pytest tests/ -v

# Check linting
uvx ruff@latest check .

# Build package
uv build
```

## Next Steps

- [Tools Reference](tools.md): Complete list of available MCP tools
- [Session Management](sessions.md): Advanced session workflows
- [Architecture](architecture.md): Understanding the internal design
- [Examples](examples.md): More complex usage patterns

## Troubleshooting

### Common Issues

**CLI Command Not Found:**
```bash
# Ensure package is installed correctly
pip show python-mcp-server

# Try direct Python execution
python -m python_mcp_server.server --help

# Or use uvx
uvx python-mcp-server --help
```

**Server Won't Start:**
```bash
# Check port availability
netstat -an | grep 8000

# Try different port
python-mcp-server --port 8080

# Check FastMCP configuration
fastmcp run --transport http --port 8080
```

**Claude Desktop Integration Issues:**
```bash
# Test server directly first
python-mcp-server --workspace ./test_workspace

# Generate configuration
fastmcp install claude-desktop fastmcp.json --name "Python Test"

# Check configuration file
cat ~/.config/Claude\ Desktop/claude_desktop_config.json
```

**Import Errors:**
```bash
# Install dependencies
uv sync

# Or reinstall package
pip uninstall python-mcp-server
pip install python-mcp-server
```

**Permission Errors:**
```bash
# Check workspace permissions
ls -la workspace/
chmod 755 workspace/

# Try custom workspace
export MCP_WORKSPACE_DIR="/tmp/mcp_workspace"
python-mcp-server
```

For more help, see [Troubleshooting](troubleshooting.md).
