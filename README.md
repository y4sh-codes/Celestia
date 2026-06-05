# Celestia

MCP server that lets Claude Desktop and Cursor control a telescope through natural language. You say "point to Jupiter" — CAPIBARA figures out the rest.

---

## Architecture

```
Claude Desktop / Cursor
        │
        │  MCP (stdio)
        ▼
  celestia
  (this server)
        │
        │  HTTP (httpx)
        ▼
  CAPIBARA Backend API
  (telescope logic, plate solving,
   calibration, camera, hardware)
        │
        ▼
  Telescope Hardware
```

The MCP server is intentionally thin:
1. Receive tool call from Claude
2. Validate arguments
3. Forward to backend
4. Return result

No astronomy logic lives here.

---

## Project Structure

```
celestia/
├── pyproject.toml
├── README.md
├── SKILL.md
├── .env.example
└── src/
    └── celestia/
        ├── server.py
        ├── backend_client.py
        ├── target_classifier.py
        └── tools/
            ├── point_to.py
            ├── get_calibration_status.py
            ├── get_current_orientation.py
            ├── abort_calibration.py
            ├── list_visible_objects.py
            ├── get_telescope_status.py
            └── manual_slew.py
```

---

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Setup

```bash
# Clone / copy the project
cd celestia

# Create virtualenv and install dependencies
uv sync

# Copy environment config
cp .env.example .env
```

Edit `.env` to point at your backend:

```
BACKEND_BASE_URL=http://localhost:8000
```

### Run the server (standalone test)

```bash
uv run celestia
```

The server starts in stdio mode, waiting for an MCP client to connect.
You should see:

```
🔭 Celestia MCP server starting...
✅ 7 tools registered and ready
⏳ Waiting for MCP client (Claude Desktop / Cursor)...
```

---

## Connecting to Claude Desktop

1. Open Claude Desktop → **Settings → Developer → Edit Config**

2. Add the following to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "celestia": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/celestia", "celestia"],
      "env": {
        "BACKEND_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

3. Restart Claude Desktop. You should see **CAPIBARA Telescope Control** in the tools list.

---

## Connecting to Cursor

1. Open Cursor → **Settings → Features → MCP Servers → Add Server**

2. Set:
   - **Type:** `command`
   - **Command:** `uv`
   - **Args:** `run --directory /absolute/path/to/celestia celestia`

3. Add environment variable: `BACKEND_BASE_URL=http://localhost:8000`

4. Save and reload. The tools will appear in Cursor's Agent mode.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `BACKEND_BASE_URL` | `http://localhost:8000` | Base URL of the CAPIBARA backend API |

---

## Available Tools

### `point_to(target)`
Point the telescope at a named object. Returns a job ID.
Claude will ask for your location if not already known (needed for solar system bodies).
```
"Point to Jupiter"
"Slew to M31"
"Go to the Orion Nebula"
```

### `get_calibration_status(job_id)`
Check the progress of a running calibration or slew job.
```
"What's the status of job_123?"
"How many iterations has the calibration done?"
```

### `get_current_orientation()`
Read the current RA/Dec from the mount.
```
"Where is the telescope pointing?"
"What constellation are we in?"
```

### `abort_calibration(job_id)`
Stop a running job immediately.
```
"Abort job_123"
"Stop the current calibration"
```

### `list_visible_objects()`
See what's up in the sky right now.
```
"What can I observe tonight?"
"List visible objects"
```

### `get_telescope_status()`
Check that all subsystems are online.
```
"Is the telescope ready?"
"What's the system status?"
```

### `manual_slew(dra_arcsec, ddec_arcsec)`
Nudge the mount by a relative offset (max ±3600 arcsec per axis).
```
"Slew 200 arcsec east"
"Nudge the telescope 100 arcsec north and 50 arcsec west"
```

---

## Example Conversation with Claude

```
You: Point the telescope to Jupiter.

Claude: What is your location? (city or coordinates, and approximate elevation)

You: London, UK

Claude: [calls point_to("Jupiter", resolver="horizons", input_body={...})]
        Started pointing to Jupiter. Job ID: job_123, status: running.

You: Is it done?

Claude: [calls get_calibration_status("job_123")]
        Iteration 3, pointing error 50 arcseconds, still running.

You: What's currently visible tonight?

Claude: [calls list_visible_objects()]
        Jupiter (alt: 45°, az: 180°, mag: -2.1) is well-placed for observing.
```

---

## Backend Integration Notes

When the backend team's API is ready, the **only file you need to change is `backend_client.py`**.

Each method maps directly to one backend endpoint:

| Method | Endpoint |
|---|---|
| `point_to()` | `POST /point` |
| `get_calibration_status()` | `GET /jobs/{job_id}` |
| `get_current_orientation()` | `GET /orientation` |
| `abort_calibration()` | `POST /jobs/{job_id}/abort` |
| `list_visible_objects()` | `GET /visible-objects` |
| `get_telescope_status()` | `GET /status` |
| `manual_slew()` | `POST /manual-slew` |

If the backend adds authentication headers, add them once to `_client()` in `backend_client.py` — nothing else changes.

---

## Development

```bash
# Run the server
uv run celestia

# Add a new dependency
uv add some-package

# Check installed packages
uv pip list
```