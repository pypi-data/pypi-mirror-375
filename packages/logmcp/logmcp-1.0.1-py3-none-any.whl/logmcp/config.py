"""
Configuration management for LogMCP server
"""

import os
from typing import Dict, Any, Optional


class Config:
    """Configuration management class for LogMCP server"""
    
    def __init__(self):
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            # Loki configuration
            'loki_gateway_url': os.getenv('LOKI_GATEWAY_URL', 'https://dev-hk-loki.bitkinetic.com'),
            'loki_timeout': int(os.getenv('LOKI_TIMEOUT', '30')),
            'loki_default_limit': int(os.getenv('LOKI_DEFAULT_LIMIT', '1000')),
            
            # MCP configuration
            'mcp_server_name': os.getenv('MCP_SERVER_NAME', 'LogMCP Server'),
            'mcp_server_version': os.getenv('MCP_SERVER_VERSION', '1.0.0'),
            
            # Logging configuration
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            
            # Environment mappings
            'env_namespace_mapping': {
                'test': os.getenv('TEST_NAMESPACE', 'zkme-test'),
                'dev': os.getenv('DEV_NAMESPACE', 'zkme-dev'),
                'prod': os.getenv('PROD_NAMESPACE', 'zkme-prod')
            },
            
            # Default service name
            'default_service': os.getenv('DEFAULT_SERVICE', 'zkme-token'),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
    
    def get_loki_gateway_url(self) -> str:
        """Get Loki gateway URL with proper formatting"""
        url = self.get('loki_gateway_url')
        if not url.startswith('http'):
            url = f'http://{url}'
        return url
    
    def get_env_namespace(self, env: str) -> str:
        """Get namespace for environment"""
        mapping = self.get('env_namespace_mapping', {})
        return mapping.get(env, f'zkme-{env}')
    
    def validate(self) -> bool:
        """Validate configuration"""
        required_keys = ['loki_gateway_url', 'mcp_server_name']
        for key in required_keys:
            if not self.get(key):
                raise ValueError(f"Required configuration key '{key}' is missing")
        return True


# Global configuration instance
config = Config()
