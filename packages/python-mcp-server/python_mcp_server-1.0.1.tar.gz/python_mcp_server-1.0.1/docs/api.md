# API Reference

Technical API documentation for the Python MCP Server v0.6.0 with FastMCP framework integration.

## MCP Protocol Implementation

The server implements the [Model Context Protocol](https://modelcontextprotocol.io/) specification and provides HTTP/JSON-RPC endpoints for client communication.

### Base URL
```
http://localhost:8000/mcp
```

### Endpoint Structure
```
POST /mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call", 
  "params": {
    "name": "tool_name",
    "arguments": {...}
  }
}
```

## Tool Categories

### Execution Tools

#### `run_python_code`
**Method:** `tools/call`
**Name:** `run_python_code`

**Parameters:**
```typescript
{
  code: string;           // Python code to execute
  timeout?: number;       // Execution timeout (1-300 seconds)
}
```

**Response:**
```typescript
{
  stdout: string;         // Standard output
  stderr: string;         // Error output
  execution_time: number; // Time in seconds
  outputs: string[];      // Generated output files
  new_files: string[];    // New files created
}
```

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "run_python_code",
    "arguments": {
      "code": "import numpy as np\nprint(np.array([1,2,3]).sum())"
    }
  }
}
```

#### `code_completion`
**Method:** `tools/call`
**Name:** `code_completion`

**Parameters:**
```typescript
{
  code: string;           // Code context
  cursor_pos: number;     // Cursor position
}
```

**Response:**
```typescript
{
  matches: string[];      // Completion suggestions
  cursor_start: number;   // Replacement start position
  cursor_end: number;     // Replacement end position
}
```

#### `inspect_object`
**Method:** `tools/call`
**Name:** `inspect_object`

**Parameters:**
```typescript
{
  code: string;           // Object/expression to inspect
  cursor_pos: number;     // Position in code
  detail_level?: number;  // 0=signature, 1=full details
}
```

**Response:**
```typescript
{
  found: boolean;         // Whether object was found
  data: {                 // Inspection results
    text/plain?: string;  // Basic representation
    text/html?: string;   // HTML representation
  };
}
```

### File System Tools

#### `list_files`
**Parameters:**
```typescript
{
  path?: string;          // Directory path (default: workspace root)
  recursive?: boolean;    // Include subdirectories
  tree?: boolean;         // Show tree structure
  max_depth?: number;     // Maximum recursion depth
}
```

**Response:**
```typescript
{
  files: string[];        // List of file paths
  tree?: string;          // Tree representation (if requested)
}
```

#### `read_file`
**Parameters:**
```typescript
{
  path: string;           // File path
}
```

**Response:**
```typescript
{
  text: string;           // File contents
  binary: boolean;        // Whether read as binary
  encoding: string;       // Character encoding
}
```

#### `write_file`
**Parameters:**
```typescript
{
  path: string;           // File path
  content: string;        // File content
  encoding?: string;      // Character encoding (default: utf-8)
}
```

**Response:**
```typescript
{
  path: string;           // Full file path
  size: number;           // File size in bytes
}
```

### Session Management Tools

#### `create_session`
**Parameters:**
```typescript
{
  session_id: string;     // Unique session identifier
  description?: string;   // Optional description
}
```

**Response:**
```typescript
{
  session_id: string;     // Created session ID
  status: string;         // Creation status
  description?: string;   // Session description
}
```

#### `switch_session`
**Parameters:**
```typescript
{
  session_id: string;     // Session to switch to
}
```

**Response:**
```typescript
{
  previous_session: string; // Previous active session
  current_session: string;  // New active session
}
```

#### `list_sessions`
**Parameters:** None

**Response:**
```typescript
{
  sessions: {             // Session details
    [session_id: string]: {
      description?: string;
      created_at: string;
      last_activity: string;
    };
  };
  active_session: string; // Currently active session
  total_sessions: number; // Total session count
}
```

### Health Monitoring Tools

#### `get_kernel_health`
**Parameters:** None

**Response:**
```typescript
{
  status: "healthy" | "dead" | "zombie";
  pid?: number;           // Process ID (if alive)
  memory_usage?: number;  // Memory usage in bytes
  cpu_percent?: number;   // CPU usage percentage
  num_threads?: number;   // Number of threads
  uptime?: number;        // Uptime in seconds
}
```

#### `check_kernel_responsiveness`
**Parameters:** None

**Response:**
```typescript
{
  responsive: boolean;    // Whether kernel responded
  response_time: number;  // Response time in seconds
  test_result: string;    // Result of test operation
}
```

## Error Handling

### Error Response Format
```typescript
{
  jsonrpc: "2.0";
  id: number;
  error: {
    code: number;         // Error code
    message: string;      // Error message
    data?: any;           // Additional error data
  };
}
```

### Common Error Codes
- `-32600`: Invalid Request
- `-32601`: Method not found  
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000`: Tool execution error

