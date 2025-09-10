#!/usr/bin/env python3
"""
Basic test script to verify LogMCP functionality
"""

import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastmcp import FastMCP
from logmcp.tools import register_tools
from logmcp.server import LogMCPServer


async def test_tools():
    """Test MCP tools registration"""
    print("Testing MCP tools registration...")
    
    mcp = FastMCP('test', 'test')
    register_tools(mcp)
    
    tools = await mcp.get_tools()
    print(f"Registered {len(tools)} tools:")
    for tool in tools:
        if hasattr(tool, 'name'):
            print(f"  - {tool.name}: {tool.description}")
        else:
            print(f"  - {tool}")

    return len(tools) == 3


def test_server_creation():
    """Test server creation"""
    print("\nTesting server creation...")
    
    try:
        server = LogMCPServer()
        print("[OK] Server instance created successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Server creation failed: {e}")
        return False


async def main():
    """Main test function"""
    print("=== LogMCP Basic Tests ===\n")
    
    # Test 1: Tools registration
    tools_ok = await test_tools()
    
    # Test 2: Server creation
    server_ok = test_server_creation()
    
    # Summary
    print(f"\n=== Test Results ===")
    print(f"Tools registration: {'[PASS]' if tools_ok else '[FAIL]'}")
    print(f"Server creation: {'[PASS]' if server_ok else '[FAIL]'}")

    if tools_ok and server_ok:
        print("\n[SUCCESS] All basic tests passed!")
        return 0
    else:
        print("\n[ERROR] Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
