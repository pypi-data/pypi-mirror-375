import asyncio
import base64
import atexit
import uuid
import os
import json
import shutil
import subprocess
import time
import psutil
from pathlib import Path
import argparse
from typing import Dict, Any

from jupyter_client.manager import KernelManager
from starlette.responses import FileResponse, JSONResponse
from starlette.requests import Request

from fastmcp import FastMCP, Context
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware  
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.exceptions import ToolError

# --- Timeout Configuration ---

class TimeoutConfig:
    """Centralized timeout configuration with progressive strategies."""
    
    def __init__(self):
        # Base timeouts for different operation types
        self.code_execution = 30.0      # Base timeout for code execution
        self.completion = 5.0           # Code completion timeout  
        self.inspection = 5.0           # Object inspection timeout
        self.kernel_response = 10.0     # General kernel response timeout
        self.health_check = 3.0         # Kernel health check timeout
        self.state_operations = 15.0    # State save/restore operations
        
        # Progressive timeout multipliers
        self.progressive_multipliers = [1.0, 1.5, 2.0, 3.0]
        
        # Retry configurations  
        self.max_retries = 3
        self.retry_delay = 0.5
        
    def get_progressive_timeout(self, base_timeout: float, attempt: int) -> float:
        """Get progressively longer timeout based on attempt number."""
        multiplier_index = min(attempt, len(self.progressive_multipliers) - 1)
        return base_timeout * self.progressive_multipliers[multiplier_index]
    
    def get_timeout_context(self, operation: str, attempt: int, timeout: float) -> str:
        """Get human-readable timeout context."""
        if attempt > 0:
            return f"{operation} (attempt {attempt + 1}, timeout: {timeout:.1f}s)"
        return f"{operation} (timeout: {timeout:.1f}s)"

# --- Session-based Kernel Management ---

class KernelSession:
    """A single kernel session with isolated state and execution context."""
    
    def __init__(self, session_id: str, timeout_config: TimeoutConfig):
        self.session_id = session_id
        self.timeout_config = timeout_config
        self.km = None
        self.client = None
        self.start_time = None
        self.execution_count = 0
        self.last_execution_time = None
        self.total_execution_time = 0.0
        self.pending_operations = {}
        self.metadata = {}
        self.is_active = False
        
    def start(self):
        """Start this kernel session."""
        if self.is_active:
            return
            
        self.km = KernelManager()
        self.km.start_kernel()
        self.start_time = time.time()
        self.client = self.km.client()
        self.client.start_channels()
        self.is_active = True
        print(f"Kernel Session '{self.session_id}' Started")
        
    def stop(self):
        """Stop this kernel session."""
        if not self.is_active:
            return
            
        if self.km and self.km.is_alive():
            self.km.shutdown_kernel(now=True)
        self.is_active = False
        print(f"Kernel Session '{self.session_id}' Stopped")
        
    def get_client(self):
        """Get the kernel client for this session."""
        return self.client if self.is_active else None
        
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics for this specific session."""
        if not self.km or not self.km.is_alive() or not self.is_active:
            return {
                "status": "dead",
                "session_id": self.session_id,
                "uptime": 0,
                "execution_count": self.execution_count,
                "error": "Kernel session is not running"
            }
        
        uptime = time.time() - (self.start_time or 0)
        
        # Get kernel process info if available
        kernel_info = {}
        try:
            if hasattr(self.km, 'kernel') and self.km.kernel:
                pid = self.km.kernel.pid
                if pid:
                    process = psutil.Process(pid)
                    kernel_info = {
                        "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                        "cpu_percent": process.cpu_percent(),
                        "num_threads": process.num_threads(),
                        "create_time": process.create_time(),
                    }
        except (psutil.NoSuchProcess, AttributeError):
            kernel_info = {"error": "Could not access kernel process info"}
        
        return {
            "status": "alive",
            "session_id": self.session_id,
            "uptime": round(uptime, 2),
            "execution_count": self.execution_count,
            "last_execution_time": self.last_execution_time,
            "average_execution_time": round(
                self.total_execution_time / max(1, self.execution_count), 3
            ),
            "kernel_process": kernel_info,
            "metadata": self.metadata.copy()
        }
    
    def record_execution(self, execution_time: float):
        """Record execution metrics for this session."""
        self.execution_count += 1
        self.last_execution_time = time.time()
        self.total_execution_time += execution_time
    
    def is_responsive(self, timeout: float = 5.0) -> bool:
        """Check if this session's kernel is responsive."""
        try:
            client = self.get_client()
            if not client:
                return False
            
            # Send a simple kernel_info request to test responsiveness
            msg_id = client.kernel_info()
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    msg = client.get_shell_msg(timeout=0.5)
                    parent_msg_id = msg.get('parent_header', {}).get('msg_id')
                    if parent_msg_id == msg_id:
                        return msg['content']['status'] == 'ok'
                except Exception:
                    continue
            return False
        except Exception:
            return False

