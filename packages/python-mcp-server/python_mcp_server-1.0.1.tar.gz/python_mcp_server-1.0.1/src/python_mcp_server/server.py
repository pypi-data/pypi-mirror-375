import asyncio
import base64
import atexit
import uuid
import os
import sys
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

# Ensure consistent interpreter and plotting backend by default
os.environ.setdefault("PYTHON", sys.executable)
os.environ.setdefault("MPLBACKEND", "Agg")

# Configurable interpreter/venv/PYTHONPATH (set via CLI in main())
SELECTED_PYTHON = os.environ.get("PYTHON", sys.executable)
VENV_PATH: str | None = None
EXTRA_PYTHONPATH: list[str] = []

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
        self.state_operations = 60.0    # State save/restore & dataset ops (CI-safe)
        
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
            
        # Build environment for the kernel
        env = os.environ.copy()
        # Prepend venv bin/Scripts if configured
        if VENV_PATH:
            bin_dir = Path(VENV_PATH) / ("Scripts" if os.name == "nt" else "bin")
            env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
            env["VIRTUAL_ENV"] = VENV_PATH
        # Extend PYTHONPATH if provided
        if EXTRA_PYTHONPATH:
            env["PYTHONPATH"] = os.pathsep.join(EXTRA_PYTHONPATH + [env.get("PYTHONPATH", "")])
        env.setdefault("MPLBACKEND", "Agg")

        # Explicit kernel command to ensure interpreter parity
        kernel_cmd = [SELECTED_PYTHON, "-m", "ipykernel", "-f", "{connection_file}"]

        self.km = KernelManager(kernel_cmd=kernel_cmd)
        cwd_dir = str(WORKSPACE_DIR) if 'WORKSPACE_DIR' in globals() else os.getcwd()
        self.km.start_kernel(env=env, cwd=cwd_dir)
        self.start_time = time.time()
        self.client = self.km.client()
        self.client.start_channels()
        self.is_active = True
        print(f"Kernel Session '{self.session_id}' Started", file=sys.stderr)
        
    def stop(self):
        """Stop this kernel session."""
        if not self.is_active:
            return
            
        if self.km and self.km.is_alive():
            self.km.shutdown_kernel(now=True)
        self.is_active = False
        print(f"Kernel Session '{self.session_id}' Stopped", file=sys.stderr)
        
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
            print("Session-based Kernel Manager Initialized", file=sys.stderr)
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


def create_app():
    """Create and initialize the MCP server application.
    
    This function is primarily for testing purposes to ensure workspace
    directories are created and the server is properly initialized.
    
    Returns:
        FastMCP: The configured MCP server instance
    """
    # Ensure all workspace directories exist
    for d in (WORKSPACE_DIR, SCRIPTS_DIR, OUTPUTS_DIR, UPLOADS_DIR):
        d.mkdir(parents=True, exist_ok=True)
    
    return mcp


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

# --- Notebook Manager (sessions, manifests, datasets) ---

MAX_CONCURRENT_CELLS = int(os.environ.get("MCP_MAX_CONCURRENT_CELLS", "3"))
SERVER_MEMORY_BUDGET_MB = int(os.environ.get("MCP_MEMORY_BUDGET_MB", "4096"))
SOFT_WATERMARK = float(os.environ.get("MCP_SOFT_WATERMARK", "0.7"))
HARD_WATERMARK = float(os.environ.get("MCP_HARD_WATERMARK", "0.85"))


class NotebookSession:
    def __init__(self, notebook_id: str):
        self.id = notebook_id
        self.lock = asyncio.Lock()
        self.next_cell = 1
        self.created_at = time.time()
        self.manifest_dir = OUTPUTS_DIR / "notebooks" / notebook_id
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.manifest_dir / "index.json"
        if not self.index_path.exists():
            self._write_index({"notebook_id": notebook_id, "created_at": self.created_at, "cells": []})

    def _read_index(self) -> dict:
        try:
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        except Exception:
            return {"notebook_id": self.id, "created_at": self.created_at, "cells": []}

    def _write_index(self, data: dict):
        tmp = self.index_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.index_path)

    def add_cell(self, cell_info: dict) -> None:
        index = self._read_index()
        index.setdefault("cells", []).append(cell_info)
        self._write_index(index)


