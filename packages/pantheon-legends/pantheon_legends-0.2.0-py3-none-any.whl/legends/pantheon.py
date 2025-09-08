"""
Pantheon orchestrator for managing multiple legend engines.

This module provides the main Pantheon class that coordinates
multiple legend engines and provides a unified interface with
awareness of Traditional Legends vs Scanner Engines.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Set, Any

import pandas as pd

from .contracts import (
    ILegendEngine,
    LegendRequest,
    LegendProgress,
    LegendEnvelope,
    ProgressCallback,
    LegendType,
    ReliabilityLevel
)
from .engines import DowLegendEngine, WyckoffLegendEngine, VolumeBreakoutScanner


class Pantheon:
    """
    Enhanced orchestrator for Pantheon Legends analysis with type awareness.
    
    Pantheon manages multiple legend engines and provides methods to:
    - Register legend engines with type classification
    - Run single or multiple legend analyses
    - Filter engines by type (Traditional vs Scanner) or reliability
    - Aggregate results with appropriate weighting
    - Generate consensus analysis combining both legend types
    """

    def __init__(self):
        """Initialize Pantheon with an empty registry of legend engines."""
        self._engines: Dict[str, ILegendEngine] = {}
        
    def register_engine(self, engine: ILegendEngine) -> None:
        """
        Register a legend engine with Pantheon.
        
        Args:
            engine: A legend engine implementing ILegendEngine protocol
            
        Raises:
            ValueError: If an engine with the same name is already registered
        """
        if engine.name in self._engines:
            raise ValueError(f"Engine '{engine.name}' is already registered")
        
        self._engines[engine.name] = engine
    
    @property
    def available_engines(self) -> Dict[str, Dict[str, str]]:
        """Get available engines with their type classification."""
        return {
            engine.name: {
                "type": engine.legend_type.value,
                "reliability": engine.reliability_level.value,
                "description": engine.description
            }
            for engine in self._engines.values()
        }
    
    def get_engines_by_type(self, legend_type: LegendType) -> List[ILegendEngine]:
        """Get engines filtered by legend type."""
        return [engine for engine in self._engines.values() 
                if engine.legend_type == legend_type]
    
    def get_engines_by_reliability(self, min_reliability: ReliabilityLevel) -> List[ILegendEngine]:
        """Get engines with at least the specified reliability level."""
        reliability_order = [
            ReliabilityLevel.EXPERIMENTAL, 
            ReliabilityLevel.VARIABLE, 
            ReliabilityLevel.MEDIUM, 
            ReliabilityLevel.HIGH
        ]
        min_index = reliability_order.index(min_reliability)
        
        return [engine for engine in self._engines.values() 
                if reliability_order.index(engine.reliability_level) >= min_index]
    
    def unregister_engine(self, name: str) -> None:
        """
        Unregister a legend engine from Pantheon.
        
        Args:
            name: Name of the engine to unregister
            
        Raises:
            KeyError: If no engine with the given name is registered
        """
        if name not in self._engines:
            raise KeyError(f"No engine named '{name}' is registered")
        
        del self._engines[name]
    
    def get_registered_engines(self) -> List[str]:
        """Get the names of all registered legend engines."""
        return list(self._engines.keys())
    
    async def run_legend_async(
        self,
        engine_name: str,
        request: LegendRequest,
        progress_callback: Optional[ProgressCallback] = None
    ) -> LegendEnvelope:
        """
        Run a specific legend engine asynchronously.
        
        Args:
            engine_name: Name of the legend engine to run
            request: Analysis request
            progress_callback: Optional progress reporting callback
            
        Returns:
            LegendEnvelope with analysis results
            
        Raises:
            KeyError: If the specified engine is not registered
        """
        if engine_name not in self._engines:
            raise KeyError(f"No engine named '{engine_name}' is registered")
        
        engine = self._engines[engine_name]
        return await engine.run_async(request, progress_callback)
    
    async def run_multiple_legends_async(
        self,
        engine_names: List[str],
        request: LegendRequest,
        progress_callback: Optional[ProgressCallback] = None
    ) -> List[LegendEnvelope]:
        """
        Run multiple legend engines concurrently.
        
        Args:
            engine_names: List of engine names to run
            request: Analysis request (same for all engines)
            progress_callback: Optional progress reporting callback
            
        Returns:
            List of LegendEnvelope results, one per engine
            
        Raises:
            KeyError: If any specified engine is not registered
        """
        # Validate all engines exist before starting
        for name in engine_names:
            if name not in self._engines:
                raise KeyError(f"No engine named '{name}' is registered")
        
        # Create tasks for all engines
        tasks = []
        for name in engine_names:
            engine = self._engines[name]
            task = asyncio.create_task(
                engine.run_async(request, progress_callback)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        return results
    
    async def run_all_legends_async(
        self,
        request: LegendRequest,
        progress_callback: Optional[ProgressCallback] = None
    ) -> List[LegendEnvelope]:
        """
        Run all registered legend engines concurrently.
        
        Args:
            request: Analysis request
            progress_callback: Optional progress reporting callback
            
        Returns:
            List of LegendEnvelope results from all engines
        """
        return await self.run_multiple_legends_async(
            list(self._engines.keys()),
            request,
            progress_callback
        )

    @classmethod
    def create_default(cls) -> 'Pantheon':
        """
        Create a Pantheon instance with default legend engines registered.
        
        Returns:
            Pantheon instance with traditional legend engines and a scanner example
        """
        pantheon = cls()
        # Traditional Legends
        pantheon.register_engine(DowLegendEngine())
        pantheon.register_engine(WyckoffLegendEngine())
        # Scanner Engine example
        pantheon.register_engine(VolumeBreakoutScanner())
        return pantheon
    
    def get_consensus_analysis(self, symbol: str, data: pd.DataFrame, 
                             min_reliability: ReliabilityLevel = ReliabilityLevel.MEDIUM,
                             include_scanner_engines: bool = True) -> Dict[str, Any]:
        """
        Get a consensus analysis across multiple engines with reliability weighting.
        
        NOTE: This is a simplified synchronous version for demonstration.
        For real consensus analysis, you would typically run engines asynchronously
        and aggregate their LegendEnvelope results.
        
        Args:
            symbol: The symbol to analyze
            data: Market data DataFrame
            min_reliability: Minimum reliability level to include
            include_scanner_engines: Whether to include scanner engines
            
        Returns:
            Dictionary containing consensus results and engine breakdown
        """
        # Get qualified engines
        qualified_engines = []
        for name, engine in self._engines.items():
            # Check reliability level
            reliability_values = {
                ReliabilityLevel.HIGH: 4,
                ReliabilityLevel.MEDIUM: 3,
                ReliabilityLevel.VARIABLE: 2,
                ReliabilityLevel.EXPERIMENTAL: 1
            }
            
            min_value = reliability_values[min_reliability]
            engine_value = reliability_values[engine.reliability_level]
            
            if engine_value < min_value:
                continue
                
            # Check type filter
            if not include_scanner_engines and engine.legend_type == LegendType.SCANNER:
                continue
                
            qualified_engines.append((name, engine, engine_value))
        
        if not qualified_engines:
            return {
                'consensus_signal': None,
                'confidence': 0.0,
                'qualified_engines': 0,
                'engine_results': {}
            }
        
        # For demonstration, we'll simulate engine results
        # In a real implementation, you'd run the engines with actual requests
        engine_results = {}
        total_weight = 0
        weighted_signals = 0
        
        for name, engine, weight in qualified_engines:
            try:
                # Simulate engine analysis (would normally call engine.run_async)
                # Different engines would have different logic here
                simulated_signal = 1 if "Dow" in name else (-1 if "Wyckoff" in name else 0)
                
                engine_results[name] = {
                    'simulated_signal': simulated_signal,
                    'weight': weight,
                    'type': engine.legend_type.value,
                    'reliability': engine.reliability_level.value,
                    'note': 'Simulated result - would normally run engine analysis'
                }
                
                weighted_signals += simulated_signal * weight
                total_weight += weight
                
            except Exception as e:
                engine_results[name] = {
                    'error': str(e),
                    'weight': weight,
                    'type': engine.legend_type.value,
                    'reliability': engine.reliability_level.value
                }
        
        # Calculate consensus
        consensus_signal = None
        confidence = 0.0
        
        if total_weight > 0:
            consensus_score = weighted_signals / total_weight
            confidence = min(abs(consensus_score) * 0.3, 1.0)  # Simple confidence calculation
            
            if abs(consensus_score) > 0.3:
                consensus_signal = 'bullish' if consensus_score > 0 else 'bearish'
        
        return {
            'consensus_signal': consensus_signal,
            'confidence': confidence,
            'consensus_score': weighted_signals / total_weight if total_weight > 0 else 0,
            'qualified_engines': len(qualified_engines),
            'total_weight': total_weight,
            'engine_results': engine_results,
            'note': 'Demonstration version with simulated signals'
        }
