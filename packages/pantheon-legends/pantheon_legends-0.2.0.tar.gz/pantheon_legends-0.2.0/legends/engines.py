"""
Example/demo legend engine implementations.

This module provides demo implementations of the ILegendEngine protocol,
demonstrating how to build custom legend engines for financial analysis.

**IMPORTANT**: These are demonstration engines that generate sample data.
- Traditional legends (Dow, Wyckoff) do NOT implement actual methodologies
- Scanner engines show the structure for algorithmic detection
They serve as examples of the framework structure for building real engines.
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

from .contracts import (
    ILegendEngine,
    LegendRequest,
    LegendProgress,
    LegendEnvelope,
    QualityMeta,
    ProgressCallback,
    TraditionalLegendBase,
    ScannerEngineBase,
    LegendType,
    ReliabilityLevel
)


class DowLegendEngine(TraditionalLegendBase):
    """
    Demo implementation showing the structure for a Dow Theory legend engine.
    
    **WARNING**: This is a demonstration engine that generates sample data.
    It does NOT implement actual Dow Theory analysis. It serves as an example
    of how to structure a real Dow Theory implementation using the framework.
    
    For real Dow Theory analysis, you would need to:
    - Implement actual trend identification algorithms
    - Analyze volume confirmation patterns
    - Identify primary/secondary trend relationships
    - Use real market data instead of sample data
    """

    @property
    def name(self) -> str:
        """Return the name of this legend engine."""
        return "Dow Theory"
    
    @property
    def description(self) -> str:
        """Return a description of this legend engine."""
        return "Demo engine for Dow Theory trend analysis (sample data only)"

    async def run_async(
        self,
        request: LegendRequest,
        progress_callback: Optional[ProgressCallback] = None
    ) -> LegendEnvelope:
        """
        Execute Dow Theory analysis (demo version with sample data).
        
        Args:
            request: Analysis request with symbol, timeframe, etc.
            progress_callback: Optional callback for progress updates
            
        Returns:
            LegendEnvelope containing sample analysis results
            
        **WARNING**: This returns sample data for demonstration purposes only.
        """
        # Report progress stages
        await self._report_progress("initialization", 0.0, "Starting Dow Theory analysis", progress_callback)
        await asyncio.sleep(0.1)  # Simulate work
        
        await self._report_progress("trend_analysis", 25.0, "Identifying primary trends", progress_callback)
        await asyncio.sleep(0.2)
        
        await self._report_progress("volume_confirmation", 50.0, "Analyzing volume patterns", progress_callback)
        await asyncio.sleep(0.15)
        
        await self._report_progress("signal_generation", 75.0, "Generating signals", progress_callback)
        await asyncio.sleep(0.1)
        
        await self._report_progress("completion", 100.0, "Analysis complete", progress_callback)
        
        # Sample facts (in real implementation, these would come from actual analysis)
        facts = {
            "primary_trend": "bullish",
            "secondary_trend": "neutral", 
            "volume_confirmation": True,
            "trend_strength": 0.65,
            "analysis_note": "DEMO DATA - Not real Dow Theory analysis"
        }
        
        quality = self._create_quality_meta(
            sample_size=1000.0,
            freshness_sec=30.0,
            data_completeness=0.98,
            validation_years=125.0  # Dow Theory ~125 years of validation
        )
        
        return LegendEnvelope(
            legend=self.name,
            at=request.as_of,
            tf=request.timeframe,
            facts=facts,
            quality=quality
        )

    async def _report_progress(
        self,
        stage: str,
        percent: float,
        note: str,
        progress_callback: Optional[ProgressCallback]
    ) -> None:
        """Helper method to report progress if callback is provided."""
        if progress_callback:
            progress = LegendProgress(
                legend=self.name,
                stage=stage,
                percent=percent,
                note=note
            )
            await progress_callback(progress)


class WyckoffLegendEngine(TraditionalLegendBase):
    """
    Demo implementation showing the structure for a Wyckoff Method legend engine.
    
    **WARNING**: This is a demonstration engine that generates sample data.
    It does NOT implement actual Wyckoff Method analysis. It serves as an example
    of how to structure a real Wyckoff implementation using the framework.
    
    For real Wyckoff analysis, you would need to:
    - Implement supply/demand zone identification
    - Analyze effort vs result relationships
    - Identify accumulation/distribution phases
    - Track smart money vs public sentiment
    """

    @property
    def name(self) -> str:
        """Return the name of this legend engine."""
        return "Wyckoff Method"
    
    @property
    def description(self) -> str:
        """Return a description of this legend engine."""
        return "Demo engine for Wyckoff Method supply/demand analysis (sample data only)"

    async def run_async(
        self,
        request: LegendRequest,
        progress_callback: Optional[ProgressCallback] = None
    ) -> LegendEnvelope:
        """
        Execute Wyckoff Method analysis (demo version with sample data).
        
        Args:
            request: Analysis request with symbol, timeframe, etc.
            progress_callback: Optional callback for progress updates
            
        Returns:
            LegendEnvelope containing sample analysis results
            
        **WARNING**: This returns sample data for demonstration purposes only.
        """
        # Report progress stages
        await self._report_progress("initialization", 0.0, "Starting Wyckoff analysis", progress_callback)
        await asyncio.sleep(0.1)
        
        await self._report_progress("supply_demand", 30.0, "Mapping supply/demand zones", progress_callback)
        await asyncio.sleep(0.25)
        
        await self._report_progress("effort_result", 60.0, "Analyzing effort vs result", progress_callback)
        await asyncio.sleep(0.2)
        
        await self._report_progress("phase_identification", 85.0, "Identifying market phase", progress_callback)
        await asyncio.sleep(0.15)
        
        await self._report_progress("completion", 100.0, "Analysis complete", progress_callback)
        
        # Sample facts (in real implementation, these would come from actual analysis)
        facts = {
            "market_phase": "accumulation",
            "supply_zones": [45.20, 47.80],
            "demand_zones": [42.10, 43.90],
            "effort_vs_result": "bullish_divergence",
            "smart_money_activity": 0.72,
            "analysis_note": "DEMO DATA - Not real Wyckoff analysis"
        }
        
        quality = self._create_quality_meta(
            sample_size=800.0,
            freshness_sec=45.0,
            data_completeness=0.95,
            validation_years=100.0  # Wyckoff Method ~100 years of validation
        )
        
        return LegendEnvelope(
            legend=self.name,
            at=request.as_of,
            tf=request.timeframe,
            facts=facts,
            quality=quality
        )

    async def _report_progress(
        self,
        stage: str,
        percent: float,
        note: str,
        progress_callback: Optional[ProgressCallback]
    ) -> None:
        """Helper method to report progress if callback is provided."""
        if progress_callback:
            progress = LegendProgress(
                legend=self.name,
                stage=stage,
                percent=percent,
                note=note
            )
            await progress_callback(progress)


class VolumeBreakoutScanner(ScannerEngineBase):
    """
    Example scanner engine for volume breakout detection.
    
    **WARNING**: This scanner may produce false signals due to:
    - Whale manipulation creating artificial volume spikes
    - News events causing fundamental (not technical) volume
    - Low liquidity periods amplifying normal activity
    """
    
    @property
    def name(self) -> str:
        """Return the name of this scanner engine."""
        return "Volume Breakout Scanner"
    
    @property 
    def description(self) -> str:
        """Return a description of this scanner engine."""
        return "Algorithmic detection of unusual volume patterns with breakout confirmation"

    async def run_async(
        self,
        request: LegendRequest,
        progress_callback: Optional[ProgressCallback] = None
    ) -> LegendEnvelope:
        """
        Execute volume breakout scanning (demo version with sample data).
        
        Args:
            request: Analysis request with symbol, timeframe, etc.
            progress_callback: Optional callback for progress updates
            
        Returns:
            LegendEnvelope containing sample scan results
        """
        # Report progress stages
        await self._report_progress("initialization", 0.0, "Initializing volume scanner", progress_callback)
        await asyncio.sleep(0.05)
        
        await self._report_progress("volume_analysis", 40.0, "Analyzing volume patterns", progress_callback)
        await asyncio.sleep(0.1)
        
        await self._report_progress("breakout_detection", 80.0, "Detecting breakout signals", progress_callback)
        await asyncio.sleep(0.08)
        
        await self._report_progress("completion", 100.0, "Scan complete", progress_callback)
        
        # Sample facts (in real implementation, these would come from actual scanning)
        facts = {
            "volume_spike_detected": True,
            "volume_ratio": 2.3,  # 2.3x normal volume
            "breakout_direction": "upward",
            "price_confirmation": True,
            "scan_timestamp": datetime.now().isoformat(),
            "analysis_note": "DEMO DATA - Not real volume scanning"
        }
        
        quality = self._create_quality_meta(
            sample_size=200.0,  # Smaller sample for recent data
            freshness_sec=5.0,   # Very fresh for scanner
            data_completeness=0.92,
            validation_years=5.0,  # Shorter validation period
            false_positive_risk=0.35,  # Higher false positive risk
            manipulation_sensitivity=0.8  # High sensitivity to manipulation
        )
        
        return LegendEnvelope(
            legend=self.name,
            at=request.as_of,
            tf=request.timeframe,
            facts=facts,
            quality=quality
        )

    async def _report_progress(
        self,
        stage: str,
        percent: float,
        note: str,
        progress_callback: Optional[ProgressCallback]
    ) -> None:
        """Helper method to report progress if callback is provided."""
        if progress_callback:
            progress = LegendProgress(
                legend=self.name,
                stage=stage,
                percent=percent,
                note=note
            )
            await progress_callback(progress)
