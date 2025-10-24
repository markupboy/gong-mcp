# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server implementation that provides access to Gong's API for retrieving call recordings and transcripts. The server enables Claude to interact with Gong data through a standardized MCP interface.

Built with [FastMCP](https://github.com/jlowin/fastmcp), the fast, Pythonic way to build MCP servers.

## Key Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server directly
python -m gong_mcp.server

# Or use FastMCP CLI
fastmcp run src/gong_mcp/server.py
```

### Docker
```bash
# Build Docker container
docker build -t gong-mcp .

# Run container with credentials
docker run -it --rm \
  -e GONG_ACCESS_KEY=your_key \
  -e GONG_ACCESS_SECRET=your_secret \
  gong-mcp
```

## Architecture

### Core Components

The server is implemented in a Python package structure under `src/gong_mcp/`:

1. **GongClient Class** ([src/gong_mcp/server.py](src/gong_mcp/server.py)) - Handles all Gong API interactions with HMAC-SHA256 signature-based authentication using `httpx` for HTTP requests
2. **FastMCP Server** - Built on FastMCP framework, exposes two tools to Claude using decorator-based tool registration
3. **STDIO Transport** - FastMCP automatically handles stdin/stdout communication following MCP protocol

### Authentication Flow

The GongClient uses a custom authentication mechanism:
- Basic Auth header with base64-encoded credentials
- Additional headers: `X-Gong-AccessKey`, `X-Gong-Timestamp`, `X-Gong-Signature`
- Signature is HMAC-SHA256 of: `METHOD\nPATH\nTIMESTAMP\nBODY/PARAMS`
- Uses Python's `hmac` and `hashlib` libraries for signature generation

### MCP Tools

The server exposes two tools using FastMCP's `@mcp.tool()` decorator:

1. **list_calls** - Lists Gong calls with optional date range filtering (`from_date_time`, `to_date_time` in ISO format)
2. **retrieve_transcripts** - Retrieves detailed transcripts for a list of call IDs, including speaker IDs, topics, and timestamped sentences

FastMCP automatically generates JSON schemas from Python type hints, making tool definitions type-safe and self-documenting.

### Configuration

Environment variables (required):
- `GONG_ACCESS_KEY` - Gong API access key
- `GONG_ACCESS_SECRET` - Gong API secret

Create a `.env` file based on `.env.example` for local development. The server uses `python-dotenv` to load environment variables.

### Type Safety

The codebase uses Python type hints with dataclasses:
- `GongCall` - Dataclass for call metadata structure
- Function parameters and return types are fully annotated
- FastMCP uses type hints to automatically generate tool schemas

### Error Handling

Tools wrap API calls in try-except blocks and return JSON strings with error information when exceptions occur, ensuring graceful error handling in the MCP protocol.
