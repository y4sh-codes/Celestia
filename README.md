## Project Structure

```
celestia/
├── pyproject.toml
├── README.md
├── .env.example
└── src/
    └── celestia/
        ├── server.py            # Entry point, registers all tools
        ├── backend_client.py    # All HTTP calls to the backend
        └── tools/
            ├── point_to.py
            ├── get_calibration_status.py
            ├── get_current_orientation.py
            ├── abort_calibration.py
            ├── list_visible_objects.py
            ├── get_telescope_status.py
            └── manual_slew.py
```
