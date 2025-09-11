# LogMCP Server

A Model Context Protocol (MCP) server implementation for log querying and system monitoring via Loki, using stdio transport.

## Features

- **MCP Protocol Support**: Full implementation of the Model Context Protocol using stdio transport
- **Loki Integration**: Query logs from Loki using LogQL
- **Multiple Environments**: Support for test, dev, and prod environments
- **Flexible Queries**: Keyword-based and time-range-based log queries
- **Error Handling**: Comprehensive error handling and logging
- **Async Support**: Fully asynchronous implementation

## Installation

This project uses [uv](https://github.com/astral-sh/uv) as the package manager.

### Prerequisites

- Python 3.8+
- uv package manager

### Install uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Dependencies

```bash
# Install project dependencies
uv sync

# Install development dependencies
uv sync --dev
```

## Configuration

The server can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOKI_GATEWAY_URL` | Loki gateway URL | `https://dev-hk-loki.bitkinetic.com` |
| `LOKI_TIMEOUT` | Loki query timeout (seconds) | `30` |
| `LOKI_DEFAULT_LIMIT` | Default query result limit | `1000` |
| `LOKI_SSL_VERIFY` | Enable SSL certificate verification | `true` |
| `MCP_SERVER_NAME` | MCP server name | `LogMCP Server` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEFAULT_SERVICE` | Default service name | `zkme-token` |
| `TEST_NAMESPACE` | Test environment namespace | `zkme-test` |
| `DEV_NAMESPACE` | Dev environment namespace | `zkme-dev` |
| `PROD_NAMESPACE` | Prod environment namespace | `zkme-prod` |

### SSL Configuration

For test environments with self-signed certificates, you can disable SSL certificate verification:

```bash
# Disable SSL verification (for test environments only)
export LOKI_SSL_VERIFY=false

# Or enable SSL verification (default, recommended for production)
export LOKI_SSL_VERIFY=true
```

**Security Note**: Only disable SSL verification in test environments. Always keep SSL verification enabled in production environments for security.

## Usage

### Running the Server

```bash
# Using uvx
uvx logmcp

# Or using uv
uv run python main.py

# Or directly with Python
python main.py
```

### MCP Tools

The server provides two main MCP tools:

#### 1. loki_keyword_query

Query logs containing keywords from the last 30 days.

**Parameters:**
- `env` (required): Environment name (test, dev, prod)
- `keywords` (required): Search keywords (comma-separated)
- `service_name` (optional): Service name (default: zkme-token)
- `namespace` (optional): Loki namespace (auto-detected from env)
- `limit` (optional): Result limit (default: 1000)

#### 2. loki_range_query

Query logs containing keywords within a specified time range.

**Parameters:**
- `env` (required): Environment name (test, dev, prod)
- `start_date` (required): Start date (YYYYMMDD format)
- `end_date` (required): End date (YYYYMMDD format)
- `keywords` (required): Search keywords (comma-separated)
- `service_name` (optional): Service name (default: zkme-token)
- `namespace` (optional): Loki namespace (auto-detected from env)
- `limit` (optional): Result limit (default: 1000)

## Development

### Running Tests

```bash
# Run all tests
uvx pytest

# Run tests with coverage
uvx pytest --cov=src/logmcp

# Run specific test file
uvx pytest tests/test_server.py
```

### Code Formatting

```bash
# Format code with black
uvx black src tests

# Sort imports with isort
uvx isort src tests

# Type checking with mypy
uvx mypy src
```

## Project Structure

```
LogMCP/
├── pyproject.toml              # uv project configuration
├── main.py                     # Program entry point
├── README.md                   # Project documentation
├── src/logmcp/
│   ├── __init__.py            # Package initialization
│   ├── server.py              # MCP server implementation
│   ├── tools.py               # MCP tools implementation
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging utilities
│   └── services/
│       ├── __init__.py        # Services package
│       └── loki_service.py    # Loki integration service
└── tests/
    ├── __init__.py            # Test package
    ├── test_server.py         # Server tests
    ├── test_tools.py          # Tools tests
    └── test_loki_service.py   # Loki service tests
```

## License

This project is licensed under the MIT License.
