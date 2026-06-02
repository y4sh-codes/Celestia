"""
target_classifier.py

Classification is handled by Claude itself at the tool-call level.

Why no API call needed:
  Claude (in Claude Desktop / Cursor) reads the point_to tool's docstring
  before deciding how to call it. The docstring instructs Claude to pass
  the correct resolver and input_body format based on its own astronomical
  knowledge. No separate classification step or API key required.

This file only defines the TargetType enum so the rest of the codebase
has a clean type to work with.
"""

from enum import Enum


class TargetType(Enum):
    SOLAR_SYSTEM = "solar_system"  # → JPL Horizons
    DEEP_SKY = "deep_sky"          # → Simbad
