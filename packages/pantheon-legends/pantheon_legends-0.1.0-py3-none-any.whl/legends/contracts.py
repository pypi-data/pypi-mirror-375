"""
Core contracts and interfaces for Pantheon Legends.

Converted from C# contracts to idiomatic Python using dataclasses and type hints.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Protocol, Callable, Awaitable
from datetime import datetime
import asyncio


# --- Data Transfer Objects ---

@dataclass(frozen=True)
class LegendRequest:
    """
    Request to run a legend analysis.
    
    Args:
        symbol: Financial instrument symbol (e.g., "AAPL", "MSFT")
        timeframe: Time interval for analysis (e.g., "1d", "1h", "5m")
        as_of: Point in time for the analysis
    """
    symbol: str
    timeframe: str
    as_of: datetime


@dataclass(frozen=True)
class LegendProgress:
    """
    Progress update during legend execution.
    
    Args:
        legend: Name of the legend being executed (e.g., "Dow", "Wyckoff")
        stage: Current processing stage (e.g., "fetch", "compute", "score")
        percent: Completion percentage (0.0 to 100.0)
        note: Optional human-readable progress note
    """
    legend: str
    stage: str
    percent: float
    note: Optional[str] = None


@dataclass(frozen=True)
class QualityMeta:
    """
    Metadata about the quality of the analysis results.
    
    Args:
        sample_size: Number of data points analyzed
        freshness_sec: Age of the most recent data in seconds
        data_completeness: Completeness ratio (0.0 to 1.0)
    """
    sample_size: float
    freshness_sec: float
    data_completeness: float


@dataclass(frozen=True)
class LegendEnvelope:
    """
    Complete result envelope from a legend analysis.
    
    Args:
        legend: Name of the legend that produced this result
        at: Timestamp when the analysis was performed
        tf: Timeframe used for the analysis
        facts: Dictionary of analysis results and metrics
        quality: Quality metadata for the analysis
    """
    legend: str
    at: datetime
    tf: str
    facts: Dict[str, Any]
    quality: QualityMeta


# --- Progress Callback Type ---

ProgressCallback = Callable[[LegendProgress], Awaitable[None]]


# --- Legend Engine Interface ---

class ILegendEngine(Protocol):
    """
    Protocol defining the interface for all legend engines.
    
    Legend engines are responsible for analyzing financial data
    and producing insights based on specific methodologies (Dow Theory, Wyckoff, etc.).
    """
    
    @property
    def name(self) -> str:
        """
        Name of the legend engine (e.g., "Dow", "Wyckoff", "Elliott").
        """
        ...

    async def run_async(
        self,
        request: LegendRequest,
        progress_callback: Optional[ProgressCallback] = None
    ) -> LegendEnvelope:
        """
        Execute the legend analysis asynchronously.
        
        Args:
            request: The analysis request containing symbol, timeframe, and timestamp
            progress_callback: Optional callback to receive progress updates
            
        Returns:
            LegendEnvelope containing the analysis results and quality metadata
            
        Raises:
            ValueError: If the request parameters are invalid
            RuntimeError: If the analysis fails due to data or processing issues
        """
        ...