### Tool-Specific Errors

#### Code Execution Errors
```json
{
  "error": {
    "code": -32000,
    "message": "Internal error: Code execution failed: NameError: name 'undefined_var' is not defined"
  }
}
```

#### Session Errors
```json
{
  "error": {
    "code": -32000, 
    "message": "Internal error: Session 'nonexistent' not found"
  }
}
```

#### File System Errors
```json
{
  "error": {
    "code": -32000,
    "message": "Internal error: Path 'invalid/path' is outside workspace"
  }
}
```

## Client Integration

### FastMCP Client (Python)
```python
from fastmcp.client import Client

async with Client("http://localhost:8000/mcp") as client:
    result = await client.call_tool("run_python_code", {
        "code": "print('Hello, World!')"
    })
    print(result.data["stdout"])
```

### Raw HTTP Client (Python)
```python
import httpx
import json

async def call_mcp_tool(tool_name: str, arguments: dict):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return response.json()

# Usage
result = await call_mcp_tool("run_python_code", {
    "code": "print('Hello from raw HTTP!')"
})
```

### JavaScript/Node.js Client
```javascript
async function callMcpTool(toolName, arguments) {
    const payload = {
        jsonrpc: "2.0",
        id: 1,
        method: "tools/call",
        params: {
            name: toolName,
            arguments: arguments
        }
    };
    
    const response = await fetch("http://localhost:8000/mcp", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}

// Usage
const result = await callMcpTool("run_python_code", {
    code: "print('Hello from JavaScript!')"
});
```

## Authentication & Security

### Current Implementation
- No authentication required (local development)
- Workspace sandboxing for file operations
- Path traversal protection
- Input validation via Pydantic models

### Production Considerations
For production deployments, consider adding:

```python
# Example JWT authentication middleware
from fastapi.security import HTTPBearer
from jwt import decode

security = HTTPBearer()

@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    if request.url.path.startswith("/mcp"):
        # Validate JWT token
        token = await security(request)
        # Verify token and extract user info
        pass
    return await call_next(request)
```

## Rate Limiting

### Implementation Example
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/mcp")
@limiter.limit("100/minute")
async def mcp_endpoint(request: Request):
    # Your MCP handling code
    pass
```

## OpenAPI Documentation

The server automatically generates OpenAPI documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## WebSocket Support

### Future Enhancement
WebSocket support for real-time communication:

```python
@app.websocket("/mcp/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        # Process MCP message
        response = await handle_mcp_message(data)
        await websocket.send_json(response)
```

## Monitoring & Metrics

### Health Endpoints
```
GET /health          # Basic health check
GET /health/detailed # Detailed system metrics
GET /metrics         # Prometheus metrics (if enabled)
```

### Custom Metrics
```python
from prometheus_client import Counter, Histogram

TOOL_CALLS = Counter('mcp_tool_calls_total', 'Total tool calls', ['tool_name'])
EXECUTION_TIME = Histogram('mcp_execution_seconds', 'Tool execution time')

@EXECUTION_TIME.time()
async def execute_tool(tool_name: str, arguments: dict):
    TOOL_CALLS.labels(tool_name=tool_name).inc()
    # Tool execution logic
```

This API reference provides comprehensive documentation for integrating with the Python Interpreter MCP Server.