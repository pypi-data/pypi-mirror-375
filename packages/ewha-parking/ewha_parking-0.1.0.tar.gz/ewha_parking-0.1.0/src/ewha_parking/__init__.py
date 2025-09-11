"""
ewha_parking
------------

A Python package for analyzing frequent parking patterns and illegal parking
using trajectory data and GIS layers.

Public API:
- FrequentParking: Detects habitual / frequent parking stays
- IllegalParking: Identifies illegal parking spots based on GIS constraints
"""

from .frequent_parking import FrequentParking
from .illegal_parking import IllegalParking

__all__ = ["FrequentParking", "IllegalParking"]

__version__ = "0.1.0"