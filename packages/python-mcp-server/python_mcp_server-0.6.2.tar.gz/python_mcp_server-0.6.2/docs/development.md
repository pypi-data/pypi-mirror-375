# Development Guide

Contributing to and extending the Python MCP Server v0.6.0 with FastMCP integration.

## Development Setup

### Prerequisites
- Python 3.10+
- uv package manager
- Git
- FastMCP CLI (optional but recommended)

### Getting Started
```bash
# Clone the repository
git clone https://github.com/deadmeme5441/python-mcp-server.git
cd python-mcp-server

# Install dependencies with uv
uv sync

# Run tests
uv run pytest tests/ -v

# Start development server
python-mcp-server --port 8000

# Or use FastMCP for development (recommended)
fastmcp dev  # Includes MCP Inspector and debug logging
```

### v0.6.0 Project Structure
```
python-mcp-server/
├── src/
│   └── python_mcp_server/
│       ├── __init__.py         # Package initialization
│       └── server.py           # Main FastMCP server
├── tests/
│   ├── test_server.py          # Integration tests
│   ├── test_sessions.py        # Session management tests
│   └── unit/
│       └── test_core_helpers.py
├── docs/                       # MkDocs documentation
├── fastmcp.json               # FastMCP configuration
├── pyproject.toml             # Project metadata (hatchling)
├── mkdocs.yml                 # Documentation config
├── main.py.backup             # Backed up original entry point
└── CLAUDE.md                  # Development notes
```

## Architecture Components

### Core Classes

#### SessionManager
```python
class SessionManager:
    """Manages multiple isolated kernel sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, KernelSession] = {}
        self.current_session = "default"
    
    async def create_session(self, session_id: str, description: Optional[str] = None):
        """Create new kernel session with isolation"""
        
    async def cleanup_session(self, session_id: str):
        """Properly shutdown session resources"""
```

#### KernelSession
```python
@dataclass
class KernelSession:
    """Represents an isolated Python kernel"""
    session_id: str
    kernel_manager: AsyncKernelManager
    kernel_client: AsyncKernelClient
    created_at: datetime
    last_activity: datetime
    description: Optional[str] = None
```

### Middleware Stack
The server uses FastMCP middleware for production features:

```python
# Initialize FastMCP with middleware (v0.6.0)
mcp = FastMCP(
    name="python-mcp-server",
    version="0.6.0",
    description="World-class Python interpreter with session management"
)

# Middleware is automatically configured by FastMCP
```

## Adding New Tools

### Tool Structure
All MCP tools follow this pattern:

```python
@mcp.tool()
async def my_new_tool(
    required_param: str,
    optional_param: Optional[int] = None,
    ctx: Context = Depends(get_context)  # Always last
) -> Dict[str, Any]:
    """Tool description for MCP introspection
    
    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter
        
    Returns:
        Dictionary with tool results
    """
    
    # 1. Log the operation
    ctx.logger.info(f"Executing my_new_tool with {required_param}")
    
    # 2. Validate inputs (Pydantic handles this automatically)
    
    # 3. Get current session
    session = await session_manager.get_session(session_manager.current_session)
    
    # 4. Perform operation with error handling
    try:
        result = await perform_operation(required_param, optional_param)
    except Exception as e:
        raise ToolError(f"Operation failed: {str(e)}")
    
    # 5. Return structured response
    return {
        "status": "success",
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
```

### Example: Adding a Data Visualization Tool
```python
@mcp.tool()
async def create_plot(
    data_source: str,
    plot_type: str = "line",
    title: Optional[str] = None,
    ctx: Context = Depends(get_context)
) -> Dict[str, Any]:
    """Create data visualization from various sources
    
    Args:
        data_source: Path to data file or Python variable name
        plot_type: Type of plot (line, scatter, bar, histogram)
        title: Optional plot title
        
    Returns:
        Dictionary with plot file path and metadata
    """
    ctx.logger.info(f"Creating {plot_type} plot from {data_source}")
    
    session = await session_manager.get_session(session_manager.current_session)
    
    # Generate plotting code
    plot_code = f"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Load data
if Path('{data_source}').exists():
    if '{data_source}'.endswith('.csv'):
        data = pd.read_csv('{data_source}')
    elif '{data_source}'.endswith('.json'):
        data = pd.read_json('{data_source}')
else:
    # Assume it's a variable name
    data = globals()['{data_source}']

# Create plot
plt.figure(figsize=(10, 6))

if '{plot_type}' == 'line':
    plt.plot(data.iloc[:, 0], data.iloc[:, 1])
elif '{plot_type}' == 'scatter':
    plt.scatter(data.iloc[:, 0], data.iloc[:, 1])
elif '{plot_type}' == 'bar':
    plt.bar(range(len(data)), data.iloc[:, 0])
elif '{plot_type}' == 'histogram':
    plt.hist(data.iloc[:, 0], bins=30)

if '{title}':
    plt.title('{title}')

# Save plot
import uuid
filename = f"plot_{{uuid.uuid4().hex[:8]}}.png"
plt.savefig(f"outputs/{{filename}}")
plt.close()

print(f"Plot saved as {{filename}}")
"""
    
    try:
        # Execute plotting code
        result = await _execute_code(session, plot_code, timeout=30.0)
        
        # Extract filename from output
        output_lines = result.get('stdout', '').strip().split('\n')
        filename = None
        for line in output_lines:
            if 'Plot saved as' in line:
                filename = line.split('Plot saved as ')[-1]
                break
        
        if not filename:
            raise ToolError("Failed to extract plot filename")
        
        return {
            "status": "success", 
            "plot_file": f"outputs/{filename}",
            "plot_type": plot_type,
            "data_source": data_source,
            "title": title
        }
        
    except Exception as e:
        raise ToolError(f"Plot creation failed: {str(e)}")
```

