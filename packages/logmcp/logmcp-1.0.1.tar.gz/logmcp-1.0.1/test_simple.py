#!/usr/bin/env python3
"""
Simple test script for LogMCP server (ASCII-only)
"""

import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastmcp import FastMCP
from logmcp.tools import register_tools
from logmcp.server import LogMCPServer
from logmcp.services.loki_service import LokiService


async def test_all():
    """Run all tests"""
    print("=== LogMCP Server Tests ===\n")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Tools registration
    total_tests += 1
    print("Test 1: MCP tools registration...")
    try:
        mcp = FastMCP('test', 'test')
        register_tools(mcp)
        tools = await mcp.get_tools()
        
        if len(tools) == 2 and 'loki_keyword_query' in tools and 'loki_range_query' in tools:
            print("  [PASS] Tools registered successfully")
            tests_passed += 1
        else:
            print(f"  [FAIL] Expected 2 tools, got {len(tools)}")
    except Exception as e:
        print(f"  [FAIL] Tools registration failed: {e}")
    
    # Test 2: Server creation
    total_tests += 1
    print("\nTest 2: Server creation...")
    try:
        server = LogMCPServer()
        mcp = server.create_server()
        
        if mcp is not None:
            print("  [PASS] Server created successfully")
            tests_passed += 1
        else:
            print("  [FAIL] Server creation returned None")
    except Exception as e:
        print(f"  [FAIL] Server creation failed: {e}")
    
    # Test 3: Loki service functionality
    total_tests += 1
    print("\nTest 3: Loki service functionality...")
    try:
        service = LokiService()
        
        # Test keyword parsing
        keywords = service._parse_keywords_input("error, warning")
        if keywords == ["error", "warning"]:
            print("  [PASS] Keyword parsing works")
        else:
            print(f"  [FAIL] Keyword parsing failed: {keywords}")
            raise Exception("Keyword parsing failed")
        
        # Test query building
        query = service._build_loki_query("test-ns", "test-service", ["error"])
        expected = '{namespace="test-ns", app="test-service"}|~ "(?i)error"'
        if query == expected:
            print("  [PASS] Query building works")
        else:
            print(f"  [FAIL] Query building failed: {query}")
            raise Exception("Query building failed")
        
        tests_passed += 1
    except Exception as e:
        print(f"  [FAIL] Loki service test failed: {e}")
    
    # Test 4: Configuration
    total_tests += 1
    print("\nTest 4: Configuration...")
    try:
        from logmcp.config import config
        
        loki_url = config.get('loki_gateway_url')
        if loki_url:
            print(f"  [PASS] Configuration loaded: {loki_url}")
            tests_passed += 1
        else:
            print("  [FAIL] Configuration not loaded")
    except Exception as e:
        print(f"  [FAIL] Configuration test failed: {e}")
    
    # Summary
    print(f"\n=== Test Results ===")
    print(f"Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n[SUCCESS] All tests passed!")
        print("\nThe LogMCP server is ready for use.")
        print("To start the server: uv run python main.py")
        return 0
    else:
        print(f"\n[ERROR] {total_tests - tests_passed} tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_all())
    sys.exit(exit_code)
