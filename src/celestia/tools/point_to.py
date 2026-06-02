"""
tools/point_to.py

MCP tool: point_to

Claude (the client running in Claude Desktop / Cursor) reads this tool's
docstring before calling it. The docstring carries all the instructions
needed for Claude to classify the target, ask the user for their location
if not already known, and populate resolver + input_body correctly.
"""

import json
from mcp.server.fastmcp import FastMCP
from celestia import backend_client


def register(mcp: FastMCP) -> None:
    """Attach the point_to tool to the MCP server instance."""

    @mcp.tool()
    def point_to(
        target: str,
        resolver: str,
        input_body: dict,
    ) -> str:
        """
        Point the telescope at a named celestial target.

        Before calling this tool, YOU (Claude) must:
          1. Classify the target (see CLASSIFICATION RULES below)
          2. Know the user's observer location (see OBSERVER LOCATION below)
          3. Build input_body in the correct format (see INPUT_BODY FORMAT below)

        OBSERVER LOCATION
        ──────────────────
        The location block inside input_body requires the observer's:
          - lon       : longitude in decimal degrees (e.g. 85.13)
          - lat       : latitude  in decimal degrees (e.g. 25.99)
          - elevation : elevation above sea level in kilometres (e.g. 0.053)

        If you do not already know the user's location from this conversation,
        STOP and ask them before calling this tool:
          "What is your location? (city or coordinates, and approximate elevation)"

        Convert a city name to approximate decimal lon/lat/elevation using your
        knowledge. If the user provides coordinates directly, use them as-is.
        If elevation is not mentioned, use 0.0 as a safe default.

        CLASSIFICATION RULES
        ─────────────────────
        Solar system bodies → resolver = "horizons"
          Includes: planets (Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune),
          dwarf planets (Pluto, Ceres, Eris…), moons (Moon, Titan, Europa…),
          comets (Halley, 67P, Hale-Bopp…), asteroids (Apophis, Vesta…), the Sun.

        Everything else → resolver = "simbad"
          Includes: nebulae, galaxies, star clusters, individual stars (other than
          the Sun), and any object outside our solar system.
          Examples: Orion Nebula, M31, Andromeda Galaxy, Pleiades, Betelgeuse, NGC 224.

        INPUT_BODY FORMAT
        ──────────────────
        For resolver = "horizons" (solar system bodies):
          {
            "id": "<target name or JPL numeric ID>",
            "location": {
              "lon": <user longitude as float>,
              "lat": <user latitude as float>,
              "elevation": <user elevation in km as float>
            },
            "epochs": "Time.now().jd",
            "id_type": "majorbody"
          }
          Use id_type "smallbody" for asteroids and comets.
          Location must come from the user — never hardcode it.

        For resolver = "simbad" (deep sky objects):
          {
            "name": "<target name>"
          }
          Simbad does not need a location — observer position is irrelevant
          for fixed deep sky coordinates.

        EXAMPLES
        ─────────
        User in London (lon=-0.12, lat=51.51, elevation=0.011):
          "Jupiter"      → resolver="horizons", input_body={"id":"Jupiter","location":{"lon":-0.12,"lat":51.51,"elevation":0.011},"epochs":"Time.now().jd","id_type":"majorbody"}
          "Apophis"      → resolver="horizons", input_body={"id":"Apophis","location":{"lon":-0.12,"lat":51.51,"elevation":0.011},"epochs":"Time.now().jd","id_type":"smallbody"}

        Any location:
          "Orion Nebula" → resolver="simbad", input_body={"name":"Orion Nebula"}
          "M31"          → resolver="simbad", input_body={"name":"M31"}

        Args:
            target:     Human-readable name of the object (used for job metadata).
            resolver:   "horizons" for solar system bodies, "simbad" for deep sky objects.
            input_body: Pre-formatted dict for the chosen resolver (see formats above).
        """
        if not target.strip():
            return "Error: target name cannot be empty."

        if resolver not in ("horizons", "simbad"):
            return f"Error: resolver must be 'horizons' or 'simbad', got '{resolver}'."

        if not isinstance(input_body, dict) or not input_body:
            return "Error: input_body must be a non-empty dict."

        # Validate that horizons payloads always carry a real location
        if resolver == "horizons":
            location = input_body.get("location", {})
            if not isinstance(location, dict) or "lon" not in location or "lat" not in location:
                return (
                    "Error: input_body.location with 'lon' and 'lat' is required "
                    "for resolver='horizons'. Ask the user for their location first."
                )

        try:
            result = backend_client.point_to(
                target=target.strip(),
                resolver=resolver,
                input_body=input_body,
            )
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            return f"Error: {e}"
