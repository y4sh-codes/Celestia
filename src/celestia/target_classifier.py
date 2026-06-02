"""
target_classifier.py

Classification is handled by Claude itself at the tool-call level.

"""

from enum import Enum


class TargetType(Enum):
    SOLAR_SYSTEM = "solar_system"  # → JPL Horizons
    DEEP_SKY = "deep_sky"          # → Simbad
