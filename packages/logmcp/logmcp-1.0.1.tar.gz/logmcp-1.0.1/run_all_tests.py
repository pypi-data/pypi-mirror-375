#!/usr/bin/env python3
"""
Run all tests for LogMCP server
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 LogMCP Server - Complete Test Suite")
    print("=" * 60)
    
    tests = [
        ("uv run python test_basic.py", "Basic Functionality Tests"),
        ("uv run python test_integration.py", "Integration Tests"),
        ("uv run python test_server_init.py", "Server Initialization Tests"),
        ("uv run python demo.py", "Demo and Capabilities Test"),
        ("uv run pytest tests/test_loki_service.py::TestLokiService::test_parse_keywords_input_string -v", "Unit Test - Keyword Parsing"),
        ("uv run pytest tests/test_loki_service.py::TestLokiService::test_build_loki_query -v", "Unit Test - Query Building"),
        ("uv run pytest tests/test_loki_service.py::TestLokiService::test_format_query_result_no_results -v", "Unit Test - Result Formatting"),
    ]
    
    results = []
    
    for cmd, description in tests:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = 0
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {description}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📋 Summary:")
        print("  ✅ Basic functionality works")
        print("  ✅ Integration tests pass")
        print("  ✅ Server initialization works")
        print("  ✅ Demo runs successfully")
        print("  ✅ Unit tests pass")
        print("\n🚀 The LogMCP server is ready for production use!")
        print("\n📝 To start the server:")
        print("   uv run python main.py")
        print("\n📖 For more information, see README.md")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed!")
        print("\n🔧 Please review the failed tests and fix any issues.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