class SessionManager:
    """Manages multiple kernel sessions with isolation and resource control."""
    
    def __init__(self, timeout_config: TimeoutConfig):
        self.timeout_config = timeout_config
        self.sessions = {}  # session_id -> KernelSession
        self.default_session_id = "default"
        self.active_session_id = self.default_session_id
        self.max_sessions = 5  # Configurable limit
        self.session_counter = 0
        
        # Create default session
        self._create_session(self.default_session_id, auto_start=True)
        
        # Register cleanup
        atexit.register(self.shutdown_all_sessions)
    
    def _create_session(self, session_id: str, auto_start: bool = False) -> KernelSession:
        """Create a new kernel session."""
        if session_id in self.sessions:
            return self.sessions[session_id]
            
        if len(self.sessions) >= self.max_sessions:
            raise ToolError(f"Maximum number of sessions ({self.max_sessions}) reached")
        
        session = KernelSession(session_id, self.timeout_config)
        self.sessions[session_id] = session
        
        if auto_start:
            session.start()
            
        return session
    
    def create_session(self, session_id: str = None, metadata: Dict[str, Any] = None) -> str:
        """Create a new isolated kernel session."""
        if session_id is None:
            self.session_counter += 1
            session_id = f"session_{self.session_counter}"
        
        session = self._create_session(session_id)
        if metadata:
            session.metadata.update(metadata)
            
        return session_id
    
    def get_session(self, session_id: str = None) -> KernelSession:
        """Get a specific session or the active session."""
        target_id = session_id or self.active_session_id
        
        if target_id not in self.sessions:
            raise ToolError(f"Session '{target_id}' does not exist")
        
        return self.sessions[target_id]
    
    def switch_session(self, session_id: str):
        """Switch the active session."""
        if session_id not in self.sessions:
            raise ToolError(f"Session '{session_id}' does not exist")
        
        self.active_session_id = session_id
        
        # Ensure the session is started
        session = self.sessions[session_id]
        if not session.is_active:
            session.start()
    
    def list_sessions(self) -> Dict[str, Any]:
        """List all available sessions."""
        sessions_info = {}
        for session_id, session in self.sessions.items():
            sessions_info[session_id] = {
                "active": session.is_active,
                "current": session_id == self.active_session_id,
                "execution_count": session.execution_count,
                "uptime": time.time() - session.start_time if session.start_time else 0,
                "metadata": session.metadata.copy()
            }
        
        return {
            "sessions": sessions_info,
            "active_session": self.active_session_id,
            "total_sessions": len(self.sessions),
            "max_sessions": self.max_sessions
        }
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session (cannot delete default session)."""
        if session_id == self.default_session_id:
            raise ToolError("Cannot delete the default session")
        
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.stop()
        del self.sessions[session_id]
        
        # If we deleted the active session, switch to default
        if self.active_session_id == session_id:
            self.active_session_id = self.default_session_id
            
        return True
    
    def shutdown_all_sessions(self):
        """Shutdown all kernel sessions."""
        for session in self.sessions.values():
            session.stop()

# --- Kernel Manager Singleton (Updated for Session Support) ---

class KernelManagerSingleton:
    """Backwards compatibility wrapper that delegates to session manager."""
    _instance = None
    _session_manager = None
    _timeout_config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KernelManagerSingleton, cls).__new__(cls)
            cls._timeout_config = TimeoutConfig()
            cls._session_manager = SessionManager(cls._timeout_config)
            print("Session-based Kernel Manager Initialized")
        return cls._instance

    def get_client(self):
        """Get client from the active session."""
        session = self._session_manager.get_session()
        return session.get_client()

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics from active session."""
        session = self._session_manager.get_session()
        return session.get_health_metrics()
    
    def record_execution(self, execution_time: float):
        """Record execution metrics in active session."""
        session = self._session_manager.get_session()
        session.record_execution(execution_time)
    
    async def execute_with_retry(self, operation_name: str, operation_func, max_retries: int = None, base_timeout: float = None):
        """Execute an operation with progressive timeout and retry logic in active session."""
        session = self._session_manager.get_session()
        
        max_retries = max_retries or self._timeout_config.max_retries
        base_timeout = base_timeout or self._timeout_config.kernel_response
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                timeout = self._timeout_config.get_progressive_timeout(base_timeout, attempt)
                context_msg = self._timeout_config.get_timeout_context(operation_name, attempt, timeout)
                
                # Register operation for potential cancellation in the session
                operation_id = str(uuid.uuid4())
                session.pending_operations[operation_id] = {
                    "name": operation_name,
                    "start_time": time.time(),
                    "timeout": timeout,
                    "attempt": attempt + 1
                }
                
                try:
                    # Execute the operation with timeout
                    result = await asyncio.wait_for(
                        operation_func(timeout, context_msg),
                        timeout=timeout
                    )
                    
                    # Clean up successful operation
                    session.pending_operations.pop(operation_id, None)
                    return result
                    
                except asyncio.TimeoutError:
                    last_exception = ToolError(
                        f"Operation '{operation_name}' timed out after {timeout:.1f}s on attempt {attempt + 1}"
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(self._timeout_config.retry_delay)
                        continue
                    else:
                        raise last_exception
                
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries and self._should_retry_on_error(e):
                        await asyncio.sleep(self._timeout_config.retry_delay)
                        continue
                    else:
                        raise e
                        
                finally:
                    # Clean up operation tracking
                    session.pending_operations.pop(operation_id, None)
                    
            except Exception as e:
                if attempt == max_retries:
                    # Convert to ToolError if not already
                    if not isinstance(e, ToolError):
                        raise ToolError(f"Operation '{operation_name}' failed after {max_retries + 1} attempts: {str(e)}")
                    raise e
        
        # Fallback (shouldn't reach here)
        raise ToolError(f"Operation '{operation_name}' failed after all retry attempts")
    
    def _should_retry_on_error(self, error: Exception) -> bool:
        """Determine if an error is retryable."""
        # Don't retry on certain fatal errors
        fatal_patterns = [
            "kernel died",
            "connection refused", 
            "no such process",
            "permission denied"
        ]
        
        error_msg = str(error).lower()
        return not any(pattern in error_msg for pattern in fatal_patterns)
    
    def get_pending_operations(self) -> Dict[str, Any]:
        """Get information about currently pending operations from active session."""
        session = self._session_manager.get_session()
        now = time.time()
        return {
            op_id: {
                **op_info,
                "elapsed_time": round(now - op_info["start_time"], 2),
                "remaining_time": round(op_info["timeout"] - (now - op_info["start_time"]), 2)
            }
            for op_id, op_info in session.pending_operations.items()
        }
    
    def cancel_all_operations(self) -> Dict[str, Any]:
        """Cancel all pending operations from active session."""
        session = self._session_manager.get_session()
        cancelled_ops = list(session.pending_operations.keys())
        session.pending_operations.clear()
        return {
            "cancelled_operations": len(cancelled_ops),
            "operation_ids": cancelled_ops
        }
    
    def is_responsive(self, timeout: float = 5.0) -> bool:
        """Check if active session kernel is responsive."""
        session = self._session_manager.get_session()
        return session.is_responsive(timeout)
    
    def get_kernel_state(self, timeout: float = 10.0) -> Dict[str, Any]:
        """Extract current kernel state (variables) for preservation."""
        try:
            client = self.get_client()
            if not client:
                return {}
            
            # Get all non-private variables from the kernel
            code = '''
import pickle, base64, types, sys
_preserved_vars = {}
for _k, _v in globals().items():
    if not _k.startswith('_') and not isinstance(_v, types.ModuleType):
        try:
            # Test if the object can be pickled
            pickle.dumps(_v)
            _preserved_vars[_k] = _v
        except Exception:
            # Skip unpickleable objects
            pass
            
_encoded_state = base64.b64encode(pickle.dumps(_preserved_vars)).decode('ascii')
print(f"STATE_SNAPSHOT:{_encoded_state}")
'''
            
            msg_id = client.execute(code)
            
            start_time = time.time()
            state_data = {}
            
            while time.time() - start_time < timeout:
                try:
                    msg = client.get_iopub_msg(timeout=1)
                    parent_msg_id = msg.get('parent_header', {}).get('msg_id')
                    if parent_msg_id != msg_id:
                        continue
                    
                    if msg['header']['msg_type'] == 'stream' and msg['content']['name'] == 'stdout':
                        content = msg['content']['text']
                        if content.startswith('STATE_SNAPSHOT:'):
                            encoded_state = content[15:].strip()
                            try:
                                import pickle
                                import base64
                                state_data = pickle.loads(base64.b64decode(encoded_state))
                                break
                            except Exception:
                                continue
                    elif msg['header']['msg_type'] == 'status':
                        if msg['content']['execution_state'] == 'idle':
                            break
                except Exception:
                    continue
            
            return {
                "success": True,
                "variables": state_data,
                "count": len(state_data),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restore_kernel_state(self, state_data: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
        """Restore kernel state from preserved data."""
        try:
            if not state_data.get("success") or not state_data.get("variables"):
                return {"success": False, "error": "No valid state data provided"}
            
            client = self.get_client()
            if not client:
                return {"success": False, "error": "No kernel client available"}
            
            # Encode the state data and restore it
            import pickle
            import base64
            encoded_vars = base64.b64encode(pickle.dumps(state_data["variables"])).decode('ascii')
            
            code = f'''
import pickle
import base64
try:
    _restored_vars = pickle.loads(base64.b64decode("{encoded_vars}"))
    _restored_count = 0
    for _k, _v in _restored_vars.items():
        globals()[_k] = _v
        _restored_count += 1
    print(f"RESTORE_SUCCESS:{{_restored_count}}")
except Exception as e:
    print(f"RESTORE_ERROR:{{str(e)}}")
'''
            
            msg_id = client.execute(code)
            
            start_time = time.time()
            restored_count = 0
            success = False
            
            while time.time() - start_time < timeout:
                try:
                    msg = client.get_iopub_msg(timeout=1)
                    parent_msg_id = msg.get('parent_header', {}).get('msg_id')
                    if parent_msg_id != msg_id:
                        continue
                    
                    if msg['header']['msg_type'] == 'stream' and msg['content']['name'] == 'stdout':
                        content = msg['content']['text'].strip()
                        if content.startswith('RESTORE_SUCCESS:'):
                            restored_count = int(content[16:])
                            success = True
                            break
                        elif content.startswith('RESTORE_ERROR:'):
                            return {"success": False, "error": content[14:]}
                    elif msg['header']['msg_type'] == 'status':
                        if msg['content']['execution_state'] == 'idle':
                            break
                except Exception:
                    continue
            
            return {
                "success": success,
                "restored_count": restored_count,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def shutdown_kernel(self):
        """Shutdown all sessions (backwards compatibility)."""
        self._session_manager.shutdown_all_sessions()

# Initialize the singleton
kernel_manager = KernelManagerSingleton()

# --- Workspace Setup ---
MCP_WORKSPACE_ENV = os.environ.get("MCP_WORKSPACE_DIR", "workspace")
WORKSPACE_DIR = Path(MCP_WORKSPACE_ENV).resolve()
SCRIPTS_DIR = WORKSPACE_DIR / "scripts"
OUTPUTS_DIR = WORKSPACE_DIR / "outputs"
UPLOADS_DIR = WORKSPACE_DIR / "uploads"
for d in (WORKSPACE_DIR, SCRIPTS_DIR, OUTPUTS_DIR, UPLOADS_DIR):
    d.mkdir(parents=True, exist_ok=True)

def _ensure_within_workspace(p: Path) -> Path:
    p = (WORKSPACE_DIR / p).resolve() if not p.is_absolute() else p.resolve()
    if WORKSPACE_DIR not in p.parents and p != WORKSPACE_DIR:
        raise ValueError("Path escapes workspace")
    return p

# --- FastMCP Server ---

mcp = FastMCP(name="Python Interpreter MCP")

# Add comprehensive middleware stack for professional error handling, timing, and logging
mcp.add_middleware(ErrorHandlingMiddleware(
    include_traceback=True,
    transform_errors=True
))
mcp.add_middleware(TimingMiddleware())
mcp.add_middleware(LoggingMiddleware())

def _snapshot_workspace_files() -> set[str]:
    return {
        str(p.relative_to(WORKSPACE_DIR))
        for p in WORKSPACE_DIR.rglob("*")
        if p.is_file()
    }


async def _execute_code_with_timeout(code: str, ctx: Context, timeout: float, context_msg: str) -> dict:
    """Execute Python code with enhanced timeout handling."""
    await ctx.debug(f"Executing Python code ({len(code)} characters) - {context_msg}")
    client = kernel_manager.get_client()
    
    if not client:
        raise ToolError("Kernel client is not available")
    
    # Clear any pending messages
    await ctx.debug("Clearing pending kernel messages")
    while True:
        try:
            client.get_shell_msg(timeout=0.1)
        except Exception:
            break

    # Snapshot files before execution to detect newly created outputs
    await ctx.debug("Taking workspace snapshot before execution")
    before_files = _snapshot_workspace_files()

    await ctx.info(f"Starting code execution - {context_msg}")
    execution_start_time = time.time()
    msg_id = client.execute(code)
    
    stdout = ""
    stderr = ""
    outputs = []
    results = []
    
    # Calculate deadline for this execution
    deadline = execution_start_time + timeout
    
    while time.time() < deadline:
        try:
            remaining_timeout = max(0.1, deadline - time.time())
            msg = client.get_iopub_msg(timeout=min(1.0, remaining_timeout))
            
            # Check if message belongs to our execution
            parent_msg_id = msg.get('parent_header', {}).get('msg_id')
            if parent_msg_id != msg_id:
                continue

            msg_type = msg['header']['msg_type']

            if msg_type == 'status':
                if msg['content']['execution_state'] == 'idle':
                    break
            
            elif msg_type == 'stream':
                if msg['content']['name'] == 'stdout':
                    stdout += msg['content']['text']
                else:
                    stderr += msg['content']['text']

            elif msg_type in ('display_data', 'execute_result'):
                data = msg['content']['data']
                # Save images
                if 'image/png' in data:
                    img_data = base64.b64decode(data['image/png'])
                    filename = f"{uuid.uuid4()}.png"
                    filepath = OUTPUTS_DIR / filename
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                    outputs.append(str(filepath.relative_to(WORKSPACE_DIR)))
                # Save SVG if provided
                elif 'image/svg+xml' in data:
                    svg_text = data['image/svg+xml']
                    filename = f"{uuid.uuid4()}.svg"
                    filepath = OUTPUTS_DIR / filename
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(svg_text)
                    outputs.append(str(filepath.relative_to(WORKSPACE_DIR)))
                # Save JSON payloads to a file for later retrieval
                if 'application/json' in data:
                    try:
                        parsed = data['application/json']
                        filename = f"{uuid.uuid4()}.json"
                        filepath = OUTPUTS_DIR / filename
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(parsed, f)
                        outputs.append(str(filepath.relative_to(WORKSPACE_DIR)))
                    except Exception:
                        pass
                # Capture plain text results too
                if 'text/plain' in data:
                    results.append(str(data['text/plain']))
            
            elif msg_type == 'error':
                stderr += "\n".join(msg['content']['traceback'])

        except asyncio.TimeoutError:
            # Check if we've exceeded our overall timeout
            if time.time() >= deadline:
                raise asyncio.TimeoutError(f"Code execution timed out after {timeout:.1f}s")
            # Otherwise, kernel is idle - continue
            break
        except Exception as e:
            # Something went wrong with message handling
            await ctx.warning(f"Error processing kernel message: {str(e)}")
            stderr += f"Error processing kernel message: {e}"
            break
    
    # Check if we timed out
    if time.time() >= deadline:
        raise asyncio.TimeoutError(f"Code execution exceeded timeout of {timeout:.1f}s")

    # Detect any files created during execution
    await ctx.debug("Taking final workspace snapshot")
    after_files = _snapshot_workspace_files()
    new_files = sorted(list(after_files - before_files))
    
    # Record execution metrics
    execution_time = time.time() - execution_start_time
    kernel_manager.record_execution(execution_time)
    
    await ctx.info(f"Code execution completed in {execution_time:.3f}s. Generated {len(outputs)} outputs, {len(new_files)} new files")
    if stderr:
        await ctx.warning(f"Execution had errors: {stderr[:100]}...")
    
    return {
        "stdout": stdout,
        "stderr": stderr,
        "results": results,
        "outputs": outputs,
        "new_files": new_files,
        "execution_time": round(execution_time, 3)
    }

@mcp.tool
async def run_python_code(code: str, ctx: Context) -> dict:
    """Execute Python code in the persistent Jupyter kernel with enhanced timeout handling.

    The kernel session is shared across calls, enabling stateful workflows.
    Rich display outputs (image/png, image/svg+xml, application/json) are saved
    under `outputs/` and their relative paths are returned.

    Features progressive timeout and retry logic for reliable execution.

    Args:
        code: Python source to execute.
        ctx: FastMCP request context.

    Returns:
        dict: A payload containing:
            stdout: Captured standard output.
            stderr: Captured standard error and tracebacks.
            results: Text/plain execute_result payloads.
            outputs: Relative paths to saved display outputs under outputs/.
            new_files: Relative paths of files newly created under the workspace.
    """
    # Use the enhanced timeout handling with retry logic
    async def execute_operation(timeout: float, context_msg: str):
        return await _execute_code_with_timeout(code, ctx, timeout, context_msg)
    
    return await kernel_manager.execute_with_retry(
        "Python code execution",
        execute_operation,
        base_timeout=kernel_manager._timeout_config.code_execution
    )

async def _get_completions_with_timeout(code: str, cursor_pos: int, ctx: Context, timeout: float, context_msg: str) -> dict:
    """Get code completions with enhanced timeout handling."""
    await ctx.debug(f"Requesting completions at position {cursor_pos} - {context_msg}")
    client = kernel_manager.get_client()
    
    if not client:
        raise ToolError("Kernel client is not available")
    
    client.complete(code, cursor_pos)
    
    try:
        msg = client.get_shell_msg(timeout=timeout)
        await ctx.debug(f"Received {len(msg['content'].get('matches', []))} completion suggestions")
        return msg['content']
    except Exception as e:
        raise ToolError(f"Failed to get code completions: {str(e)}")

@mcp.tool
async def code_completion(code: str, cursor_pos: int, ctx: Context) -> dict:
    """Provide code completion suggestions from the Jupyter kernel with enhanced timeout handling.

    Args:
        code: Buffer contents to complete against.
        cursor_pos: Cursor index within `code` to request completions for.
        ctx: FastMCP request context.

    Returns:
        dict: Raw Jupyter completion reply.
    """
    # Use the enhanced timeout handling with retry logic
    async def completion_operation(timeout: float, context_msg: str):
        return await _get_completions_with_timeout(code, cursor_pos, ctx, timeout, context_msg)
    
    return await kernel_manager.execute_with_retry(
        "Code completion",
        completion_operation,
        base_timeout=kernel_manager._timeout_config.completion
    )

async def _inspect_object_with_timeout(code: str, cursor_pos: int, ctx: Context, detail_level: int, timeout: float, context_msg: str) -> dict:
    """Inspect object with enhanced timeout handling."""
    await ctx.debug(f"Inspecting object at position {cursor_pos} with detail level {detail_level} - {context_msg}")
    client = kernel_manager.get_client()
    
    if not client:
        raise ToolError("Kernel client is not available")
    
    client.inspect(code, cursor_pos, detail_level)
    
    try:
        msg = client.get_shell_msg(timeout=timeout)
        await ctx.debug("Object inspection completed")
        return msg['content']
    except Exception as e:
        raise ToolError(f"Failed to inspect object: {str(e)}")

@mcp.tool
async def inspect_object(code: str, cursor_pos: int, ctx: Context, detail_level: int = 0) -> dict:
    """Inspect an object/expression within the kernel namespace with enhanced timeout handling.

    Args:
        code: Buffer containing the target expression.
        cursor_pos: Cursor index within `code` to inspect.
        ctx: FastMCP request context.
        detail_level: Jupyter detail level (0 minimal, higher is more verbose).

    Returns:
        dict: Raw Jupyter inspection reply.
    """
    # Use the enhanced timeout handling with retry logic
    async def inspection_operation(timeout: float, context_msg: str):
        return await _inspect_object_with_timeout(code, cursor_pos, ctx, detail_level, timeout, context_msg)
    
    return await kernel_manager.execute_with_retry(
        "Object inspection",
        inspection_operation,
        base_timeout=kernel_manager._timeout_config.inspection
    )

def _render_tree(root: Path, max_depth: int | None = 3, include_files: bool = True, include_dirs: bool = True) -> str:
    def is_included(p: Path) -> bool:
        return (include_files and p.is_file()) or (include_dirs and p.is_dir())

    def children(p: Path):
        try:
            return sorted([c for c in p.iterdir() if is_included(c)], key=lambda x: (x.is_file(), x.name.lower()))
        except Exception:
            return []

    lines: list[str] = []

    def walk(p: Path, prefix: str = "", depth: int = 0):
        if depth == 0:
            lines.append(p.name + ("/" if p.is_dir() else ""))
        if max_depth is not None and depth >= max_depth:
            return
        kids = children(p)
        for i, c in enumerate(kids):
            last = i == len(kids) - 1
            connector = "└── " if last else "├── "
            lines.append(prefix + connector + c.name + ("/" if c.is_dir() else ""))
            if c.is_dir():
                extension = "    " if last else "│   "
                walk(c, prefix + extension, depth + 1)

    walk(root)
    return "\n".join(lines)


@mcp.tool
async def list_files(
    ctx: Context,
    path: str | None = None,
    recursive: bool = False,
    tree: bool = False,
    max_depth: int | None = 3,
    include_files: bool = True,
    include_dirs: bool = True
) -> dict:
    """List workspace files/directories with flat or tree output.

    Args:
        ctx: FastMCP request context.
        path: Optional relative subpath. Defaults to workspace root.
        recursive: If True, return all descendants (flat list in `files`).
        tree: If True, return an ASCII tree rendering in `tree`.
        max_depth: Depth cap for recursion/tree; None for unlimited.
        include_files: Include files in results.
        include_dirs: Include directories in results.

    Returns:
        dict: Flat listing -> {root, files}; tree -> {root, tree}. On error -> {error}.
    """
    await ctx.debug(f"Listing files - path: {path}, recursive: {recursive}, tree: {tree}")
    try:
        base = _ensure_within_workspace(WORKSPACE_DIR / (path or ""))
    except Exception:
        await ctx.warning(f"Invalid path provided: {path}")
        raise ToolError(f"Invalid path: {path} escapes workspace boundaries")

    if tree:
        root = base
        if not root.exists():
            raise ToolError(f"Path not found: {path}")
        if root.is_file():
            # Tree for a file is trivial
            rel = root.relative_to(WORKSPACE_DIR)
            return {"root": str(rel), "tree": rel.name}
        txt = _render_tree(root, max_depth=max_depth, include_files=include_files, include_dirs=include_dirs)
        return {"root": str(base.relative_to(WORKSPACE_DIR)), "tree": txt}

    # Flat listing
    if not base.exists():
        raise ToolError(f"Path not found: {path}")

    if recursive:
        results: list[str] = []
        for p in base.rglob("*"):
            if not ((include_files and p.is_file()) or (include_dirs and p.is_dir())):
                continue
            # Respect max_depth if provided
            if max_depth is not None:
                try:
                    depth = len(p.relative_to(base).parts)
                except Exception:
                    depth = 0
                if depth > max_depth:
                    continue
            results.append(str(p.relative_to(WORKSPACE_DIR)))
        return {"root": str(base.relative_to(WORKSPACE_DIR)) if base != WORKSPACE_DIR else ".", "files": sorted(results)}
    else:
        try:
            entries = [
                str((base / c.name).relative_to(WORKSPACE_DIR))
                for c in base.iterdir()
                if (include_files and c.is_file()) or (include_dirs and c.is_dir())
            ]
        except Exception as e:
            raise ToolError(f"Error listing files: {str(e)}")
        return {"root": str(base.relative_to(WORKSPACE_DIR)) if base != WORKSPACE_DIR else ".", "files": sorted(entries)}

@mcp.tool
async def ping(ctx: Context) -> dict:
    """Health check for the MCP server.

    Args:
        ctx: FastMCP request context.

    Returns:
        dict: {ok: True}
    """
    return {"ok": True}

@mcp.tool
async def delete_file(filename: str, ctx: Context) -> dict:
    """Delete a file from the workspace.

    Args:
        filename: Relative path of the file to delete.
        ctx: FastMCP request context.

    Returns:
        dict: {success: True} on success; otherwise {error} with status code.
    """
    await ctx.debug(f"Deleting file: {filename}")
    try:
        filepath = _ensure_within_workspace(Path(filename))
    except Exception:
        await ctx.warning(f"Invalid path provided for deletion: {filename}")
        raise ToolError(f"Invalid path: {filename} escapes workspace boundaries")
    if not filepath.exists():
        raise ToolError(f"File not found: {filename}")
    try:
        os.remove(filepath)
        await ctx.info(f"Successfully deleted file: {filename}")
        return {"success": True}
    except Exception as e:
        raise ToolError(f"Error deleting file: {str(e)}")

@mcp.tool
async def read_file(path: str, ctx: Context, max_bytes: int | None = None) -> dict:
    """Read a text or binary file from the workspace.

    Attempts UTF-8 decoding; if that fails, returns base64-encoded bytes.

    Args:
        path: Relative file path.
        ctx: FastMCP request context.
        max_bytes: Optional byte limit to truncate content.

    Returns:
        dict: {text} for UTF-8, or {base64} for binary; or {error}.
    """
    await ctx.debug(f"Reading file: {path} (max_bytes: {max_bytes})")
    try:
        filepath = _ensure_within_workspace(Path(path))
        if not filepath.exists() or not filepath.is_file():
            await ctx.warning(f"File not found: {path}")
            raise ToolError(f"File not found: {path}")
        data = filepath.read_bytes()
        if max_bytes is not None:
            data = data[:max_bytes]
        try:
            await ctx.debug(f"Successfully read file as UTF-8: {path}")
            return {"text": data.decode("utf-8")}
        except UnicodeDecodeError:
            await ctx.debug(f"File is binary, returning base64: {path}")
            return {"base64": base64.b64encode(data).decode("ascii")}
    except Exception as e:
        raise ToolError(f"Error reading file {path}: {str(e)}")

@mcp.tool
async def write_file(path: str, content: str, ctx: Context, binary_base64: bool = False) -> dict:
    """Write a file under the workspace (text or base64-encoded binary).

    Args:
        path: Relative destination path.
        content: Text or base64 data.
        ctx: FastMCP request context.
        binary_base64: Treat `content` as base64 and write bytes when True.

    Returns:
        dict: {path} relative to the workspace; or {error}.
    """
    await ctx.debug(f"Writing file: {path} (binary_base64: {binary_base64})")
    try:
        filepath = _ensure_within_workspace(Path(path))
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if binary_base64:
            data = base64.b64decode(content)
            filepath.write_bytes(data)
        else:
            filepath.write_text(content, encoding="utf-8")
        await ctx.debug(f"Successfully wrote file: {path}")
        return {"path": str(filepath.relative_to(WORKSPACE_DIR))}
    except Exception as e:
        raise ToolError(f"Error writing file {path}: {str(e)}")

@mcp.tool
async def save_script(name: str, content: str, ctx: Context) -> dict:
    """Save a Python script under `scripts/`.

    Args:
        name: Script filename; `.py` appended if missing.
        content: Python source code.
        ctx: FastMCP request context.

    Returns:
        dict: {script} relative path under the workspace; or {error}.
    """
    await ctx.debug(f"Saving script: {name}")
    if not name.endswith(".py"):
        name = f"{name}.py"
    try:
        target = _ensure_within_workspace(SCRIPTS_DIR / name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        await ctx.debug(f"Successfully saved script: {name}")
        return {"script": str(target.relative_to(WORKSPACE_DIR))}
    except Exception as e:
        raise ToolError(f"Error saving script {name}: {str(e)}")

@mcp.tool
async def run_script(path: str, ctx: Context, args: list[str] | None = None, timeout: int = 120) -> dict:
    """Run a Python script in a subprocess and report artifacts.

    Args:
        path: Relative script path under the workspace.
        ctx: FastMCP request context.
        args: Optional subprocess arguments.
        timeout: Seconds until execution times out.

    Returns:
        dict: {stdout, stderr, returncode, new_files}; or {error}.
    """
    await ctx.info(f"Running script: {path} with args: {args}")
    try:
        script_path = _ensure_within_workspace(Path(path))
    except Exception:
        await ctx.warning(f"Invalid script path: {path}")
        raise ToolError(f"Invalid script path: {path}")
    if not script_path.exists():
        raise ToolError(f"Script not found: {path}")
    if args is None:
        args = []
    before = _snapshot_workspace_files()
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"), str(script_path)] + list(args),
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = proc.stdout
        stderr = proc.stderr
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        await ctx.warning(f"Script execution timed out after {timeout}s: {path}")
        raise ToolError(f"Script execution timed out after {timeout} seconds")
    after = _snapshot_workspace_files()
    new_files = sorted(list(after - before))
    return {"stdout": stdout, "stderr": stderr, "returncode": rc, "new_files": new_files}

@mcp.tool
async def install_dependencies(packages: list[str], ctx: Context) -> dict:
    """Install Python packages into the current environment.

    Prefers `uv pip install` when available; otherwise uses `python -m pip install`.

    Args:
        packages: List of package specifiers.
        ctx: FastMCP request context.

    Returns:
        dict: {returncode, stdout, stderr} from the installer.
    """
    await ctx.info(f"Installing packages: {packages}")
    if not packages:
        await ctx.warning("No packages provided for installation")
        raise ToolError("No packages provided for installation")
    cmds = []
    # Prefer uv if available (works well in uv-managed envs)
    if shutil.which("uv"):
        cmds.append(["uv", "pip", "install", *packages])
    # Fallback to pip if present
    cmds.append([os.environ.get("PYTHON", "python"), "-m", "pip", "install", "--disable-pip-version-check", *packages])
    last = {"returncode": -1, "stdout": "", "stderr": ""}
    for cmd in cmds:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            last = {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
            if proc.returncode == 0:
                return last
        except Exception as e:
            last = {"returncode": -1, "stdout": "", "stderr": str(e)}
    return last

@mcp.tool
async def list_variables(ctx: Context) -> dict:
    """List variable names in the kernel's global namespace (best-effort).

    Args:
        ctx: FastMCP request context.

    Returns:
        dict: {variables: list[str]} of non-private globals (modules filtered).
    """
    await ctx.debug("Listing kernel variables")
    client = kernel_manager.get_client()
    code = (
        "import builtins,types\n"
        "_vars=[k for k,v in globals().items() if not k.startswith('_') and not isinstance(v, types.ModuleType)]\n"
        "print('\n'.join(sorted(_vars)))\n"
    )
    msg_id = client.execute(code)
    names = []
    while True:
        try:
            msg = client.get_iopub_msg(timeout=1)
            parent_msg_id = msg.get('parent_header', {}).get('msg_id')
            if parent_msg_id != msg_id:
                continue
            if msg['header']['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                break
            if msg['header']['msg_type'] == 'stream' and msg['content']['name'] == 'stdout':
                stdout_text = msg['content']['text']
                names.extend([line for line in stdout_text.splitlines() if line.strip()])
        except asyncio.TimeoutError:
            break
        except Exception:
            break
    return {"variables": sorted(set(names))}

@mcp.tool
async def restart_kernel(ctx: Context, preserve_state: bool = False) -> dict:
    """Restart the Jupyter kernel with optional state preservation.

    Args:
        ctx: FastMCP request context.
        preserve_state: If True, save and restore kernel variables across restart.

    Returns:
        dict: {restarted: True, preserved_vars: count} on success.
    """
    await ctx.info(f"Restarting Jupyter kernel (preserve_state: {preserve_state})")
    
    saved_state = None
    preserved_count = 0
    
    try:
        # Save state if requested
        if preserve_state:
            await ctx.info("Saving kernel state before restart...")
            saved_state = kernel_manager.get_kernel_state()
            if saved_state.get("success"):
                preserved_count = saved_state.get("count", 0)
                await ctx.info(f"Saved {preserved_count} variables")
            else:
                await ctx.warning(f"Failed to save state: {saved_state.get('error', 'Unknown error')}")
        
        # Restart the active session kernel
        session_manager = kernel_manager._session_manager
        current_session_id = session_manager.active_session_id
        current_session = session_manager.get_session(current_session_id)
        
        # Stop and restart the session
        current_session.stop()
        
        # Reset session metrics
        current_session.execution_count = 0
        current_session.last_execution_time = None
        current_session.total_execution_time = 0.0
        current_session.pending_operations.clear()
        
        # Start the session again (creates fresh kernel)
        current_session.start()
        
        # Restore state if we saved it
        restore_result = {"success": True, "restored_count": 0}
        if preserve_state and saved_state and saved_state.get("success"):
            await ctx.info("Restoring kernel state...")
            restore_result = kernel_manager.restore_kernel_state(saved_state)
            if restore_result.get("success"):
                await ctx.info(f"Restored {restore_result.get('restored_count', 0)} variables")
            else:
                await ctx.warning(f"Failed to restore state: {restore_result.get('error', 'Unknown error')}")
        
        await ctx.info(f"Kernel session '{current_session_id}' restarted successfully")
        return {
            "restarted": True,
            "session_id": current_session_id,
            "preserve_state": preserve_state,
            "preserved_vars": preserved_count,
            "restored_vars": restore_result.get("restored_count", 0) if preserve_state else 0,
            "timestamp": time.time()
        }
        
    except Exception as e:
        await ctx.error(f"Failed to restart kernel: {str(e)}")
        raise ToolError(f"Failed to restart kernel: {str(e)}")

@mcp.tool
async def get_workspace_info(ctx: Context) -> dict:
    """Return absolute paths for the active workspace layout.

    Args:
        ctx: FastMCP request context.

    Returns:
        dict: {workspace, scripts, outputs, uploads} absolute paths.
    """
    await ctx.debug("Getting workspace info")
    return {
        "workspace": str(WORKSPACE_DIR),
        "scripts": str(SCRIPTS_DIR),
        "outputs": str(OUTPUTS_DIR),
        "uploads": str(UPLOADS_DIR),
    }

@mcp.tool
async def get_kernel_health(ctx: Context) -> dict:
    """Get comprehensive kernel health metrics and diagnostics.
    
    Args:
        ctx: FastMCP request context.
        
    Returns:
        dict: Comprehensive kernel health information including uptime, memory usage,
              execution statistics, and process information.
    """
    await ctx.debug("Getting kernel health metrics")
    
    health_metrics = kernel_manager.get_health_metrics()
    
    # Add system-level information
    try:
        system_info = {
            "system_memory_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
            "system_cpu_percent": psutil.cpu_percent(interval=0.1),
            "disk_free_gb": round(psutil.disk_usage(str(WORKSPACE_DIR)).free / 1024 / 1024 / 1024, 2)
        }
        health_metrics["system"] = system_info
    except Exception as e:
        health_metrics["system"] = {"error": f"Could not get system info: {str(e)}"}
    
    await ctx.info(f"Kernel status: {health_metrics['status']}, uptime: {health_metrics.get('uptime', 0)}s")
    return health_metrics

@mcp.tool  
async def check_kernel_responsiveness(ctx: Context, timeout: float = 5.0) -> dict:
    """Check if the kernel is responsive by sending a test request.
    
    Args:
        ctx: FastMCP request context.
        timeout: Maximum time to wait for kernel response in seconds.
        
    Returns:
        dict: Responsiveness check results including response time and status.
    """
    await ctx.debug(f"Checking kernel responsiveness with timeout: {timeout}s")
    
    start_time = time.time()
    is_responsive = kernel_manager.is_responsive(timeout)
    response_time = time.time() - start_time
    
    result = {
        "responsive": is_responsive,
        "response_time": round(response_time, 3),
        "timeout": timeout
    }
    
    if is_responsive:
        await ctx.info(f"Kernel is responsive (response time: {response_time:.3f}s)")
    else:
        await ctx.warning(f"Kernel is not responsive after {timeout}s timeout")
        
    return result

@mcp.tool
async def create_session(ctx: Context, session_id: str = None, description: str = None) -> dict:
    """Create a new isolated kernel session.
    
    Each session runs its own independent Python kernel with isolated state.
    
    Args:
        ctx: FastMCP request context.
        session_id: Optional custom session ID. If not provided, will auto-generate one.
        description: Optional description/metadata for the session.
        
    Returns:
        dict: Information about the created session including its ID.
    """
    await ctx.info(f"Creating new kernel session: {session_id or 'auto-generated'}")
    
    metadata = {}
    if description:
        metadata["description"] = description
        metadata["created_at"] = time.time()
    
    try:
        created_session_id = kernel_manager._session_manager.create_session(session_id, metadata)
        await ctx.info(f"Successfully created session: {created_session_id}")
        
        return {
            "session_id": created_session_id,
            "status": "created",
            "metadata": metadata,
            "timestamp": time.time()
        }
    except Exception as e:
        await ctx.error(f"Failed to create session: {str(e)}")
        raise ToolError(f"Failed to create session: {str(e)}")

@mcp.tool
async def switch_session(session_id: str, ctx: Context) -> dict:
    """Switch to a different kernel session.
    
    All subsequent operations will execute in the specified session.
    
    Args:
        session_id: The ID of the session to switch to.
        ctx: FastMCP request context.
        
    Returns:
        dict: Information about the session switch including previous and new active sessions.
    """
    previous_session = kernel_manager._session_manager.active_session_id
    await ctx.info(f"Switching from session '{previous_session}' to '{session_id}'")
    
    try:
        kernel_manager._session_manager.switch_session(session_id)
        await ctx.info(f"Successfully switched to session: {session_id}")
        
        return {
            "previous_session": previous_session,
            "current_session": session_id,
            "status": "switched",
            "timestamp": time.time()
        }
    except Exception as e:
        await ctx.error(f"Failed to switch session: {str(e)}")
        raise ToolError(f"Failed to switch session: {str(e)}")

@mcp.tool
async def list_sessions(ctx: Context) -> dict:
    """List all available kernel sessions and their status.
    
    Shows information about all sessions including which one is currently active.
    
    Args:
        ctx: FastMCP request context.
        
    Returns:
        dict: Information about all sessions including status, execution counts, and metadata.
    """
    await ctx.debug("Retrieving list of all kernel sessions")
    
    sessions_info = kernel_manager._session_manager.list_sessions()
    
    # Add health metrics for active sessions
    detailed_sessions = {}
    for session_id, info in sessions_info["sessions"].items():
        detailed_info = info.copy()
        if info["active"]:
            try:
                session = kernel_manager._session_manager.get_session(session_id)
                health = session.get_health_metrics()
                detailed_info["health"] = health
            except Exception:
                detailed_info["health"] = {"status": "error", "error": "Could not get health metrics"}
        detailed_sessions[session_id] = detailed_info
    
    result = {
        **sessions_info,
        "sessions": detailed_sessions,
        "timestamp": time.time()
    }
    
    await ctx.info(f"Found {len(detailed_sessions)} sessions, active: {sessions_info['active_session']}")
    return result

@mcp.tool
async def delete_session(session_id: str, ctx: Context) -> dict:
    """Delete a kernel session and free its resources.
    
    Note: Cannot delete the default session. All operations in the session will be terminated.
    
    Args:
        session_id: The ID of the session to delete.
        ctx: FastMCP request context.
        
    Returns:
        dict: Information about the deletion operation.
    """
    await ctx.warning(f"Deleting session: {session_id}")
    
    try:
        was_active = session_id == kernel_manager._session_manager.active_session_id
        success = kernel_manager._session_manager.delete_session(session_id)
        
        if success:
            await ctx.info(f"Successfully deleted session: {session_id}")
            result = {
                "session_id": session_id,
                "status": "deleted",
                "was_active": was_active,
                "timestamp": time.time()
            }
            
            if was_active:
                result["new_active_session"] = kernel_manager._session_manager.active_session_id
                await ctx.info(f"Switched to default session: {result['new_active_session']}")
            
            return result
        else:
            raise ToolError(f"Session '{session_id}' does not exist")
            
    except Exception as e:
        await ctx.error(f"Failed to delete session: {str(e)}")
        raise ToolError(f"Failed to delete session: {str(e)}")

@mcp.custom_route("/files/upload", methods=["POST"])
async def upload_file(request: Request):
    """Handles file uploads."""
    form = await request.form()
    upload_file = form["file"]
    raw_name = Path(upload_file.filename).name
    try:
        filepath = _ensure_within_workspace(UPLOADS_DIR / raw_name)
    except Exception:
        return JSONResponse({"error": "Invalid path"}, status_code=400)
    with open(filepath, "wb") as f:
        f.write(await upload_file.read())
    return JSONResponse({"filename": filepath.name})

@mcp.custom_route("/files/download/{path:path}", methods=["GET"])
async def download_file(request: Request):
    """Serves a file from the workspace directory."""
    path = request.path_params['path']
    try:
        filepath = _ensure_within_workspace(Path(path))
    except Exception:
        return JSONResponse({"error": "Invalid path"}, status_code=400)
    if not filepath.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(filepath)


def main():
    """Main entry point for the Python MCP Server."""
    parser = argparse.ArgumentParser(description="Python Interpreter MCP")
    parser.add_argument("--workspace", type=str, default=os.environ.get("MCP_WORKSPACE_DIR", "workspace"), help="Workspace directory for files, scripts, outputs")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # Recompute directories if overridden via CLI
    ws = Path(args.workspace).resolve()
    if ws != WORKSPACE_DIR:
        globals()["WORKSPACE_DIR"] = ws
        globals()["SCRIPTS_DIR"] = (ws / "scripts").resolve()
        globals()["OUTPUTS_DIR"] = (ws / "outputs").resolve()
        globals()["UPLOADS_DIR"] = (ws / "uploads").resolve()
        for d in (WORKSPACE_DIR, SCRIPTS_DIR, OUTPUTS_DIR, UPLOADS_DIR):
            d.mkdir(parents=True, exist_ok=True)

    mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
