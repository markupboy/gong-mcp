# Gong MCP Server

A Model Context Protocol (MCP) server that provides access to Gong's API for retrieving call recordings and transcripts. This server allows Claude to interact with Gong data through a standardized interface.

Built with [FastMCP](https://github.com/jlowin/fastmcp), the fast, Pythonic way to build MCP servers.

## Features

- List Gong calls with optional date range filtering
- Retrieve detailed transcripts for specific calls
- Secure authentication using Gong's API credentials
- Standardized MCP interface for easy integration with Claude

## Prerequisites

- Python 3.10 or higher
- Docker (optional, for containerized deployment)
- Gong API credentials (Access Key and Secret)

## Installation

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Gong API credentials
   ```

### Docker

Build the container:
```bash
docker build -t gong-mcp .
```

## Running the Server

### Local Development

Run the server directly:
```bash
python -m gong_mcp.server
```

Or use the FastMCP CLI:
```bash
fastmcp run src/gong_mcp/server.py
```

### Docker

Run the container:
```bash
docker run -it --rm \
  -e GONG_ACCESS_KEY=your_access_key \
  -e GONG_ACCESS_SECRET=your_access_secret \
  gong-mcp
```

## Configuring Claude Desktop

1. Open Claude Desktop settings
2. Navigate to the MCP Servers section
3. Add a new server with the following configuration:

**For Docker deployment:**
```json
{
  "command": "docker",
  "args": [
    "run",
    "-it",
    "--rm",
    "gong-mcp"
  ],
  "env": {
    "GONG_ACCESS_KEY": "your_access_key_here",
    "GONG_ACCESS_SECRET": "your_access_secret_here"
  }
}
```

**For local Python deployment:**
```json
{
  "command": "python",
  "args": [
    "-m",
    "gong_mcp.server"
  ],
  "env": {
    "GONG_ACCESS_KEY": "your_access_key_here",
    "GONG_ACCESS_SECRET": "your_access_secret_here"
  }
}
```

4. Replace the placeholder credentials with your actual Gong API credentials

## Available Tools

### list_calls

List Gong calls with optional date range filtering.

**Parameters:**
- `from_date_time` (optional): Start date/time in ISO format (e.g. `2024-03-01T00:00:00Z`)
- `to_date_time` (optional): End date/time in ISO format (e.g. `2024-03-31T23:59:59Z`)

**Returns:** JSON string containing call details including ID, title, start/end times, participants, and duration.

### retrieve_transcripts

Retrieve transcripts for specified call IDs.

**Parameters:**
- `call_ids` (required): List of Gong call IDs to retrieve transcripts for

**Returns:** JSON string containing detailed transcripts including speaker IDs, topics, and timestamped sentences.

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 
