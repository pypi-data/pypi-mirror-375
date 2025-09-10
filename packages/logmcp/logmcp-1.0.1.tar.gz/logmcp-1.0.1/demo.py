#!/usr/bin/env python3
"""
Demo script showing LogMCP server capabilities
"""

import asyncio
import sys
import os
from unittest.mock import patch

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastmcp import FastMCP
from logmcp.tools import register_tools
from logmcp.services.loki_service import LokiService


def demo_loki_service():
    """Demonstrate Loki service capabilities"""
    print("=== Loki Service Demo ===\n")
    
    service = LokiService()
    
    # Demo 1: Keyword parsing
    print("1. Keyword Parsing:")
    keywords = service._parse_keywords_input("error, warning, exception")
    print(f"   Input: 'error, warning, exception'")
    print(f"   Parsed: {keywords}")
    
    # Demo 2: Query building
    print("\n2. LogQL Query Building:")
    query = service._build_loki_query("zkme-prod", "zkme-token", keywords)
    print(f"   Namespace: zkme-prod")
    print(f"   Service: zkme-token")
    print(f"   Keywords: {keywords}")
    print(f"   Generated LogQL: {query}")
    
    # Demo 3: Mock query execution
    print("\n3. Mock Query Execution:")
    mock_result = {
        'status': 'success',
        'data': {
            'resultType': 'streams',
            'result': [
                {
                    'stream': {'namespace': 'zkme-prod', 'app': 'zkme-token'},
                    'values': [
                        ['1640995200000000000', 'ERROR: Database connection failed'],
                        ['1640995260000000000', 'WARNING: High memory usage detected'],
                        ['1640995320000000000', 'ERROR: API request timeout']
                    ]
                }
            ]
        }
    }
    
    from datetime import datetime
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)
    
    formatted = service._format_query_result(mock_result, 'prod', keywords, start_time, end_time)
    print("   Mock query result:")
    print("   " + "\n   ".join(formatted.split('\n')[:10]))  # Show first 10 lines
    print("   ...")


async def demo_mcp_tools():
    """Demonstrate MCP tools"""
    print("\n=== MCP Tools Demo ===\n")
    
    # Create MCP server and register tools
    mcp = FastMCP('LogMCP Demo', 'Demo of LogMCP server capabilities')
    register_tools(mcp)
    
    # Show registered tools
    tools = await mcp.get_tools()
    print(f"Registered {len(tools)} MCP tools:")
    for tool_name in tools:
        print(f"  - {tool_name}")
    
    # Demo tool calls with mocked Loki service
    print("\n1. Keyword Query Tool (mocked):")
    with patch('logmcp.tools.loki_service') as mock_loki_service:
        mock_loki_service.query_keyword_logs.return_value = """
=== Loki Query Results ===
Environment: prod
Keywords: error
Time Range: 2023-12-01 00:00:00 - 2023-12-31 23:59:59
Result Type: streams
Total Streams: 1

--- Stream: {'namespace': 'zkme-prod', 'app': 'zkme-token'} ---
[2023-12-15 10:30:15] ERROR: Database connection timeout
[2023-12-15 10:31:22] ERROR: Failed to process payment request
[2023-12-15 10:32:45] ERROR: Authentication service unavailable

=== Summary ===
Total Log Entries: 3
        """.strip()
        
        print("   Simulating: loki_keyword_query(env='prod', keywords='error')")
        print("   Result preview:")
        result_lines = mock_loki_service.query_keyword_logs.return_value.split('\n')
        for line in result_lines[:8]:
            print(f"     {line}")
        print("     ...")
    
    print("\n2. Range Query Tool (mocked):")
    with patch('logmcp.tools.loki_service') as mock_loki_service:
        mock_loki_service.query_range_logs_by_dates.return_value = """
=== Loki Query Results ===
Environment: test
Keywords: warning, timeout
Time Range: 2023-12-01 00:00:00 - 2023-12-02 23:59:59
Result Type: streams
Total Streams: 1

--- Stream: {'namespace': 'zkme-test', 'app': 'zkme-token'} ---
[2023-12-01 14:20:10] WARNING: Request processing slow
[2023-12-01 15:45:33] TIMEOUT: External API call exceeded limit

=== Summary ===
Total Log Entries: 2
        """.strip()
        
        print("   Simulating: loki_range_query(env='test', start_date='20231201', end_date='20231202', keywords='warning,timeout')")
        print("   Result preview:")
        result_lines = mock_loki_service.query_range_logs_by_dates.return_value.split('\n')
        for line in result_lines[:8]:
            print(f"     {line}")
        print("     ...")


def demo_configuration():
    """Demonstrate configuration management"""
    print("\n=== Configuration Demo ===\n")
    
    from logmcp.config import config
    
    print("Current configuration:")
    print(f"  Loki Gateway URL: {config.get('loki_gateway_url')}")
    print(f"  Loki Timeout: {config.get('loki_timeout')} seconds")
    print(f"  Default Limit: {config.get('loki_default_limit')} entries")
    print(f"  MCP Server Name: {config.get('mcp_server_name')}")
    
    print("\nEnvironment namespace mapping:")
    for env in ['test', 'dev', 'prod']:
        namespace = config.get_env_namespace(env)
        print(f"  {env} -> {namespace}")


def demo_usage_instructions():
    """Show usage instructions"""
    print("\n=== Usage Instructions ===\n")
    
    print("1. Start the MCP server:")
    print("   uv run python main.py")
    print()
    print("2. The server uses stdio transport and provides these tools:")
    print("   - loki_keyword_query: Query logs with keywords (last 30 days)")
    print("   - loki_range_query: Query logs with keywords in date range")
    print()
    print("3. Environment variables for configuration:")
    print("   LOKI_GATEWAY_URL=http://your-loki:80")
    print("   LOKI_TIMEOUT=30")
    print("   LOKI_DEFAULT_LIMIT=1000")
    print("   DEFAULT_SERVICE=your-service-name")
    print()
    print("4. Example MCP tool calls:")
    print("   loki_keyword_query(env='prod', keywords='error,exception')")
    print("   loki_range_query(env='test', start_date='20231201', end_date='20231202', keywords='warning')")


async def main():
    """Main demo function"""
    print("🚀 LogMCP Server Demo\n")
    print("This demo shows the capabilities of the LogMCP server,")
    print("a Model Context Protocol server for Loki log querying.\n")
    
    # Demo 1: Loki service
    demo_loki_service()
    
    # Demo 2: MCP tools
    await demo_mcp_tools()
    
    # Demo 3: Configuration
    demo_configuration()
    
    # Demo 4: Usage instructions
    demo_usage_instructions()
    
    print("\n✅ Demo completed!")
    print("\nThe LogMCP server is ready for use with MCP-compatible clients.")


if __name__ == "__main__":
    asyncio.run(main())
