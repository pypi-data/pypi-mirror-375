"""
Pantheon Legends Python Package

A Python implementation of the Pantheon Legends model for financial market analysis.
"""

from .contracts import (
    LegendRequest,
    LegendProgress,
    LegendEnvelope,
    QualityMeta,
    ILegendEngine
)
from .engines import DowLegendEngine
from .pantheon import Pantheon

__version__ = "0.1.0"
__all__ = [
    "LegendRequest",
    "LegendProgress", 
    "LegendEnvelope",
    "QualityMeta",
    "ILegendEngine",
    "DowLegendEngine",
    "Pantheon"
]
