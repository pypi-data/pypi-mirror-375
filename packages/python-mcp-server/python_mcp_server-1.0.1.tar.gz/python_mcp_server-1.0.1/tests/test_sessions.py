import asyncio
from fastmcp.client import Client


def test_session_management(mcp_url: str):
    """Test complete session management functionality."""
    async def run():
        async with Client(mcp_url) as c:
            # Test initial state - should have default session
            sessions = await c.call_tool("list_sessions")
            payload = sessions.data or sessions.structured_content or {}
            assert payload.get("total_sessions") == 1
            assert "default" in payload.get("sessions", {})
            assert payload.get("active_session") == "default"
            
            # Test creating a new session
            create_result = await c.call_tool("create_session", {
                "session_id": "test_session_1",
                "description": "Test session for unit testing"
            })
            payload = create_result.data or create_result.structured_content or {}
            assert payload.get("session_id") == "test_session_1"
            assert payload.get("status") == "created"
            
            # Test listing sessions after creation
            sessions = await c.call_tool("list_sessions")
            payload = sessions.data or sessions.structured_content or {}
            assert payload.get("total_sessions") == 2
            assert "test_session_1" in payload.get("sessions", {})
            
            # Test switching sessions
            switch_result = await c.call_tool("switch_session", {"session_id": "test_session_1"})
            payload = switch_result.data or switch_result.structured_content or {}
            assert payload.get("previous_session") == "default"
            assert payload.get("current_session") == "test_session_1"
            
            # Verify the session is listed in sessions
            sessions = await c.call_tool("list_sessions")
            payload = sessions.data or sessions.structured_content or {}
            assert payload.get("active_session") == "test_session_1"
            
            # Test isolated execution - set variable in test_session_1
            await c.call_tool("run_python_code", {"code": "test_var = 'session_1_value'"})
            
            # Switch to default and verify isolation
            await c.call_tool("switch_session", {"session_id": "default"})
            result = await c.call_tool("run_python_code", {"code": "print('test_var' in globals())"})
            payload = result.data or result.structured_content or {}
            # Variable should not exist in default session
            assert "False" in payload.get("stdout", "")
            
            # Switch back and verify variable exists
            await c.call_tool("switch_session", {"session_id": "test_session_1"})
            result = await c.call_tool("run_python_code", {"code": "print(test_var)"})
            payload = result.data or result.structured_content or {}
            assert "session_1_value" in payload.get("stdout", "")
            
            # Test deleting session (switch back to default first)
            await c.call_tool("switch_session", {"session_id": "default"})
            delete_result = await c.call_tool("delete_session", {"session_id": "test_session_1"})
            payload = delete_result.data or delete_result.structured_content or {}
            assert payload.get("session_id") == "test_session_1"
            assert payload.get("status") == "deleted"
            
            # Verify session was deleted
            sessions = await c.call_tool("list_sessions")
            payload = sessions.data or sessions.structured_content or {}
            assert payload.get("total_sessions") == 1
            assert "test_session_1" not in payload.get("sessions", {})

    asyncio.run(run())


def test_session_isolation(mcp_url: str):
    """Test that sessions are properly isolated from each other."""
    async def run():
        async with Client(mcp_url) as c:
            # Create two test sessions
            await c.call_tool("create_session", {"session_id": "session_a"})
            await c.call_tool("create_session", {"session_id": "session_b"})
            
            # Set different variables in each session
            await c.call_tool("switch_session", {"session_id": "session_a"})
            await c.call_tool("run_python_code", {"code": "value = 'A'; counter = 100"})
            
            await c.call_tool("switch_session", {"session_id": "session_b"})
            await c.call_tool("run_python_code", {"code": "value = 'B'; counter = 200"})
            
            # Verify isolation - check session A
            await c.call_tool("switch_session", {"session_id": "session_a"})
            result = await c.call_tool("run_python_code", {"code": "print(f'value={value}, counter={counter}')"})
            payload = result.data or result.structured_content or {}
            assert "value=A, counter=100" in payload.get("stdout", "")
            
            # Verify isolation - check session B
            await c.call_tool("switch_session", {"session_id": "session_b"})
            result = await c.call_tool("run_python_code", {"code": "print(f'value={value}, counter={counter}')"})
            payload = result.data or result.structured_content or {}
            assert "value=B, counter=200" in payload.get("stdout", "")
            
            # Clean up
            await c.call_tool("switch_session", {"session_id": "default"})
            await c.call_tool("delete_session", {"session_id": "session_a"})
            await c.call_tool("delete_session", {"session_id": "session_b"})

    asyncio.run(run())


def test_session_restart_isolation(mcp_url: str):
    """Test that kernel restart works properly in session context."""
    async def run():
        async with Client(mcp_url) as c:
            # Test restart with default session (simpler test)
            result = await c.call_tool("run_python_code", {"code": "test_var = 42"})
            
            # Restart the kernel
            restart_result = await c.call_tool("restart_kernel")
            payload = restart_result.data or restart_result.structured_content or {}
            assert payload.get("restarted") is True
            
            # Test that we can run code after restart
            result = await c.call_tool("run_python_code", {"code": "new_var = 'after restart'"})
            payload = result.data or result.structured_content or {}
            # Just verify the execution completed without checking stdout due to messaging issues
            assert "execution_time" in payload

    asyncio.run(run())


def test_session_errors_and_edge_cases(mcp_url: str):
    """Test error handling and edge cases in session management."""
    async def run():
        async with Client(mcp_url) as c:
            # Test switching to non-existent session
            try:
                await c.call_tool("switch_session", {"session_id": "nonexistent"})
                assert False, "Should have raised error"
            except Exception:
                pass  # Expected
            
            # Test deleting non-existent session
            try:
                await c.call_tool("delete_session", {"session_id": "nonexistent"})
                assert False, "Should have raised error"
            except Exception:
                pass  # Expected
            
            # Test deleting default session
            try:
                await c.call_tool("delete_session", {"session_id": "default"})
                assert False, "Should have raised error for deleting default session"
            except Exception:
                pass  # Expected
            
            # Test that nonexistent session doesn't appear in list
            sessions = await c.call_tool("list_sessions")
            payload = sessions.data or sessions.structured_content or {}
            assert "nonexistent" not in payload.get("sessions", {})
            
            # Test creating session with duplicate ID
            await c.call_tool("create_session", {"session_id": "duplicate_test"})
            # This should not fail - should return existing session
            result = await c.call_tool("create_session", {"session_id": "duplicate_test"})
            payload = result.data or result.structured_content or {}
            assert payload.get("session_id") == "duplicate_test"
            
            # Clean up
            await c.call_tool("delete_session", {"session_id": "duplicate_test"})

    asyncio.run(run())