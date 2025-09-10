"""
LogMCP - MCP server for log querying and system monitoring via Loki

This package provides a Model Context Protocol (MCP) server implementation
that uses stdio transport for communication and integrates with Loki for
log querying and system monitoring.
"""

__version__ = "1.0.0"
__author__ = "LogMCP Team"

from .server import LogMCPServer
from .tools import register_tools
from .config import config

__all__ = ["LogMCPServer", "register_tools", "config"]
