"""
tools/point_to.py

MCP tool: point_to
Tells the telescope to slew to a named celestial object.
The backend resolves the name to coordinates and manages the slew job.
"""

import json
from mcp.server.fastmcp import FastMCP
from celestia import backend_client


def register(mcp: FastMCP) -> None:
    """Attach the point_to tool to the MCP server instance."""

    @mcp.tool()
    def point_to(target: str) -> str:
        """
        Point the telescope at a named celestial target.

        The backend resolves the target name (e.g. "Jupiter", "M31") to
        coordinates and starts a slew job. Returns the job ID so you can
        track progress with get_calibration_status.

        Args:
            target: Common name or catalog ID of the object (e.g. "Jupiter", "M31", "Andromeda Galaxy")
        """
        if not target.strip():
            return "Error: target name cannot be empty."

        try:
            result = backend_client.point_to(target.strip())
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            return f"Error: {e}"
