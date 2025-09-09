# Solscan MCP Server

A Model Context Protocol (MCP) server implementation for interacting with the Solscan Pro API. This server allows AI agents to fetch and analyze token, transaction, and DeFi activity data from the Solana blockchain.

## Overview

This MCP server provides a bridge between AI agents and the Solscan Pro API service. It follows the best practices laid out by Anthropic for building MCP servers, allowing seamless integration with any MCP-compatible client.

## Features

The server provides several essential tools for interacting with Solscan:

1. **`token_meta`**: Get token metadata

   - Fetch comprehensive token information
   - Get name, symbol, price, market cap, etc.

2. **`token_markets`**: Get token market data and liquidity pools

   - View market pairs and liquidity pools
   - Filter by program addresses
   - Sort and paginate results

3. **`token_holders`**: Get token holder distribution

   - View holder balances and distribution
   - Filter by amount ranges
   - Paginate through results

4. **`token_price`**: Get token price information

   - Historical price data
   - Filter by date range
   - Price trends and statistics

5. **`token_accounts`**: Get token holdings for a wallet

   - List token and NFT holdings
   - Filter zero balances
   - Paginate results

6. **`defi_activities`**: Get DeFi activities for a wallet

   - Filter by activity type and platform
   - Sort by time or other metrics
   - Comprehensive activity details

7. **`balance_change`**: Get balance change activities

   - Track token balance changes
   - Filter by token and amount
   - Remove spam transactions

8. **`account_transactions`**: Get wallet transactions

   - List wallet transactions
   - Paginate through transaction history
   - Configurable result limits

9. **`transaction_detail`**: Get transaction information

   - Detailed transaction data
   - Parsed instructions
   - Fee information

10. **`transaction_actions`**: Get transaction actions

- List token transfers
- View program interactions
- Decoded instruction data

## Prerequisites

- Python 3.10+
- Solscan Pro API key (obtain from [Solscan APIs](https://solscan.io/apis))
- Docker if running the MCP server as a container (recommended)

## Installation

### Using uv (Recommended)

When using [`uv`](https://docs.astral.sh/uv/), no specific installation is needed. We use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run _solscan-mcp-server_.

### Using pip

Alternatively, install via pip:

```bash
pip install solscan-mcp-server
```

## Configuration

You can configure the server using either environment variables or command-line arguments:

| Option    | Env Variable    | CLI Argument | Default   | Description                                |
| --------- | --------------- | ------------ | --------- | ------------------------------------------ |
| API Key   | SOLSCAN_API_KEY | --api-key    | Required  | Your Solscan Pro API key                   |
| Transport | TRANSPORT       | --transport  | sse       | Transport protocol (sse or stdio)          |
| Host      | HOST            | --host       | 127.0.0.1 | Host to bind to when using SSE transport   |
| Port      | PORT            | --port       | 8050      | Port to listen on when using SSE transport |
| Log Level | LOG_LEVEL       | --verbose    | INFO      | Logging level (use -v or -vv for detail)   |

## Running the Server

### Using uvx (Recommended)

```bash
# Using environment variables:
SOLSCAN_API_KEY=your-key uvx solscan-mcp-server

# Using CLI arguments:
uvx solscan-mcp-server --api-key your-key
```

### Using pip Installation

```bash
# Using environment variables:
SOLSCAN_API_KEY=your-key python -m solscan_mcp_server

# Using CLI arguments:
python -m solscan_mcp_server --api-key your-key
```

### Using Docker

```bash
# Build the image
docker build -t solscan-mcp-server .

# Run with environment variables
docker run -e SOLSCAN_API_KEY=your-key solscan-mcp-server
```

## Integration with MCP Clients

### Claude Desktop Configuration

#### Using uvx (Recommended)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "solscan": {
      "command": "uvx",
      "args": ["solscan-mcp-server"]
    }
  }
}
```

#### Using pip Installation

```json
{
  "mcpServers": {
    "solscan": {
      "command": "python",
      "args": ["-m", "solscan_mcp_server"]
    }
  }
}
```

### Zed Configuration

Add to your Zed settings.json:

```json
"context_servers": {
  "solscan": {
    "command": {
      "path": "uvx",
      "args": ["solscan-mcp-server"]
    }
  }
}
```

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

### Code Quality

```bash
# Run type checker
pyright

# Run linter
ruff check .
```

### Debugging

You can use the MCP inspector to debug the server:

```bash
npx @modelcontextprotocol/inspector uvx solscan-mcp-server
```

For development debugging:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
