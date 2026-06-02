"""
tools/get_calibration_status.py

MCP tool: get_calibration_status
Polls the backend for the status of a running calibration or alignment job.
Useful for watching convergence: iteration count and error in arcseconds.
"""

import json
from mcp.server.fastmcp import FastMCP
from celestia import backend_client


def register(mcp: FastMCP) -> None:
    """Attach the get_calibration_status tool to the MCP server instance."""

    @mcp.tool()
    def get_calibration_status(job_id: str) -> str:
        """
        Check the current status of a calibration or alignment job.

        Returns iteration count, pointing error in arcseconds, and job status.
        Call this repeatedly to watch a calibration converge.

        Args:
            job_id: The job ID returned by point_to or a calibration start call.
        """
        if not job_id.strip():
            return "Error: job_id cannot be empty."

        try:
            result = backend_client.get_calibration_status(job_id.strip())
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            return f"Error: {e}"
