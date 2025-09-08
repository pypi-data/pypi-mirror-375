# Pantheon Legends

A Python implementation of the Pantheon Legends model for financial market analysis, converted from C# contracts to idiomatic Python using dataclasses and type hints.

## Overview

Pantheon Legends provides a framework for implementing and orchestrating multiple financial analysis "legends" (methodologies) such as Dow Theory, Wyckoff Method, Elliott Wave, etc. Each legend engine analyzes market data according to its specific methodology and returns structured results.

## Features

- **Async/Await Support**: All analysis operations are asynchronous for better performance
- **Type Safety**: Full type hints using Python's typing system
- **Progress Reporting**: Real-time progress updates during analysis
- **Quality Metadata**: Comprehensive data quality metrics for each analysis
- **Extensible Design**: Easy to add new legend engines
- **Orchestration**: Run multiple legend engines concurrently

## Installation

```bash
# Install from PyPI (when published)
pip install pantheon-legends

# Or install from source
git clone https://github.com/SpartanDigitalDotNet/pantheon-legends
cd pantheon-legends
pip install -e .
```

## Quick Start

### Basic Usage

```python
import asyncio
from datetime import datetime
from legends import Pantheon, LegendRequest

async def main():
    # Create Pantheon with default engines
    pantheon = Pantheon.create_default()
    
    # Create an analysis request
    request = LegendRequest(
        symbol="AAPL",
        timeframe="1d", 
        as_of=datetime.now()
    )
    
    # Run all legend engines
    results = await pantheon.run_all_legends_async(request)
    
    # Display results
    for result in results:
        print(f"{result.legend}: {result.facts}")

asyncio.run(main())
```

### Using Individual Engines

```python
import asyncio
from datetime import datetime
from legends import DowLegendEngine, LegendRequest

async def main():
    # Create a specific legend engine
    dow_engine = DowLegendEngine()
    
    request = LegendRequest(
        symbol="MSFT",
        timeframe="4h",
        as_of=datetime.now()
    )
    
    # Run the analysis
    result = await dow_engine.run_async(request)
    
    print(f"Primary Trend: {result.facts['primary_trend']}")
    print(f"Confidence: {result.facts['confidence_score']}")

asyncio.run(main())
```

### Progress Monitoring

```python
import asyncio
from legends import LegendProgress

async def progress_handler(progress: LegendProgress):
    print(f"[{progress.legend}] {progress.stage}: {progress.percent:.1f}%")

# Use with any engine
result = await engine.run_async(request, progress_handler)
```

## Core Components

### Data Models

- **`LegendRequest`**: Analysis request with symbol, timeframe, and timestamp
- **`LegendProgress`**: Progress updates during analysis execution  
- **`LegendEnvelope`**: Complete analysis results with metadata
- **`QualityMeta`**: Data quality metrics (sample size, freshness, completeness)

### Engines

- **`DowLegendEngine`**: Dow Theory-based analysis
- **`WyckoffLegendEngine`**: Wyckoff Method analysis
- **Custom Engines**: Implement `ILegendEngine` protocol

### Orchestration

- **`Pantheon`**: Manages multiple engines and provides unified interface
- **Progress Callbacks**: Real-time progress reporting
- **Concurrent Execution**: Run multiple engines simultaneously

## Creating Custom Legend Engines

```python
from legends.contracts import ILegendEngine, LegendRequest, LegendEnvelope

class MyCustomLegend:
    @property
    def name(self) -> str:
        return "MyLegend"
    
    async def run_async(self, request: LegendRequest, progress_callback=None):
        # Your analysis logic here
        facts = {"signal": "bullish", "strength": 0.85}
        quality = QualityMeta(100.0, 30.0, 1.0)
        
        return LegendEnvelope(
            legend=self.name,
            at=request.as_of, 
            tf=request.timeframe,
            facts=facts,
            quality=quality
        )

# Register with Pantheon
pantheon = Pantheon()
pantheon.register_engine(MyCustomLegend())
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/SpartanDigitalDotNet/pantheon-legends
cd pantheon-legends

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black legends/
isort legends/
```

### Type Checking

```bash
mypy legends/
```

## API Reference

### LegendRequest

```python
@dataclass(frozen=True)
class LegendRequest:
    symbol: str          # Financial instrument symbol
    timeframe: str       # Time interval (e.g., "1d", "4h", "1m")
    as_of: datetime      # Analysis timestamp
```

### LegendEnvelope

```python
@dataclass(frozen=True) 
class LegendEnvelope:
    legend: str                    # Engine name
    at: datetime                   # Analysis time
    tf: str                        # Timeframe
    facts: Dict[str, Any]          # Analysis results
    quality: QualityMeta           # Quality metrics
```

### ILegendEngine Protocol

```python
class ILegendEngine(Protocol):
    @property
    def name(self) -> str: ...
    
    async def run_async(
        self,
        request: LegendRequest,
        progress_callback: Optional[ProgressCallback] = None
    ) -> LegendEnvelope: ...
```

## Examples

See `examples.py` for comprehensive usage examples including:

- Single engine execution
- Multi-engine orchestration  
- Custom engine implementation
- Progress monitoring
- Error handling

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Roadmap

- [ ] Additional built-in legend engines
- [ ] Data source integrations
- [ ] Performance optimizations
- [ ] Advanced orchestration features
- [ ] Web API interface
- [ ] Real-time streaming support
