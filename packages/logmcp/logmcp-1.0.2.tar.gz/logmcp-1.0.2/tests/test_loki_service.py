"""
Tests for Loki service
"""

import pytest
import requests
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logmcp.services.loki_service import LokiService


class TestLokiService:
    """Test cases for LokiService"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service = LokiService()
    
    def test_initialization(self):
        """Test service initialization"""
        assert not self.service.is_initialized

        with patch('logmcp.services.loki_service.config') as mock_config:
            mock_config.get_loki_gateway_url.return_value = 'http://test-loki:80'
            mock_config.get.side_effect = lambda key, default=None: {
                'loki_timeout': 30,
                'loki_default_limit': 1000
            }.get(key, default)

            self.service.initialize()

            assert self.service.is_initialized
            assert self.service.gateway_url == 'http://test-loki:80'
            assert self.service.timeout == 30
            assert self.service.default_limit == 1000
    
    def test_parse_keywords_input_string(self):
        """Test parsing keywords from string"""
        # Single keyword
        result = self.service._parse_keywords_input("error")
        assert result == ["error"]
        
        # Multiple keywords
        result = self.service._parse_keywords_input("error, warning, debug")
        assert result == ["error", "warning", "debug"]
        
        # Keywords with extra spaces
        result = self.service._parse_keywords_input("  error  ,  warning  ")
        assert result == ["error", "warning"]
    
    def test_parse_keywords_input_list(self):
        """Test parsing keywords from list"""
        result = self.service._parse_keywords_input(["error", "warning"])
        assert result == ["error", "warning"]
        
        # List with mixed types
        result = self.service._parse_keywords_input(["error", 123, "warning"])
        assert result == ["error", "123", "warning"]
    
    def test_parse_keywords_input_empty(self):
        """Test parsing empty keywords"""
        assert self.service._parse_keywords_input("") == []
        assert self.service._parse_keywords_input([]) == []
        assert self.service._parse_keywords_input("  ,  ,  ") == []
    
    def test_build_loki_query(self):
        """Test building Loki LogQL query"""
        # Single keyword
        query = self.service._build_loki_query("test-ns", "test-service", ["error"])
        expected = '{namespace="test-ns", service_name="test-service"}|~ "(?i)error"'
        assert query == expected

        # Multiple keywords
        query = self.service._build_loki_query("test-ns", "test-service", ["error", "warning"])
        expected = '{namespace="test-ns", service_name="test-service"}|~ "(?i)error"|~ "(?i)warning"'
        assert query == expected
        
        # No keywords
        query = self.service._build_loki_query("test-ns", "test-service", [])
        expected = '{namespace="test-ns", service_name="test-service"}'
        assert query == expected

    def test_build_loki_query_with_special_chars(self):
        """Test building query with special characters in keywords"""
        query = self.service._build_loki_query("test-ns", "test-service", ['error "test"'])
        expected = '{namespace="test-ns", service_name="test-service"}|~ "(?i)error \\"test\\""'
        assert query == expected
    
    @patch('requests.get')
    def test_execute_loki_query_success(self, mock_get):
        """Test successful Loki query execution"""
        # Setup mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'status': 'success',
            'data': {
                'resultType': 'streams',
                'result': []
            }
        }
        mock_get.return_value = mock_response
        
        # Initialize service
        self.service.gateway_url = 'http://test-loki:80'
        self.service.timeout = 30
        self.service.is_initialized = True
        
        # Execute query
        params = {'query': 'test', 'start': '2023-01-01T00:00:00Z', 'end': '2023-01-02T00:00:00Z'}
        result = self.service._execute_loki_query(params)
        
        # Verify result
        assert result['status'] == 'success'
        mock_get.assert_called_once_with(
            'http://test-loki:80/loki/api/v1/query_range',
            params=params,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
    
    @patch('requests.get')
    def test_execute_loki_query_http_error(self, mock_get):
        """Test Loki query with HTTP error"""
        # Setup mock to raise HTTP error
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")
        
        # Initialize service
        self.service.gateway_url = 'http://test-loki:80'
        self.service.is_initialized = True
        
        # Execute query
        params = {'query': 'test'}
        result = self.service._execute_loki_query(params)
        
        # Verify error handling
        assert result['status'] == 'error'
        assert 'HTTP request failed' in result['error']
    
    def test_format_query_result_no_results(self):
        """Test formatting query result with no results"""
        result_data = {
            'status': 'success',
            'data': {
                'resultType': 'streams',
                'result': []
            }
        }
        
        start_time = datetime(2023, 1, 1)
        end_time = datetime(2023, 1, 2)
        keywords = ['error']
        
        formatted = self.service._format_query_result(result_data, 'test', keywords, start_time, end_time)
        
        assert 'No logs found' in formatted
        assert 'error' in formatted
        assert 'test' in formatted
    
    def test_format_query_result_with_results(self):
        """Test formatting query result with results"""
        result_data = {
            'status': 'success',
            'data': {
                'resultType': 'streams',
                'result': [
                    {
                        'stream': {'namespace': 'test', 'app': 'service'},
                        'values': [
                            ['1640995200000000000', 'Error message 1'],
                            ['1640995260000000000', 'Error message 2']
                        ]
                    }
                ]
            }
        }
        
        start_time = datetime(2023, 1, 1)
        end_time = datetime(2023, 1, 2)
        keywords = ['error']
        
        formatted = self.service._format_query_result(result_data, 'test', keywords, start_time, end_time)
        
        assert '=== Loki Query Results ===' in formatted
        assert 'Environment: test' in formatted
        assert 'Keywords: error' in formatted
        assert 'Total Log Entries: 2' in formatted
        assert 'Error message 1' in formatted
        assert 'Error message 2' in formatted
    
    def test_format_query_result_error_status(self):
        """Test formatting query result with error status"""
        result_data = {
            'status': 'error',
            'error': 'Query syntax error'
        }
        
        start_time = datetime(2023, 1, 1)
        end_time = datetime(2023, 1, 2)
        keywords = ['error']
        
        formatted = self.service._format_query_result(result_data, 'test', keywords, start_time, end_time)
        
        assert 'Query failed: Query syntax error' in formatted
    
    @patch.object(LokiService, 'query_range_logs')
    def test_query_keyword_logs(self, mock_query_range):
        """Test keyword logs query (30 days)"""
        mock_query_range.return_value = "Test result"
        
        result = self.service.query_keyword_logs('test', 'error')
        
        assert result == "Test result"
        mock_query_range.assert_called_once()
        
        # Check that the time range is approximately 30 days
        call_args = mock_query_range.call_args
        start_time = call_args[1]['start_time']
        end_time = call_args[1]['end_time']
        time_diff = end_time - start_time
        
        # Should be close to 30 days (allowing some tolerance for test execution time)
        assert 29 <= time_diff.days <= 31
    
    def test_query_range_logs_by_dates_valid_format(self):
        """Test query by date strings with valid format"""
        with patch.object(self.service, 'query_range_logs') as mock_query:
            mock_query.return_value = "Test result"
            
            result = self.service.query_range_logs_by_dates(
                'test', '20230101', '20230102', 'error'
            )
            
            assert result == "Test result"
            mock_query.assert_called_once()
            
            # Check parsed dates
            call_args = mock_query.call_args
            start_time = call_args[1]['start_time']
            end_time = call_args[1]['end_time']
            
            assert start_time == datetime(2023, 1, 1)
            assert end_time == datetime(2023, 1, 2, 23, 59, 59)
    
    def test_query_range_logs_by_dates_invalid_format(self):
        """Test query by date strings with invalid format"""
        result = self.service.query_range_logs_by_dates(
            'test', 'invalid-date', '20230102', 'error'
        )
        
        assert 'Date format error' in result
        assert 'YYYYMMDD format' in result
