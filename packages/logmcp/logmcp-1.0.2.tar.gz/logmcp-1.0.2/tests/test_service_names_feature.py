#!/usr/bin/env python3
"""
Test cases for the new loki_service_names feature
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logmcp.services.loki_service import LokiService
from logmcp.tools import register_tools
from fastmcp import FastMCP


class TestServiceNamesFeature:
    """Test cases for service names functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = LokiService()
        self.service.gateway_url = "https://test-loki.example.com"
        self.service.timeout = 30
        self.service.is_initialized = True
    
    def test_get_service_names_method_exists(self):
        """Test that get_service_names method exists"""
        assert hasattr(self.service, 'get_service_names')
        assert callable(getattr(self.service, 'get_service_names'))
    
    def test_execute_loki_labels_query_method_exists(self):
        """Test that _execute_loki_labels_query method exists"""
        assert hasattr(self.service, '_execute_loki_labels_query')
        assert callable(getattr(self.service, '_execute_loki_labels_query'))
    
    def test_format_service_names_result_method_exists(self):
        """Test that _format_service_names_result method exists"""
        assert hasattr(self.service, '_format_service_names_result')
        assert callable(getattr(self.service, '_format_service_names_result'))
    
    @patch('requests.get')
    def test_execute_loki_labels_query_success(self, mock_get):
        """Test successful Loki labels query execution"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'data': ['service1', 'service2', 'service3']
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the method
        params = {'start': '2025-01-01T00:00:00Z', 'end': '2025-01-02T00:00:00Z'}
        result = self.service._execute_loki_labels_query('service_name', params)
        
        # Verify the result
        assert result['status'] == 'success'
        assert result['data'] == ['service1', 'service2', 'service3']
        
        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'service_name' in call_args[0][0]  # URL contains service_name
        assert call_args[1]['params'] == params
    
    def test_format_service_names_result_success(self):
        """Test formatting of successful service names result"""
        # Mock successful result
        result = {
            'status': 'success',
            'data': ['zkme-token', 'zkme-gateway', 'zkme-api']
        }
        
        start_time = datetime(2025, 1, 1, 0, 0, 0)
        end_time = datetime(2025, 1, 2, 0, 0, 0)
        
        formatted = self.service._format_service_names_result(
            result, 'dev', 'zkme-dev', start_time, end_time
        )
        
        # Verify the formatted output
        assert '=== DEV 环境中的 Service Names ===' in formatted
        assert '命名空间: zkme-dev' in formatted
        # Services are sorted alphabetically
        assert '1. zkme-api' in formatted
        assert '2. zkme-gateway' in formatted
        assert '3. zkme-token' in formatted
        assert '服务总数: 3' in formatted
        assert '💡 提示' in formatted
    
    def test_format_service_names_result_no_data(self):
        """Test formatting when no service names found"""
        # Mock empty result
        result = {
            'status': 'success',
            'data': []
        }
        
        start_time = datetime(2025, 1, 1, 0, 0, 0)
        end_time = datetime(2025, 1, 2, 0, 0, 0)
        
        formatted = self.service._format_service_names_result(
            result, 'dev', 'zkme-dev', start_time, end_time
        )
        
        # Verify the formatted output
        assert '在 dev 环境中未找到任何service_name' in formatted
        assert '命名空间: zkme-dev' in formatted
    
    def test_format_service_names_result_error(self):
        """Test formatting when query fails"""
        # Mock error result
        result = {
            'status': 'error',
            'error': 'Connection failed'
        }
        
        start_time = datetime(2025, 1, 1, 0, 0, 0)
        end_time = datetime(2025, 1, 2, 0, 0, 0)
        
        formatted = self.service._format_service_names_result(
            result, 'dev', 'zkme-dev', start_time, end_time
        )
        
        # Verify the error message
        assert 'Loki标签查询失败' in formatted
        assert 'Connection failed' in formatted
    
    @patch.object(LokiService, '_execute_loki_labels_query')
    @patch.object(LokiService, '_format_service_names_result')
    def test_get_service_names_integration(self, mock_format, mock_execute):
        """Test get_service_names method integration"""
        # Mock the dependencies
        mock_execute.return_value = {'status': 'success', 'data': ['service1']}
        mock_format.return_value = 'Formatted result'
        
        # Test the method
        result = self.service.get_service_names('dev', 'zkme-dev', 30)
        
        # Verify the result
        assert result == 'Formatted result'
        
        # Verify the methods were called
        mock_execute.assert_called_once()
        mock_format.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mcp_tool_registration(self):
        """Test that loki_service_names tool is properly registered"""
        mcp = FastMCP('test', 'test')
        register_tools(mcp)

        tools = await mcp.get_tools()
        tool_names = [tool.name for tool in tools]

        # Verify the new tool is registered
        assert 'loki_service_names' in tool_names
        assert 'loki_keyword_query' in tool_names
        assert 'loki_range_query' in tool_names
        assert len(tools) == 3

    @pytest.mark.asyncio
    async def test_mcp_tool_has_correct_parameters(self):
        """Test that loki_service_names tool has correct parameters"""
        mcp = FastMCP('test', 'test')
        register_tools(mcp)

        tools = await mcp.get_tools()
        service_names_tool = None

        for tool in tools:
            if tool.name == 'loki_service_names':
                service_names_tool = tool
                break

        assert service_names_tool is not None

        # Check parameters
        params = service_names_tool.inputSchema.get('properties', {})
        assert 'env' in params
        assert 'namespace' in params
        assert 'days_back' in params

        # Check required parameters
        required = service_names_tool.inputSchema.get('required', [])
        assert 'env' in required


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
