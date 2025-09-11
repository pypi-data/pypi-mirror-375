from loguru import logger

from rebrandly_mcp.server import mcp

import rebrandly_mcp.prompts  # noqa: F401
import rebrandly_mcp.tools  # noqa: F401


def main():
    logger.info("Starting rebrandly.com MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
