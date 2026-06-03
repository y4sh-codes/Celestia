## Architecture

```
Claude Desktop / Cursor
        │
        │  MCP (stdio)
        ▼
  celestia  ◄── You are here
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
