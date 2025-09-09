![image](https://github.com/user-attachments/assets/d16bd5fe-2057-4a32-a58d-e90bd264d73a)


# Beehiiv MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with the Beehiiv API v2. This server enables Large Language Models (LLMs) to interact with Beehiiv publications and posts through standardized tools.

## Prerequisites

- Python 3.10 or higher
- `uv` package manager
- A Beehiiv account with API access
- Claude Desktop (or another MCP-compatible client)

## Installation

1. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. If rebuilding from scratch, create and set up your project:
```bash
# Create a new directory and navigate into it
mkdir beehiiv-mcp-server
cd beehiiv-mcp-server

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx python-dotenv
```

3. Create a `.env` file in the project root:
```env
BEEHIIV_API_KEY=your_api_key_here
BEEHIIV_PUBLICATION_ID=your_publication_id_here
```

## Claude Desktop Configuration

Add the following to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "beehiiv-mcp-server": {
      "command": "<ABSOLUTE_UV_PATH>",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "<ABSOLUTE_SERVER_PATH>"
      ]
    }
  }
}
```

Replace:
- `<ABSOLUTE_UV_PATH>` with the path to your `uv` executable
- `<ABSOLUTE_SERVER_PATH>` with the absolute path to your `beehiiv_server.py` file

## Available Tools

This MCP server currently exposes the following tools (more will be added):

### list_publications
Lists all publications accessible with your API key.

### list_posts
Lists the 5 most recent confirmed posts for a given publication.
```python
list_posts(publication_id: str)
```

### get_post
Retrieves detailed information about a specific post.
```python
get_post(publication_id: str, post_id: str)
```

### get_post_content
Retrieves full HTML content for a post

### create_new_post
Creates new post on beehiiv platform (enterprise only)

## How It Works

When you interact with this server through Claude Desktop:

1. The client sends your question to Claude
2. Claude analyzes the available Beehiiv tools and decides which one(s) to use
3. The client executes the chosen tool(s) through this MCP server
4. The results are sent back to Claude
5. Claude formulates a natural language response
6. The response is displayed to you

(video coming soon)

## Troubleshooting

### Server Not Showing Up in Claude

1. Check your `claude_desktop_config.json` file syntax
2. Ensure all paths are absolute, not relative
3. Restart Claude Desktop

### Viewing Logs

Check Claude's logs for MCP-related issues:
```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
```

Logs are stored in:
- `~/Library/Logs/Claude/mcp.log` for general MCP connections
- `~/Library/Logs/Claude/mcp-server-beehiiv-mcp-server.log` for server-specific logs

## Security

- Never commit your `.env` file to version control
- Keep your Beehiiv API key secure
- Consider implementing rate limiting for API calls

## Contributing

hmu on X (https://x.com/reymerekar7)

