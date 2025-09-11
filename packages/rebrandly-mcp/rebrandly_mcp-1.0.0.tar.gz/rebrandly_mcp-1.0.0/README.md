## Rebrandly MCP Server

This MCP server provides tools to interact with [rebrandly.com](https://rebrandly.com) to manage short URLs.

### Prerequisites

- For Option 1:
  - [uv](https://docs.astral.sh/uv/) from Astral
  - [Python 3.13](https://www.python.org/downloads/) or higher
- For Option 2:
  - [Docker](https://www.docker.com/)


### Configuration

Use either of the below option to configure your MCP client. To understand the configuration options, please refer to the [documentation](https://gofastmcp.com/integrations/mcp-json-configuration).

**Option 1: Via uvx**
```json
{
  "mcpServers": {
    "rebrandly-mcp": {
      "command": "uvx",
      "args": [
        "rebrandly-mcp"
      ],
      "env": {
        "REBRANDLY_API_KEY": "__API_KEY__"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```


**Option 2: Via docker**

```json
{
  "mcpServers": {
    "rebrandly-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env",
        "REBRANDLY_API_KEY=__API_KEY__",
        "vimalpaliwal/rebrandly-mcp:latest"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Note:** Replace `__API_KEY__` with your actual API key.


### Available Tools

- `generate_short_url`: Generate a new short URL
- `delete_short_url`: Delete an existing short URL
- `get_or_list_short_url`: Get or list existing short URL(s)

### Basic Usage Examples

- Shorten linkedin.com/in/xxxxx for me
- Get me a short URL for youtube.com/xxxxx having yyyyy as the slug/slashtag
- Delete the short URL for rebrandly.com/xxxx for me please
- List all the short links
