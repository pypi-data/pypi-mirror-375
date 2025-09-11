#!/usr/bin/env python3
"""
Integration test for LogMCP server
"""

import asyncio
import sys
import os
from unittest.mock import patch, Mock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logmcp.services.loki_service import LokiService
from logmcp.config import config


async def test_loki_service():
    """Test Loki service functionality"""
    print("Testing Loki service...")
    
    service = LokiService()
    
    # Test keyword parsing
    keywords = service._parse_keywords_input("error, warning, debug")
    assert keywords == ["error", "warning", "debug"], f"Expected ['error', 'warning', 'debug'], got {keywords}"
    print("✓ Keyword parsing works")
    
    # Test query building
    query = service._build_loki_query("test-ns", "test-service", ["error"])
    expected = '{namespace="test-ns", app="test-service"}|~ "(?i)error"'
    assert query == expected, f"Expected {expected}, got {query}"
    print("✓ Query building works")
    
    # Test configuration
    try:
        config.validate()
        print("✓ Configuration validation works")
    except Exception as e:
        print(f"⚠ Configuration validation failed (expected in test): {e}")
    
    return True


def test_config():
    """Test configuration management"""
    print("\nTesting configuration...")
    
    # Test default values
    loki_url = config.get('loki_gateway_url')
    assert loki_url is not None, "Loki gateway URL should have a default value"
    print(f"✓ Loki gateway URL: {loki_url}")
    
    # Test environment namespace mapping
    test_ns = config.get_env_namespace('test')
    assert test_ns is not None, "Test namespace should be available"
    print(f"✓ Test namespace: {test_ns}")
    
    return True


async def test_tool_functions():
    """Test MCP tool functions with mocked Loki service"""
    print("\nTesting MCP tool functions...")
    
    # Mock the Loki service
    with patch('logmcp.tools.loki_service') as mock_loki_service:
        mock_loki_service.query_keyword_logs.return_value = "Mock log results"
        mock_loki_service.query_range_logs_by_dates.return_value = "Mock range results"
        
        # Import tools after patching
        from fastmcp import FastMCP
        from logmcp.tools import register_tools
        
        mcp = FastMCP('test', 'test')
        register_tools(mcp)
        
        # Test that tools are registered
        tools = await mcp.get_tools()
        assert len(tools) == 2, f"Expected 2 tools, got {len(tools)}"
        assert 'loki_keyword_query' in tools, "loki_keyword_query should be registered"
        assert 'loki_range_query' in tools, "loki_range_query should be registered"
        print("✓ Tools registered successfully")
        
        return True


async def main():
    """Main test function"""
    print("=== LogMCP Integration Tests ===\n")
    
    try:
        # Test 1: Loki service
        loki_ok = await test_loki_service()
        
        # Test 2: Configuration
        config_ok = test_config()
        
        # Test 3: Tool functions
        tools_ok = await test_tool_functions()
        
        # Summary
        print(f"\n=== Test Results ===")
        print(f"Loki service: {'✓ PASS' if loki_ok else '✗ FAIL'}")
        print(f"Configuration: {'✓ PASS' if config_ok else '✗ FAIL'}")
        print(f"Tool functions: {'✓ PASS' if tools_ok else '✗ FAIL'}")
        
        if loki_ok and config_ok and tools_ok:
            print("\n🎉 All integration tests passed!")
            print("\n📝 Note: These tests use mocked external dependencies.")
            print("   For full testing, configure a real Loki instance.")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
