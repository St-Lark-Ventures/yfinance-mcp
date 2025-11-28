#!/usr/bin/env python
import os
from typing import Literal
from yfinance_mcp import server


def transport() -> Literal["stdio", "sse", "streamable-http"]:
    """
    Determine the transport type for the MCP server.
    Defaults to 'stdio' if not set in environment variables.
    """
    mcp_transport_str = os.environ.get("MCP_TRANSPORT", "stdio")

    # These are currently the only supported transports
    supported_transports: dict[str, Literal["stdio", "sse", "streamable-http"]] = {
        "stdio": "stdio",
        "sse": "sse",
        "streamable-http": "streamable-http",
    }

    return supported_transports.get(mcp_transport_str, "stdio")


def start_server():
    print("Starting Yahoo Finance MCP server.")
    server.run(transport=transport())


if __name__ == "__main__":
    start_server()
