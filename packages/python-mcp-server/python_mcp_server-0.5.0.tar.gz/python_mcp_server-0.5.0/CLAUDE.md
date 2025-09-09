# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Dependencies
```bash
uv sync                    # Install dependencies using uv
```

### Running the Server
```bash
uv run python main.py                              # Default workspace (./workspace)
uv run python main.py --workspace /abs/path/to/work # Custom workspace
uv run python main.py --port 8001                  # Custom port (default: 8000)
MCP_WORKSPACE_DIR=/path/to/work uv run python main.py # Via environment variable
```

### Testing
```bash
uv run pytest -q          # Run all tests quietly
uv run pytest tests/      # Run tests from tests directory
uv run pytest tests/test_server.py::test_tools_list # Run specific test
```

### Development Tools
```bash
python main.py --help     # Show CLI options
```

## Architecture

This is a FastMCP-based Model Context Protocol (MCP) server that provides a persistent Jupyter kernel environment for Python code execution and data analysis.

### Core Components

#### Kernel Management (`main.py:20-48`)
- **KernelManagerSingleton**: Manages a persistent Jupyter kernel instance
- Kernel lifecycle managed via atexit handlers
- Provides stateful Python execution environment across MCP calls

#### Workspace Structure (`main.py:50-63`)
- **WORKSPACE_DIR**: Root workspace directory (configurable via CLI/env)
- **SCRIPTS_DIR**: `workspace/scripts/` - Python scripts saved via `save_script`
- **OUTPUTS_DIR**: `workspace/outputs/` - Rich display outputs (plots, SVG, JSON)
- **UPLOADS_DIR**: `workspace/uploads/` - Files uploaded via HTTP routes
- **Path Security**: `_ensure_within_workspace()` prevents path traversal attacks

#### Key MCP Tools

**Code Execution** (`main.py:77-188`):
- `run_python_code()`: Executes code in persistent kernel, captures rich outputs
- Automatically saves matplotlib plots, SVG, JSON to `outputs/`
- Returns stdout, stderr, results, output files, and newly created files

**File Operations**:
- `list_files()`: Flat listing or ASCII tree view with configurable depth
- `read_file()` / `write_file()`: UTF-8 text or base64 binary support
- `delete_file()`: Safe workspace-scoped deletion

**Script Management**:
- `save_script()`: Save Python scripts to `scripts/` directory
- `run_script()`: Execute scripts in subprocess, track new artifacts

**Kernel Management**:
- `code_completion()` / `inspect_object()`: Jupyter completion and introspection
- `list_variables()`: List non-private globals in kernel namespace
- `restart_kernel()`: Reset kernel state

#### HTTP Routes (`main.py:578-602`)
- `POST /files/upload`: Upload files to `uploads/` directory
- `GET /files/download/{path}`: Download workspace files

### Testing Architecture (`tests/`)
- **conftest.py**: Server fixture with dynamic port allocation
- **test_server.py**: Comprehensive integration tests for all MCP tools
- Uses `fastmcp.client.Client` for testing MCP protocol
- Tests cover: code execution, file operations, plotting, script lifecycle

### Dependencies and Stack
- **FastMCP**: MCP server framework with HTTP transport
- **Jupyter Client**: Kernel management and code execution
- **uv**: Package management and virtual environment
- **Python 3.12+**: Required runtime
- **matplotlib/pandas**: Data analysis dependencies

### Security Model
- All file operations restricted to configured workspace directory
- Path resolution includes symlink checking to prevent escapes
- Subprocess execution uses workspace as cwd
- No credential or sensitive data exposure in default configuration