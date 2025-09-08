"""
Pantheon Legends Python Framework

A Python framework for implementing financial market analysis legend engines.
Provides the structure and contracts for building custom legend implementations.

**Note**: Includes demo engines for demonstration purposes only.
Real legend implementations must be created by users of the framework.
"""

from .contracts import (
    LegendRequest,
    LegendProgress,
    LegendEnvelope,
    QualityMeta,
    ILegendEngine,
    LegendType,
    ReliabilityLevel,
    TraditionalLegendBase,
    ScannerEngineBase
)
from .engines import DowLegendEngine, WyckoffLegendEngine, VolumeBreakoutScanner
from .pantheon import Pantheon
from .scaffold import setup_scanner_as_legend

__version__ = "0.2.0"
__all__ = [
    "LegendRequest",
    "LegendProgress", 
    "LegendEnvelope",
    "QualityMeta",
    "ILegendEngine",
    "LegendType",
    "ReliabilityLevel",
    "TraditionalLegendBase", 
    "ScannerEngineBase",
    "DowLegendEngine",
    "WyckoffLegendEngine",
    "VolumeBreakoutScanner",
    "Pantheon",
    "test_installation",
    "setup_scanner_as_legend"
]


def test_installation():
    """
    Test if Pantheon Legends is properly installed and working.
    
    Returns:
        bool: True if installation is working correctly
    """
    try:
        # Test imports
        from datetime import datetime
        
        # Test basic functionality
        pantheon = Pantheon.create_default()
        engines = pantheon.available_engines
        
        # Test creating a request
        request = LegendRequest(
            symbol="TEST",
            timeframe="1d",
            as_of=datetime.now()
        )
        
        print("✅ Pantheon Legends Installation Test PASSED!")
        print(f"📦 Version: {__version__}")
        print(f"🔧 Available engines: {', '.join(sorted(engines))}")
        print(f"📋 Test request created: {request.symbol} ({request.timeframe})")
        print("🎉 Package is ready to use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Pantheon Legends Installation Test FAILED!")
        print(f"Error: {e}")
        return False
