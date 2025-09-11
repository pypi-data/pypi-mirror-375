"""
Tests for MCP tools
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastmcp import FastMCP
from logmcp.tools import register_tools


class TestMCPTools:
    """Test cases for MCP tools"""

    def setup_method(self):
        """Setup test environment"""
        self.mcp = FastMCP(name="Test MCP", instructions="Test server")
        register_tools(self.mcp)

        # Get tool functions for direct testing
        tools = self.mcp.get_tools()
        self.keyword_tool = next(tool for tool in tools if tool.name == 'loki_keyword_query')
        self.range_tool = next(tool for tool in tools if tool.name == 'loki_range_query')
    
    @pytest.mark.asyncio
    async def test_loki_keyword_query_success(self):
        """Test successful loki_keyword_query execution"""
        with patch('logmcp.tools.loki_service') as mock_loki_service:
            mock_loki_service.query_keyword_logs.return_value = "Test log results"

            # Create mock context
            mock_ctx = AsyncMock()

            # Import the tool function directly
            from logmcp.tools import register_tools

            # Create a temporary MCP instance to get the tool function
            temp_mcp = FastMCP(name="temp", instructions="temp")
            register_tools(temp_mcp)

            # Get the tool function
            tools = temp_mcp.get_tools()
            keyword_tool = next(tool for tool in tools if tool.name == 'loki_keyword_query')

            # Call the tool function directly
            result = await keyword_tool.func(
                env="test",
                keywords="error",
                service_name="test-service",
                namespace="test-ns",
                limit=100,
                ctx=mock_ctx
            )

            assert result == "Test log results"
            mock_loki_service.query_keyword_logs.assert_called_once_with(
                env="test",
                keywords="error",
                service_name="test-service",
                namespace="test-ns",
                limit=100
            )
            mock_ctx.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_loki_keyword_query_missing_env(self):
        """Test loki_keyword_query with missing environment"""
        tools = self.mcp._tools
        tool_func = tools['loki_keyword_query'].func
        
        mock_ctx = AsyncMock()
        
        result = await tool_func(
            env="",
            keywords="error",
            ctx=mock_ctx
        )
        
        assert "Environment parameter is required" in result
        mock_ctx.error.assert_called_with("Environment parameter is required")
    
    @pytest.mark.asyncio
    async def test_loki_keyword_query_missing_keywords(self):
        """Test loki_keyword_query with missing keywords"""
        tools = self.mcp._tools
        tool_func = tools['loki_keyword_query'].func
        
        mock_ctx = AsyncMock()
        
        result = await tool_func(
            env="test",
            keywords="",
            ctx=mock_ctx
        )
        
        assert "Keywords parameter is required" in result
        mock_ctx.error.assert_called_with("Keywords parameter is required")
    
    @pytest.mark.asyncio
    async def test_loki_keyword_query_exception(self):
        """Test loki_keyword_query with exception"""
        with patch('logmcp.tools.loki_service') as mock_loki_service:
            mock_loki_service.query_keyword_logs.side_effect = Exception("Service error")
            
            tools = self.mcp._tools
            tool_func = tools['loki_keyword_query'].func
            
            mock_ctx = AsyncMock()
            
            result = await tool_func(
                env="test",
                keywords="error",
                ctx=mock_ctx
            )
            
            assert "Loki keyword query failed: Service error" in result
            mock_ctx.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_loki_keyword_query_without_context(self):
        """Test loki_keyword_query without context"""
        with patch('logmcp.tools.loki_service') as mock_loki_service:
            mock_loki_service.query_keyword_logs.return_value = "Test results"
            
            tools = self.mcp._tools
            tool_func = tools['loki_keyword_query'].func
            
            # Call without context
            result = await tool_func(
                env="test",
                keywords="error"
            )
            
            assert result == "Test results"
    
    @pytest.mark.asyncio
    async def test_loki_range_query_success(self):
        """Test successful loki_range_query execution"""
        with patch('logmcp.tools.loki_service') as mock_loki_service:
            mock_loki_service.query_range_logs_by_dates.return_value = "Test range results"
            
            tools = self.mcp._tools
            assert 'loki_range_query' in tools
            
            tool_func = tools['loki_range_query'].func
            
            mock_ctx = AsyncMock()
            
            result = await tool_func(
                env="test",
                start_date="20230101",
                end_date="20230102",
                keywords="error",
                service_name="test-service",
                namespace="test-ns",
                limit=100,
                ctx=mock_ctx
            )
            
            assert result == "Test range results"
            mock_loki_service.query_range_logs_by_dates.assert_called_once_with(
                env="test",
                start_date="20230101",
                end_date="20230102",
                keywords="error",
                service_name="test-service",
                namespace="test-ns",
                limit=100
            )
            mock_ctx.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_loki_range_query_missing_env(self):
        """Test loki_range_query with missing environment"""
        tools = self.mcp._tools
        tool_func = tools['loki_range_query'].func
        
        mock_ctx = AsyncMock()
        
        result = await tool_func(
            env="",
            start_date="20230101",
            end_date="20230102",
            keywords="error",
            ctx=mock_ctx
        )
        
        assert "Environment parameter is required" in result
        mock_ctx.error.assert_called_with("Environment parameter is required")
    
    @pytest.mark.asyncio
    async def test_loki_range_query_missing_dates(self):
        """Test loki_range_query with missing dates"""
        tools = self.mcp._tools
        tool_func = tools['loki_range_query'].func
        
        mock_ctx = AsyncMock()
        
        # Missing start date
        result = await tool_func(
            env="test",
            start_date="",
            end_date="20230102",
            keywords="error",
            ctx=mock_ctx
        )
        
        assert "Start date and end date parameters are required" in result
        
        # Missing end date
        result = await tool_func(
            env="test",
            start_date="20230101",
            end_date="",
            keywords="error",
            ctx=mock_ctx
        )
        
        assert "Start date and end date parameters are required" in result
    
    @pytest.mark.asyncio
    async def test_loki_range_query_missing_keywords(self):
        """Test loki_range_query with missing keywords"""
        tools = self.mcp._tools
        tool_func = tools['loki_range_query'].func
        
        mock_ctx = AsyncMock()
        
        result = await tool_func(
            env="test",
            start_date="20230101",
            end_date="20230102",
            keywords="",
            ctx=mock_ctx
        )
        
        assert "Keywords parameter is required" in result
        mock_ctx.error.assert_called_with("Keywords parameter is required")
    
    @pytest.mark.asyncio
    async def test_loki_range_query_exception(self):
        """Test loki_range_query with exception"""
        with patch('logmcp.tools.loki_service') as mock_loki_service:
            mock_loki_service.query_range_logs_by_dates.side_effect = Exception("Service error")
            
            tools = self.mcp._tools
            tool_func = tools['loki_range_query'].func
            
            mock_ctx = AsyncMock()
            
            result = await tool_func(
                env="test",
                start_date="20230101",
                end_date="20230102",
                keywords="error",
                ctx=mock_ctx
            )
            
            assert "Loki range query failed: Service error" in result
            mock_ctx.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_loki_range_query_without_context(self):
        """Test loki_range_query without context"""
        with patch('logmcp.tools.loki_service') as mock_loki_service:
            mock_loki_service.query_range_logs_by_dates.return_value = "Test results"
            
            tools = self.mcp._tools
            tool_func = tools['loki_range_query'].func
            
            # Call without context
            result = await tool_func(
                env="test",
                start_date="20230101",
                end_date="20230102",
                keywords="error"
            )
            
            assert result == "Test results"
    
    def test_tools_registration(self):
        """Test that tools are properly registered"""
        tools = self.mcp.get_tools()

        # Check that both tools are registered
        tool_names = [tool.name for tool in tools]
        assert 'loki_keyword_query' in tool_names
        assert 'loki_range_query' in tool_names

        # Find the tools
        keyword_tool = next(tool for tool in tools if tool.name == 'loki_keyword_query')
        range_tool = next(tool for tool in tools if tool.name == 'loki_range_query')

        assert keyword_tool.name == 'loki_keyword_query'
        assert range_tool.name == 'loki_range_query'

        # Check that tools have descriptions
        assert keyword_tool.description is not None
        assert range_tool.description is not None
        assert 'Loki' in keyword_tool.description
        assert 'Loki' in range_tool.description
