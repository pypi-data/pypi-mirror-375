"""Python MCP Server - A world-class Python interpreter MCP server with session management and health monitoring.

This package provides a FastMCP-based server that offers:
- Python code execution with Jupyter kernel backend
- Session-based isolation for multiple concurrent workflows  
- Health monitoring and kernel management
- File system operations within sandboxed workspace
- Dependency installation and package management
"""

from .server import main

__version__ = "1.0.1"
__author__ = "DeadMeme5441"
__email__ = "deadunderscorememe@gmail.com"

__all__ = ["main"]
