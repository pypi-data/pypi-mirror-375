"""
Logger utility for LogMCP server
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class Logger:
    """Logger utility class for LogMCP server"""

    def __init__(self, name: str = 'logmcp', level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid adding duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup log handlers"""
        # Console handler - use stderr to avoid interfering with stdio MCP transport
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)

    def log_request(self, method: str, path: str, remote_addr: str, user_agent: Optional[str] = None):
        """Log request"""
        self.info(f"Request: {method} {path} from {remote_addr} - {user_agent}")

    def log_response(self, status_code: int, response_time: float):
        """Log response"""
        self.info(f"Response: {status_code} - {response_time:.3f}s")

    def log_error_with_traceback(self, message: str, exception: Exception):
        """Log error with traceback information"""
        self.logger.exception(f"{message}: {str(exception)}")

    def error_with_traceback(self, message: str, exception: Exception):
        """Log error with traceback information (alias method)"""
        self.log_error_with_traceback(message, exception)


# Global logger instance
logger = Logger()
