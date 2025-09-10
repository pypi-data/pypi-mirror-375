#!/usr/bin/env python3
"""
Test server initialization without actually starting stdio transport
"""

import asyncio
import sys
import os
from unittest.mock import patch, AsyncMock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logmcp.server import LogMCPServer


async def test_server_initialization():
    """Test server initialization process"""
    print("Testing server initialization...")
    
    server = LogMCPServer()
    
    # Test 1: Server creation
    try:
        mcp = server.create_server()
        assert mcp is not None, "MCP server should be created"
        print("✓ MCP server created successfully")
    except Exception as e:
        print(f"✗ MCP server creation failed: {e}")
        return False
    
    # Test 2: Service initialization (mocked)
    try:
        with patch('logmcp.server.loki_service') as mock_loki_service:
            mock_loki_service.initialize.return_value = None
            
            await server._initialize_services()
            print("✓ Services initialized successfully")
            mock_loki_service.initialize.assert_called_once()
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        return False
    
    # Test 3: Server start preparation (without actual stdio)
    try:
        with patch.object(server, '_initialize_services') as mock_init:
            with patch.object(server, 'create_server') as mock_create:
                mock_mcp = AsyncMock()
                mock_init.return_value = None
                mock_create.return_value = mock_mcp
                
                # This would normally start stdio transport, but we mock it
                with patch.object(mock_mcp, 'run_async') as mock_run:
                    mock_run.return_value = None
                    
                    await server.start_async()
                    print("✓ Server start process completed")
                    
                    # Verify the correct transport was specified
                    mock_run.assert_called_once_with(transport="stdio")
    except Exception as e:
        print(f"✗ Server start process failed: {e}")
        return False
    
    return True


async def test_main_entry_point():
    """Test the main entry point"""
    print("\nTesting main entry point...")
    
    try:
        # Mock the server start to avoid blocking
        with patch.object(LogMCPServer, 'start') as mock_start:
            mock_start.return_value = None
            
            from logmcp.server import main
            main()
            
            print("✓ Main entry point works")
            mock_start.assert_called_once()
            return True
    except Exception as e:
        print(f"✗ Main entry point failed: {e}")
        return False


async def main():
    """Main test function"""
    print("=== LogMCP Server Initialization Tests ===\n")
    
    try:
        # Test 1: Server initialization
        init_ok = await test_server_initialization()
        
        # Test 2: Main entry point
        main_ok = await test_main_entry_point()
        
        # Summary
        print(f"\n=== Test Results ===")
        print(f"Server initialization: {'✓ PASS' if init_ok else '✗ FAIL'}")
        print(f"Main entry point: {'✓ PASS' if main_ok else '✗ FAIL'}")
        
        if init_ok and main_ok:
            print("\n🎉 All server initialization tests passed!")
            print("\n📝 The server is ready to run with: uv run python main.py")
            print("   It will use stdio transport for MCP communication.")
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
