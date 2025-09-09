# Getting Started

Get up and running with Python Interpreter MCP Server in minutes.

## Installation

### From PyPI (Recommended)

```bash
pip install python-mcp-server
```

### From Source

```bash
git clone https://github.com/deadmeme5441/python-mcp-server.git
cd python-mcp-server
uv sync
```

## Quick Start

### 1. Start the Server

```bash
# Using the installed package
python-mcp-server --port 8000

# Or from source
python main.py --port 8000
```

The server will start on `http://localhost:8000` with MCP endpoint at `/mcp`.

### 2. Connect with MCP Client

```python
import asyncio
from fastmcp.client import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        # Execute simple Python code
        result = await client.call_tool("run_python_code", {
            "code": """
import numpy as np
import matplotlib.pyplot as plt

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('sin(X)')
plt.grid(True)
plt.show()

print("Plot created successfully!")
"""
        })
        
        print("Execution result:", result.data)

asyncio.run(main())
```

### 3. Work with Sessions

```python
async def session_example():
    async with Client("http://localhost:8000/mcp") as client:
        # Create a new session for data analysis
        await client.call_tool("create_session", {
            "session_id": "data_analysis",
            "description": "Data science workflow"
        })
        
        # Switch to the new session
        await client.call_tool("switch_session", {
            "session_id": "data_analysis"
        })
        
        # Set up data analysis environment
        await client.call_tool("run_python_code", {
            "code": """
import pandas as pd
import numpy as np

# Create sample dataset
data = {
    'x': np.random.randn(1000),
    'y': np.random.randn(1000) * 2 + 1,
    'category': np.random.choice(['A', 'B', 'C'], 1000)
}
df = pd.DataFrame(data)

print(f"Dataset shape: {df.shape}")
print(df.head())
"""
        })
        
        # In a separate session, variables are isolated
        await client.call_tool("create_session", {
            "session_id": "modeling"
        })
        
        await client.call_tool("switch_session", {
            "session_id": "modeling"
        })
        
        # This will fail - df doesn't exist in this session
        result = await client.call_tool("run_python_code", {
            "code": "print('df' in globals())"  # Will print False
        })

asyncio.run(session_example())
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
python main.py --port 8000
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
python main.py \
    --port 8000 \
    --host 0.0.0.0 \
    --workspace-dir ./custom_workspace \
    --log-level INFO
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
```

## Next Steps

- [Tools Reference](tools.md): Complete list of available MCP tools
- [Session Management](sessions.md): Advanced session workflows
- [Architecture](architecture.md): Understanding the internal design
- [Examples](examples.md): More complex usage patterns

## Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check port availability
netstat -an | grep 8000

# Try different port
python main.py --port 8080
```

**Import errors:**
```bash
# Install missing dependencies
uv sync
# or
pip install -r requirements.txt
```

**Permission errors:**
```bash
# Check workspace permissions
ls -la workspace/
chmod 755 workspace/
```

For more help, see [Troubleshooting](troubleshooting.md).