## Testing

### Test Structure
```python
# tests/test_new_feature.py
import asyncio
from fastmcp.client import Client

def test_new_feature(mcp_url: str):
    """Test new feature functionality"""
    async def run():
        async with Client(mcp_url) as client:
            # Test the new tool
            result = await client.call_tool("my_new_tool", {
                "required_param": "test_value"
            })
            
            # Verify results
            assert result.data["status"] == "success"
            
    asyncio.run(run())
```

### Running Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_server.py -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### Test Categories
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test tool interactions with kernels
- **Session Tests**: Test session management and isolation
- **Health Tests**: Test monitoring and recovery systems

## Code Style

### Formatting
```bash
# Format code with black
uv run black src/ tests/ main.py

# Sort imports
uv run isort src/ tests/ main.py

# Type checking
uv run mypy src/ main.py
```

### Code Standards
- Use type hints for all function parameters and returns
- Follow PEP 8 style guidelines
- Write docstrings for all public functions and classes
- Use async/await for all I/O operations
- Handle errors gracefully with proper exception types

## Debugging

### Local Development
```bash
# Use FastMCP dev mode (recommended)
fastmcp dev  # Includes debug logging, MCP Inspector, and hot reload

# Manual server startup
python-mcp-server --port 8000

# Test different transports
fastmcp run --transport http --port 8000
fastmcp run --transport stdio  # For Claude Desktop testing
```

### Common Issues

#### Kernel Connection Problems
```python
# Check kernel status
health = await client.call_tool("get_kernel_health")
print(f"Kernel status: {health.data}")

# Restart if needed
if health.data['status'] != 'healthy':
    await client.call_tool("restart_kernel")
```

#### Memory Leaks
```python
# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024**2:.1f} MB")

# Force garbage collection
import gc
collected = gc.collect()
print(f"Collected {collected} objects")
```

## Performance Profiling

### Execution Timing
```python
import time
start = time.time()
result = await client.call_tool("run_python_code", {"code": "..."})
duration = time.time() - start
print(f"Execution took {duration:.3f} seconds")
```

### Memory Profiling
```python
# Use memory_profiler for detailed analysis
@profile
def memory_intensive_function():
    # Your code here
    pass
```

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

EXPOSE 8000
CMD ["python-mcp-server", "--port", "8000", "--host", "0.0.0.0"]
```

### FastMCP Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

# Install FastMCP and dependencies
RUN pip install fastmcp uv
RUN uv sync

EXPOSE 8000

# Use FastMCP for production deployment
CMD ["fastmcp", "run", "--transport", "http", "--port", "8000", "--host", "0.0.0.0"]
```

### Production Configuration
```python
# Production settings
export MCP_WORKSPACE_DIR="/data/workspace"
export PYTHONUNBUFFERED=1
export MPLBACKEND=Agg

# Resource limits
export KERNEL_MEMORY_LIMIT=1GB
export MAX_CONCURRENT_SESSIONS=20
export EXECUTION_TIMEOUT=300
```

## Contributing

### Pull Request Process
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-tool`
3. Make changes with tests
4. Ensure all tests pass: `uv run pytest`
5. Format code: `uv run black . && uv run isort .`
6. Submit pull request

### Code Review Checklist
- [ ] All tests pass
- [ ] Code is properly formatted
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Error handling is appropriate
- [ ] Performance impact is considered

### Release Process
1. Update version in `pyproject.toml` and `src/python_mcp_server/__init__.py`
2. Update `CHANGELOG.md` with new features and fixes
3. Test package build: `uv build`
4. Test CLI command: `python-mcp-server --help`
5. Test FastMCP integration: `fastmcp run`
6. Tag release: `git tag v0.6.0`
7. Push: `git push --tags`
8. GitHub Actions will build and publish to PyPI

### v0.6.0 Development Notes
- **Package Structure**: Migrated to proper src-layout with hatchling
- **FastMCP Integration**: Native configuration and CLI support
- **CLI Entry Point**: Fixed `python-mcp-server` command
- **Testing**: All tests updated for new package structure
- **Documentation**: Comprehensive updates for v0.6.0

This development guide provides everything needed to contribute to and extend the Python MCP Server v0.6.0.