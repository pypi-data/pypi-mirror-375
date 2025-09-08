"""
Pantheon orchestrator for managing multiple legend engines.

This module provides the main Pantheon class that coordinates
multiple legend engines and provides a unified interface.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Set

from .contracts import (
    ILegendEngine,
    LegendRequest,
    LegendProgress,
    LegendEnvelope,
    ProgressCallback
)
from .engines import DowLegendEngine, WyckoffLegendEngine


class Pantheon:
    """
    Main orchestrator for Pantheon Legends analysis.
    
    Pantheon manages multiple legend engines and provides methods to:
    - Register legend engines
    - Run single or multiple legend analyses
    - Aggregate results from multiple engines
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
    
    @property
    def available_engines(self) -> Set[str]:
        """Get the names of all registered legend engines."""
        return set(self._engines.keys())
    
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
            Pantheon instance with Dow and Wyckoff engines registered
        """
        pantheon = cls()
        pantheon.register_engine(DowLegendEngine())
        pantheon.register_engine(WyckoffLegendEngine())
        return pantheon
