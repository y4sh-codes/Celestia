"""
server.py

Entry point for the Celestia server.

Responsibility: create the FastMCP instance, register all tools,
and start the server. Nothing else lives here — keep it as a
thin wiring layer so adding a new tool is a two-line change.
"""

import sys
from mcp.server.fastmcp import FastMCP

# Import each tool module so we can call its register() function
from celestia.tools import (
    point_to,
    get_calibration_status,
    get_current_orientation,
    abort_calibration,
    list_visible_objects,
    get_telescope_status,
    manual_slew,
)

# The server name appears in Claude Desktop / Cursor UI
mcp = FastMCP("CAPIBARA Telescope Control")


def _register_tools() -> None:
    """Wire every tool module into the MCP server."""
    point_to.register(mcp)
    get_calibration_status.register(mcp)
    get_current_orientation.register(mcp)
    abort_calibration.register(mcp)
    list_visible_objects.register(mcp)
    get_telescope_status.register(mcp)
    manual_slew.register(mcp)


def main() -> None:
    """Start the MCP server (called by the Poetry script entry point)."""
    # Log to stderr — stdout is reserved for the MCP stdio protocol
    print(" Celestia MCP server starting", file=sys.stderr)
    _register_tools()
    print(" 7 tools registered and ready", file=sys.stderr)
    print(f" Waiting for MCP client (Claude Desktop / Cursor)", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
