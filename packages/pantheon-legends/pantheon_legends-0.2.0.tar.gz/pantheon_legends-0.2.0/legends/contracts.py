"""
Core contracts and interfaces for Pantheon Legends.

Converted from C# contracts to idiomatic Python using dataclasses and type hints.
Enhanced with explicit distinctions between Traditional Legends and Scanner Engines.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Protocol, Callable, Awaitable
from datetime import datetime
from enum import Enum
import asyncio


# --- Legend Type Classifications ---

class LegendType(Enum):
    """
    Classification of analysis engine types.
    
    TRADITIONAL: Classical methodologies by legendary analysts (Dow, Wyckoff, etc.)
    SCANNER: Modern algorithmic detection engines
    HYBRID: Combines both traditional and scanner approaches
    """
    TRADITIONAL = "traditional"
    SCANNER = "scanner"
    HYBRID = "hybrid"


class ReliabilityLevel(Enum):
    """
    Expected reliability levels for different engine types.
    
    HIGH: Traditional legends with decades of market validation
    MEDIUM: Enhanced scanners with quality controls
    VARIABLE: Basic scanners, prone to false signals
    EXPERIMENTAL: New or unvalidated approaches
    """
    HIGH = "high"
    MEDIUM = "medium"
    VARIABLE = "variable"
    EXPERIMENTAL = "experimental"


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
    Enhanced data quality assessment metadata with legend type awareness.
    
    Args:
        sample_size: Number of data points analyzed
        freshness_sec: Age of the most recent data in seconds
        data_completeness: Completeness ratio (0.0 to 1.0)
        reliability_level: Expected reliability of this engine type
        false_positive_risk: Risk of false signals (0.0-1.0, higher for scanners)
        manipulation_sensitivity: Sensitivity to market manipulation (0.0-1.0)
        validation_period_years: Historical validation period (None for scanners)
    """
    sample_size: float
    freshness_sec: float
    data_completeness: float
    reliability_level: ReliabilityLevel
    false_positive_risk: float
    manipulation_sensitivity: float
    validation_period_years: Optional[float] = None


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
    Enhanced protocol defining the interface for all legend engines.
    
    Legend engines are responsible for analyzing financial data
    and producing insights based on specific methodologies (Dow Theory, Wyckoff, etc.)
    or modern algorithmic detection (scanners).
    """
    
    @property
    def name(self) -> str:
        """
        Name of the legend engine (e.g., "Dow Theory", "Volume Breakout Scanner").
        """
        ...
    
    @property
    def legend_type(self) -> LegendType:
        """
        Classification of this engine type (Traditional, Scanner, or Hybrid).
        """
        ...
    
    @property
    def reliability_level(self) -> ReliabilityLevel:
        """
        Expected reliability level of this engine.
        """
        ...
    
    @property
    def description(self) -> str:
        """
        Human-readable description of the methodology and its limitations.
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


# --- Base Classes for Different Legend Types ---

class TraditionalLegendBase:
    """
    Base class for traditional technical analysis legends.
    
    Provides common functionality and appropriate defaults for legends
    based on proven methodologies by legendary analysts.
    """
    
    @property
    def legend_type(self) -> LegendType:
        return LegendType.TRADITIONAL
    
    @property
    def reliability_level(self) -> ReliabilityLevel:
        return ReliabilityLevel.HIGH
    
    def _create_quality_meta(
        self,
        sample_size: float,
        freshness_sec: float,
        data_completeness: float,
        validation_years: float
    ) -> QualityMeta:
        """Create quality metadata appropriate for traditional legends."""
        return QualityMeta(
            sample_size=sample_size,
            freshness_sec=freshness_sec,
            data_completeness=data_completeness,
            reliability_level=self.reliability_level,
            false_positive_risk=0.1,  # Low for traditional methods
            manipulation_sensitivity=0.2,  # Less sensitive to manipulation
            validation_period_years=validation_years
        )


class ScannerEngineBase:
    """
    Base class for scanner-based detection engines.
    
    Provides common functionality and appropriate defaults for modern
    algorithmic detection engines with variable reliability.
    """
    
    @property
    def legend_type(self) -> LegendType:
        return LegendType.SCANNER
    
    @property
    def reliability_level(self) -> ReliabilityLevel:
        return ReliabilityLevel.VARIABLE  # Override in subclasses if needed
    
    def _create_quality_meta(
        self,
        sample_size: float,
        freshness_sec: float,
        data_completeness: float,
        false_positive_risk: float = 0.3,
        manipulation_sensitivity: float = 0.7
    ) -> QualityMeta:
        """Create quality metadata appropriate for scanner engines."""
        return QualityMeta(
            sample_size=sample_size,
            freshness_sec=freshness_sec,
            data_completeness=data_completeness,
            reliability_level=self.reliability_level,
            false_positive_risk=false_positive_risk,
            manipulation_sensitivity=manipulation_sensitivity,
            validation_period_years=None  # Scanners typically don't have long validation
        )
