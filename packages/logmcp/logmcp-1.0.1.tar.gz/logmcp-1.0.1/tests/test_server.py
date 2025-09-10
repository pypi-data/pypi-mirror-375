"""
Tests for LogMCP server
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logmcp.server import LogMCPServer


class TestLogMCPServer:
    """Test cases for LogMCPServer"""
    
    def setup_method(self):
        """Setup test environment"""
        self.server = LogMCPServer()
    
    def test_server_initialization(self):
        """Test server initialization"""
        assert self.server.mcp is None
        assert not self.server.is_running
    
    @patch('logmcp.server.config')
    @patch('logmcp.server.register_tools')
    def test_create_server_success(self, mock_register_tools, mock_config):
        """Test successful server creation"""
        # Setup mock config
        mock_config.validate.return_value = True
        mock_config.get.side_effect = lambda key, default=None: {
            'mcp_server_name': 'Test LogMCP Server',
            'mcp_server_version': '1.0.0'
        }.get(key, default)
        
        # Create server
        mcp = self.server.create_server()
        
        # Verify
        assert mcp is not None
        assert mcp.name == 'Test LogMCP Server'
        mock_config.validate.assert_called_once()
        mock_register_tools.assert_called_once_with(mcp)
    
    @patch('logmcp.server.config')
    def test_create_server_config_validation_failure(self, mock_config):
        """Test server creation with config validation failure"""
        mock_config.validate.side_effect = ValueError("Missing required config")
        
        with pytest.raises(ValueError, match="Missing required config"):
            self.server.create_server()
    
    @patch('logmcp.server.config')
    @patch('logmcp.server.register_tools')
    def test_create_server_with_defaults(self, mock_register_tools, mock_config):
        """Test server creation with default values"""
        mock_config.validate.return_value = True
        mock_config.get.side_effect = lambda key, default=None: {
            'mcp_server_name': 'LogMCP Server',
            'mcp_server_version': '1.0.0'
        }.get(key, default)

        mcp = self.server.create_server()

        assert mcp is not None
        # Should use configured name
        assert 'LogMCP Server' in mcp.name
    
    @pytest.mark.asyncio
    @patch.object(LogMCPServer, '_initialize_services')
    @patch.object(LogMCPServer, 'create_server')
    async def test_start_async_success(self, mock_create_server, mock_init_services):
        """Test successful async server start"""
        # Setup mocks
        mock_mcp = AsyncMock()
        mock_create_server.return_value = mock_mcp
        mock_init_services.return_value = None
        
        # Start server
        await self.server.start_async()
        
        # Verify
        mock_init_services.assert_called_once()
        mock_create_server.assert_called_once()
        mock_mcp.run_async.assert_called_once_with(transport="stdio")
        assert self.server.mcp == mock_mcp
    
    @pytest.mark.asyncio
    @patch.object(LogMCPServer, '_initialize_services')
    async def test_start_async_initialization_failure(self, mock_init_services):
        """Test async server start with initialization failure"""
        mock_init_services.side_effect = Exception("Service init failed")
        
        with pytest.raises(Exception, match="Service init failed"):
            await self.server.start_async()
    
    @pytest.mark.asyncio
    @patch.object(LogMCPServer, '_initialize_services')
    @patch.object(LogMCPServer, 'create_server')
    async def test_start_async_server_creation_failure(self, mock_create_server, mock_init_services):
        """Test async server start with server creation failure"""
        mock_init_services.return_value = None
        mock_create_server.side_effect = Exception("Server creation failed")
        
        with pytest.raises(Exception, match="Server creation failed"):
            await self.server.start_async()
    
    @pytest.mark.asyncio
    @patch('logmcp.server.loki_service')
    async def test_initialize_services_success(self, mock_loki_service):
        """Test successful service initialization"""
        mock_loki_service.initialize.return_value = None
        
        await self.server._initialize_services()
        
        mock_loki_service.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('logmcp.server.loki_service')
    async def test_initialize_services_failure(self, mock_loki_service):
        """Test service initialization failure"""
        mock_loki_service.initialize.side_effect = Exception("Loki init failed")
        
        with pytest.raises(Exception, match="Loki init failed"):
            await self.server._initialize_services()
    
    @patch.object(LogMCPServer, 'start_async')
    def test_start_success(self, mock_start_async):
        """Test successful synchronous start"""
        mock_start_async.return_value = None
        
        # Mock asyncio.run to avoid actually running the event loop
        with patch('asyncio.run') as mock_run:
            self.server.start()
            mock_run.assert_called_once()
    
    @patch.object(LogMCPServer, 'start_async')
    def test_start_keyboard_interrupt(self, mock_start_async):
        """Test start with keyboard interrupt"""
        with patch('asyncio.run') as mock_run:
            mock_run.side_effect = KeyboardInterrupt()
            
            # Should not raise exception
            self.server.start()
    
    @patch.object(LogMCPServer, 'start_async')
    def test_start_exception(self, mock_start_async):
        """Test start with exception"""
        with patch('asyncio.run') as mock_run:
            mock_run.side_effect = Exception("Start failed")
            
            with pytest.raises(SystemExit):
                self.server.start()
    
    @pytest.mark.asyncio
    async def test_stop_success(self):
        """Test successful server stop"""
        # Setup server as running
        self.server.mcp = Mock()
        self.server.is_running = True
        
        await self.server.stop()
        
        assert not self.server.is_running
    
    @pytest.mark.asyncio
    async def test_stop_not_running(self):
        """Test stop when server is not running"""
        # Server not running
        self.server.mcp = None
        self.server.is_running = False
        
        # Should not raise exception
        await self.server.stop()
    
    @pytest.mark.asyncio
    async def test_stop_exception(self):
        """Test stop with exception"""
        self.server.mcp = Mock()
        self.server.is_running = True
        
        # Mock an exception during stop
        with patch('logmcp.server.logger') as mock_logger:
            # Force an exception by making is_running access fail
            with patch.object(self.server, 'is_running', side_effect=Exception("Stop error")):
                await self.server.stop()
                mock_logger.error_with_traceback.assert_called()


class TestServerMain:
    """Test cases for server main function"""
    
    @patch.object(LogMCPServer, 'start')
    def test_main_success(self, mock_start):
        """Test successful main function execution"""
        from logmcp.server import main
        
        mock_start.return_value = None
        
        main()
        
        mock_start.assert_called_once()
    
    @patch.object(LogMCPServer, 'start')
    def test_main_exception(self, mock_start):
        """Test main function with exception"""
        from logmcp.server import main
        
        mock_start.side_effect = Exception("Server failed")
        
        with pytest.raises(SystemExit):
            main()
    
    @patch.object(LogMCPServer, '__init__')
    def test_main_server_creation_failure(self, mock_init):
        """Test main function with server creation failure"""
        from logmcp.server import main
        
        mock_init.side_effect = Exception("Server creation failed")
        
        with pytest.raises(SystemExit):
            main()