class NotebookManager:
    def __init__(self):
        self.sessions: Dict[str, NotebookSession] = {}
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_CELLS)

    def get_or_create(self, notebook_id: str | None) -> NotebookSession:
        nid = notebook_id or str(uuid.uuid4())
        if nid not in self.sessions:
            self.sessions[nid] = NotebookSession(nid)
        return self.sessions[nid]

    def reset(self, notebook_id: str) -> bool:
        sess = self.sessions.get(notebook_id)
        if not sess:
            return False
        try:
            for p in sess.manifest_dir.glob("cell_*_manifest.json"):
                try:
                    p.unlink()
                except Exception:
                    pass
            sess._write_index({"notebook_id": sess.id, "created_at": sess.created_at, "cells": []})
            sess.next_cell = 1
            return True
        except Exception:
            return False


notebooks = NotebookManager()


async def _exec_json(ctx: Context, code: str, timeout: float, sentinel: str = "NOTEBOOK_JSON:") -> dict:
    """Execute code and parse a JSON object from stdout prefixed by sentinel."""
    client = kernel_manager.get_client()
    if not client:
        raise ToolError("Kernel client is not available")
    msg_id = client.execute(code)
    start = time.time()
    while time.time() - start < timeout:
        try:
            msg = client.get_iopub_msg(timeout=1)
            if msg.get('parent_header', {}).get('msg_id') != msg_id:
                continue
            if msg['header']['msg_type'] == 'stream' and msg['content']['name'] == 'stdout':
                text = msg['content']['text']
                if sentinel in text:
                    payload = text.split(sentinel, 1)[1].strip()
                    try:
                        return json.loads(payload)
                    except Exception as e:
                        raise ToolError(f"Failed to parse JSON from kernel: {e}")
            elif msg['header']['msg_type'] in ('display_data', 'execute_result'):
                data = msg['content'].get('data', {})
                if 'application/json' in data:
                    return data['application/json']
            elif msg['header']['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                # Execution finished but no sentinel was seen; allow a brief grace period
                grace_start = time.time()
                while time.time() - grace_start < 0.5:
                    try:
                        follow = client.get_iopub_msg(timeout=0.1)
                        if follow.get('parent_header', {}).get('msg_id') != msg_id:
                            continue
                        if follow['header']['msg_type'] == 'stream' and follow['content']['name'] == 'stdout':
                            text2 = follow['content']['text']
                            if sentinel in text2:
                                return json.loads(text2.split(sentinel, 1)[1].strip())
                        elif follow['header']['msg_type'] in ('display_data', 'execute_result'):
                            data2 = follow['content'].get('data', {})
                            if 'application/json' in data2:
                                return data2['application/json']
                    except Exception:
                        pass
                return {"error": "no-json"}
        except Exception:
            continue
    raise ToolError("Timed out waiting for JSON response from kernel")


def _make_abs_glob(paths: list[str]) -> list[str]:
    abs_paths: list[str] = []
    for p in paths:
        ap = _ensure_within_workspace(Path(p))
        abs_paths.append(str(ap))
    return abs_paths


@mcp.tool
async def notebook(
    ctx: Context,
    action: str,
    notebook_id: str | None = None,
    code: str | None = None,
    save_dfs: bool = False,
    dataset_name: str | None = None,
    paths: list[str] | None = None,
    format: str | None = None,
    engine: str = "duckdb",
    query: str | None = None,
    limit_preview: int = 1000,
    cell_index: int | None = None,
    export_to: str = "both"
) -> dict:
    """Unified notebook surface with cell execution and dataset actions.

    Actions:
      - run: execute a cell, capture artifacts, write manifest, return paths
      - cells: list executed cells
      - cell: return a single cell's manifest
      - export: export .ipynb and/or HTML index
      - reset: clear manifests and counters (kernel is not restarted)
      - datasets.register/list/describe/drop/sql (duckdb default)
    """
    vm = psutil.virtual_memory()
    if vm.total > 0 and (vm.used / vm.total) > HARD_WATERMARK:
        raise ToolError("RESOURCE_LIMIT: memory watermark exceeded; try later")

    sess = notebooks.get_or_create(notebook_id)

    if action == "run":
        if not code:
            raise ToolError("'code' is required for action=run")
        async with notebooks.semaphore:
            async with sess.lock:
                async def exec_op(timeout: float, context_msg: str):
                    return await _execute_code_with_timeout(code, ctx, timeout, context_msg)

                result = await kernel_manager.execute_with_retry(
                    f"Notebook cell execution #{sess.next_cell}",
                    exec_op,
                    base_timeout=kernel_manager._timeout_config.code_execution,
                )

                df_manifest: dict[str, Any] = {"dataframes": []}
                if save_dfs:
                    cell_tag = f"cell_{sess.next_cell}"
                    save_code = f"""
import json, os
from pathlib import Path
import pandas as pd
_out = []
for _k,_v in list(globals().items()):
    try:
        import pandas as pd
        if isinstance(_v, pd.DataFrame):
            _rows, _cols = _v.shape
            _base = f"{cell_tag}_{{_k}}"
            _dir = r"{str((OUTPUTS_DIR / 'data' / sess.id).as_posix())}"
            Path(_dir).mkdir(parents=True, exist_ok=True)
            _parquet = os.path.join(_dir, _base + ".parquet")
            try:
                _v.to_parquet(_parquet)
                _saved = _parquet
            except Exception:
                _csv = os.path.join(_dir, _base + ".csv")
                _v.to_csv(_csv, index=False)
                _saved = _csv
            _head_csv = os.path.join(_dir, _base + "_head.csv")
            _v.head(50).to_csv(_head_csv, index=False)
            _out.append({"name": _k, "rows": _rows, "cols": _cols, "path": _saved, "preview_path": _head_csv})
    except Exception:
        pass
print("NOTEBOOK_JSON:" + json.dumps({"dataframes": _out}))
"""
                    df_manifest = await _exec_json(ctx, save_code, timeout=kernel_manager._timeout_config.state_operations)

                manifest = {
                    "notebook_id": sess.id,
                    "cell_index": sess.next_cell,
                    "created_at": time.time(),
                    "code": code,
                    "stdout": result.get("stdout", "")[:65536],
                    "stderr": result.get("stderr", "")[:65536],
                    "outputs": result.get("outputs", []),
                    "results": result.get("results", []),
                    "new_files": result.get("new_files", []),
                    **df_manifest,
                }
                manifest_path = sess.manifest_dir / f"cell_{sess.next_cell:04d}_manifest.json"
                manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

                sess.add_cell({
                    "cell_index": sess.next_cell,
                    "created_at": manifest["created_at"],
                    "n_outputs": len(manifest.get("outputs", [])),
                    "n_dataframes": len(manifest.get("dataframes", [])),
                })

                sess.next_cell += 1
                return {
                    "status": "completed",
                    "notebook_id": sess.id,
                    "cell_index": sess.next_cell - 1,
                    "manifest": str(manifest_path.relative_to(WORKSPACE_DIR)),
                    "artifacts": manifest.get("outputs", []) + [df.get("path") for df in manifest.get("dataframes", []) if df.get("path")],
                }

    if action == "cells":
        idx = json.loads((sess.index_path).read_text(encoding="utf-8"))
        return idx

    if action == "cell":
        if cell_index is None:
            raise ToolError("'cell_index' is required for action=cell")
        path = sess.manifest_dir / f"cell_{int(cell_index):04d}_manifest.json"
        if not path.exists():
            raise ToolError(f"Cell {cell_index} not found")
        return json.loads(path.read_text(encoding="utf-8"))

    if action == "export":
        ipynb_path = OUTPUTS_DIR / "notebooks" / f"{sess.id}.ipynb"
        try:
            import nbformat as nbf
            nb = nbf.v4.new_notebook()
            index = json.loads(sess.index_path.read_text(encoding="utf-8"))
            cells = []
            for entry in index.get("cells", []):
                cpath = sess.manifest_dir / f"cell_{entry['cell_index']:04d}_manifest.json"
                manifest = json.loads(cpath.read_text(encoding="utf-8"))
                cells.append(nbf.v4.new_code_cell(manifest.get("code", "")))
                outputs = []
                if manifest.get("stdout"):
                    outputs.append(nbf.v4.new_output("stream", name="stdout", text=manifest["stdout"]))
                if manifest.get("stderr"):
                    outputs.append(nbf.v4.new_output("stream", name="stderr", text=manifest["stderr"]))
                cells[-1]["outputs"] = outputs
            nb["cells"] = cells
            ipynb_path.parent.mkdir(parents=True, exist_ok=True)
            with open(ipynb_path, "w", encoding="utf-8") as f:
                nbf.write(nb, f)
            html_path = OUTPUTS_DIR / "notebooks" / f"{sess.id}.html"
            html_done = False
            if export_to in ("html", "both"):
                try:
                    from nbconvert import HTMLExporter
                    exp = HTMLExporter()
                    (body, _) = exp.from_notebook_node(nb)
                    html_path.write_text(body, encoding="utf-8")
                    html_done = True
                except Exception:
                    links = []
                    index = json.loads(sess.index_path.read_text(encoding="utf-8"))
                    for entry in index.get("cells", []):
                        rel = str((sess.manifest_dir / f"cell_{entry['cell_index']:04d}_manifest.json").relative_to(WORKSPACE_DIR))
                        links.append(f"<li><a href='/files/download/{rel}'>Cell {entry['cell_index']}</a></li>")
                    html_path.write_text("<ul>" + "\n".join(links) + "</ul>", encoding="utf-8")
                    html_done = True
            return {
                "ipynb": str(ipynb_path.relative_to(WORKSPACE_DIR)),
                "html": str(html_path.relative_to(WORKSPACE_DIR)) if export_to in ("html", "both") and html_done else None,
            }
        except Exception as e:
            return {"index": str(sess.index_path.relative_to(WORKSPACE_DIR)), "error": str(e)}

    if action == "reset":
        if notebooks.reset(sess.id):
            return {"status": "reset", "notebook_id": sess.id}
        raise ToolError("Failed to reset notebook")

    if action == "datasets.register":
        if not dataset_name or not paths:
            raise ToolError("'dataset_name' and 'paths' are required")
        abs_globs = _make_abs_glob(paths)
        fmt = (format or "parquet").lower()
        if engine != "duckdb":
            raise ToolError("Only engine='duckdb' is supported currently")
        code = ("""
import duckdb, json
_emit = lambda obj: print('NOTEBOOK_JSON:' + json.dumps(obj))
try:
    if 'DUCKDB_CONN' not in globals():
        DUCKDB_CONN = duckdb.connect()
    if 'DATASETS_DUCKDB' not in globals():
        DATASETS_DUCKDB = {}
    _name = %(name_json)s
    _paths = %(paths_json)s
    _fmt = %(fmt_json)s
    def _qident(s: str) -> str:
        return '"' + s.replace('"','""') + '"'
    # Build view using safely quoted literals (DuckDB doesn't allow preparing these statements)
    def _qlit(s: str) -> str:
        return "'" + s.replace("'","''") + "'"
    if isinstance(_paths, list) and len(_paths) > 1:
        if _fmt == 'parquet':
            selects = ["SELECT * FROM read_parquet(" + _qlit(p) + ")" for p in _paths]
        else:
            selects = ["SELECT * FROM read_csv_auto(" + _qlit(p) + ")" for p in _paths]
        sql = "CREATE OR REPLACE VIEW " + _qident(_name) + " AS " + " UNION ALL ".join(selects)
        DUCKDB_CONN.execute(sql)
    else:
        _glob = _paths if isinstance(_paths, str) else _paths[0]
        if _fmt == 'parquet':
            DUCKDB_CONN.execute("CREATE OR REPLACE VIEW " + _qident(_name) + " AS SELECT * FROM read_parquet(" + _qlit(_glob) + ")")
        else:
            DUCKDB_CONN.execute("CREATE OR REPLACE VIEW " + _qident(_name) + " AS SELECT * FROM read_csv_auto(" + _qlit(_glob) + ")")
    DATASETS_DUCKDB[_name] = {"paths": _paths if isinstance(_paths, list) else [_paths], "format": _fmt}
    _schema = DUCKDB_CONN.execute("PRAGMA table_info(" + _qident(_name) + ")").fetchall()
    _cols = [[r[1], r[2]] for r in _schema]
    _head = DUCKDB_CONN.execute("SELECT * FROM " + _qident(_name) + " LIMIT 50").fetchall()
    _emit({"name": _name, "paths": DATASETS_DUCKDB[_name]["paths"], "format": _fmt, "schema": _cols, "head": _head})
except Exception as e:
    _emit({"error": str(e)})
""" % {
            "name_json": json.dumps(dataset_name),
            "paths_json": json.dumps(abs_globs if len(abs_globs) > 1 else abs_globs[0]),
            "fmt_json": json.dumps(fmt),
        })
        data = await _exec_json(ctx, code, timeout=kernel_manager._timeout_config.state_operations)
        return data

    if action == "datasets.list":
        code = """
import json
datasets = []
if 'DATASETS_DUCKDB' in globals():
    for k,v in DATASETS_DUCKDB.items():
        datasets.append({"name": k, **v})
print("NOTEBOOK_JSON:" + json.dumps({"duckdb": datasets}))
"""
        return await _exec_json(ctx, code, timeout=kernel_manager._timeout_config.kernel_response)

    if action == "datasets.describe":
        if not dataset_name:
            raise ToolError("'dataset_name' is required")
        code = ("""
import duckdb, json
_emit = lambda obj: print('NOTEBOOK_JSON:' + json.dumps(obj))
try:
    if 'DUCKDB_CONN' not in globals():
        DUCKDB_CONN = duckdb.connect()
    def _qident(s: str) -> str:
        return '"' + s.replace('"','""') + '"'
    _schema = DUCKDB_CONN.execute("PRAGMA table_info(" + _qident('%(name)s') + ")").fetchall()
    _cols = [[r[1], r[2]] for r in _schema]
    _head = DUCKDB_CONN.execute("SELECT * FROM " + _qident('%(name)s') + " LIMIT 50").fetchall()
    _emit({"schema": _cols, "head": _head})
except Exception as e:
    _emit({"error": str(e)})
""" % {"name": dataset_name})
        return await _exec_json(ctx, code, timeout=kernel_manager._timeout_config.kernel_response)

    if action == "datasets.drop":
        if not dataset_name:
            raise ToolError("'dataset_name' is required")
        code = ("""
import duckdb, json
_emit = lambda obj: print('NOTEBOOK_JSON:' + json.dumps(obj))
try:
    if 'DUCKDB_CONN' not in globals():
        DUCKDB_CONN = duckdb.connect()
    try:
        DUCKDB_CONN.execute("DROP VIEW IF EXISTS %(name)s")
    except Exception:
        pass
    if 'DATASETS_DUCKDB' in globals():
        DATASETS_DUCKDB.pop("%(name)s", None)
    _emit({"dropped": "%(name)s"})
except Exception as e:
    _emit({"error": str(e)})
""" % {"name": dataset_name})
        return await _exec_json(ctx, code, timeout=kernel_manager._timeout_config.kernel_response)

    if action == "datasets.sql":
        if not query:
            raise ToolError("'query' is required for datasets.sql")
        out_dir = OUTPUTS_DIR / "data" / sess.id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"cell_{sess.next_cell:04d}_query_{uuid.uuid4().hex}.parquet"
        _query_json = json.dumps(query)
        _out_path = str(out_file.as_posix())
        _rel_path = str(out_file.relative_to(WORKSPACE_DIR))
        code = ("""
import duckdb, json
_emit = lambda obj: print('NOTEBOOK_JSON:' + json.dumps(obj))
try:
    if 'DUCKDB_CONN' not in globals():
        DUCKDB_CONN = duckdb.connect()
    _res = DUCKDB_CONN.execute(%(query_json)s)
    _preview = _res.fetchmany(%(limit)d)
    _cols = [d[0] for d in _res.description]
    # COPY doesn't support prepared parameters for file path; use quoted literal
    def _qlit(s: str) -> str:
        return "'" + s.replace("'","''") + "'"
    DUCKDB_CONN.execute("COPY (" + %(query_json)s + ") TO " + _qlit('%(out_path)s') + " (FORMAT PARQUET)")
    _emit({"columns": _cols, "rows": _preview, "result_path": "%(rel_path)s"})
except Exception as e:
    _emit({"error": str(e)})
""" % {
            "query_json": _query_json,
            "limit": min(limit_preview, 10000),
            "out_path": _out_path,
            "rel_path": _rel_path,
        })
        return await _exec_json(ctx, code, timeout=kernel_manager._timeout_config.state_operations)

    raise ToolError(f"Unknown action: {action}")

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
    parser.add_argument("--transport", type=str, default="stdio", choices=["stdio", "http"], help="Transport mode (default: stdio)")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--python", type=str, default=os.environ.get("PYTHON", sys.executable), help="Path to python interpreter to use for the kernel and subprocesses")
    parser.add_argument("--venv", type=str, default=None, help="Path to a virtual environment to activate for the kernel and subprocesses")
    parser.add_argument("--pythonpath", type=str, default=None, help="Extra PYTHONPATH entries (colon/semicolon-separated)")
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

    # Apply interpreter/venv/PYTHONPATH configuration
    global SELECTED_PYTHON, VENV_PATH, EXTRA_PYTHONPATH
    SELECTED_PYTHON = args.python or sys.executable
    os.environ["PYTHON"] = SELECTED_PYTHON
    VENV_PATH = args.venv
    if args.pythonpath:
        EXTRA_PYTHONPATH = [p for p in args.pythonpath.split(os.pathsep) if p]
    # Ensure MPL is headless
    os.environ.setdefault("MPLBACKEND", "Agg")
    # Restart active session kernel to apply new environment, if already running
    try:
        session = kernel_manager._session_manager.get_session()
        if session.is_active:
            session.stop()
            session.start()
    except Exception:
        pass

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
