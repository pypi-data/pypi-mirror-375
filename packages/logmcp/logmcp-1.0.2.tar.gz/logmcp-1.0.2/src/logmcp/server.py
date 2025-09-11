"""
LogMCP Server - MCP server implementation using stdio transport
"""

import asyncio
import sys
from typing import Optional

from fastmcp import FastMCP

from .config import config
from .logger import logger
from .tools import register_tools
from .services import loki_service


class LogMCPServer:
    """LogMCP server implementation using stdio transport"""
    
    def __init__(self):
        self.mcp: Optional[FastMCP] = None
        self.is_running = False
        
    def create_server(self) -> FastMCP:
        """Create and configure the FastMCP server"""
        try:
            # Validate configuration
            config.validate()
            
            # Create FastMCP instance
            server_name = config.get('mcp_server_name', 'LogMCP Server')
            server_version = config.get('mcp_server_version', '1.0.0')
            
            mcp = FastMCP(
                name=server_name,
                instructions=f"MCP server for log querying and system monitoring via Loki (v{server_version})"
            )
            
            # Register tools
            register_tools(mcp)
            
            logger.info(f"FastMCP server created: {server_name} v{server_version}")
            return mcp
            
        except Exception as e:
            logger.error_with_traceback("Failed to create FastMCP server", e)
            raise
    
    async def start_async(self) -> None:
        """Start the FastMCP server asynchronously with stdio transport"""
        try:
            # Initialize services
            await self._initialize_services()
            
            # Create server
            self.mcp = self.create_server()
            
            logger.info("Starting LogMCP server with stdio transport")
            
            # Run with stdio transport
            await self.mcp.run_async(transport="stdio")
            
        except Exception as e:
            logger.error_with_traceback("Failed to start LogMCP server", e)
            raise
    
    async def _initialize_services(self) -> None:
        """Initialize all required services"""
        try:
            logger.info("Initializing services...")
            
            # Initialize Loki service
            loki_service.initialize()
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error_with_traceback("Service initialization failed", e)
            raise
    
    def start(self) -> None:
        """Start the server (synchronous wrapper)"""
        try:
            asyncio.run(self.start_async())
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error_with_traceback("Server startup failed", e)
            sys.exit(1)
    
    async def stop(self) -> None:
        """Stop the server gracefully"""
        try:
            if self.mcp and self.is_running:
                logger.info("Stopping LogMCP server...")
                # FastMCP doesn't have explicit stop method for stdio
                # The server will stop when the main coroutine completes
                self.is_running = False
                logger.info("LogMCP server stopped")
        except Exception as e:
            logger.error_with_traceback("Error stopping server", e)


def main() -> None:
    """Main entry point for the LogMCP server"""
    try:
        # Create and start server
        server = LogMCPServer()
        server.start()
        
    except Exception as e:
        logger.error_with_traceback("LogMCP server failed to start", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
