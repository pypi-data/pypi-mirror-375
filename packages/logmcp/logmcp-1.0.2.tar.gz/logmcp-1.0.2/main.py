#!/usr/bin/env python3
"""
LogMCP Server Entry Point

This is the main entry point for the LogMCP server.
It provides a MCP (Model Context Protocol) server implementation
that uses stdio transport for communication and integrates with Loki
for log querying and system monitoring.

Usage:
    python main.py

Environment Variables:
    LOKI_GATEWAY_URL: Loki gateway URL (default: http://loki-gateway.loki:80)
    LOKI_TIMEOUT: Loki query timeout in seconds (default: 30)
    LOKI_DEFAULT_LIMIT: Default query result limit (default: 1000)
    MCP_SERVER_NAME: MCP server name (default: LogMCP Server)
    LOG_LEVEL: Logging level (default: INFO)
    DEFAULT_SERVICE: Default service name (default: zkme-token)
    TEST_NAMESPACE: Test environment namespace (default: zkme-test)
    DEV_NAMESPACE: Dev environment namespace (default: zkme-dev)
    PROD_NAMESPACE: Prod environment namespace (default: zkme-prod)
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logmcp.server import main

if __name__ == "__main__":
    main()
