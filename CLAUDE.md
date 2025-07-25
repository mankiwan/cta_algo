# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a Bitcoin trading strategy project focused on **Bollinger Bands + RSI strategy** with two main implementations:

### Core Files:
- **main.py**: Interactive framework entry point with data selection and user preferences
- **strategy.py**: Core strategy class implementing BBand+RSI signals and coordination
- **backtest.py**: Backtesting engine for running simulations and equity curve generation
- **analyzer.py**: Modular metrics calculation with individual functions for each metric
- **optimizer.py**: Parameter optimization engine with grid search and sensitivity analysis
- **plotting.py**: Visualization components for equity curves and optimization heatmaps
- **api.py**: GlassnodeAPI class for fetching Bitcoin price data from external API
- **draft_backtest.py**: Original standalone implementation (reference)
- **download_data.py**: Standalone data fetching utility

### Strategy Logic (BBand + RSI):
- **Long Signal**: Price touches lower Bollinger Band AND RSI < 30 (oversold)
- **Short Signal**: Price touches upper Bollinger Band AND RSI > 70 (overbought)  
- **Exit**: Price returns to middle Bollinger Band (moving average)
- **Parameters**: BB window (10-60), BB standard deviation multiplier (1.0-3.5), RSI fixed at 14 periods

### Modular Architecture Flow:
1. **Data**: User selects data source (local CSV or Glassnode API via `api.py`)
2. **Strategy** (`strategy.py`): Calculates BBand+RSI indicators and generates signals
3. **Backtesting** (`backtest.py`): Simulates trades, calculates PnL and equity curve
4. **Analysis** (`analyzer.py`): Computes individual performance metrics (Sharpe, Calmar, etc.)
5. **Optimization** (`optimizer.py`): Grid search across parameter ranges
6. **Visualization** (`plotting.py`): Charts equity curves and optimization heatmaps

### Component Interactions:
- `Strategy` coordinates `Backtester`, `Analyzer`, `Optimizer`, and `Plotter`
- `Backtester` uses `Analyzer` for metrics calculation
- `Optimizer` uses `Analyzer` for parameter evaluation
- All components are loosely coupled and individually testable

## Common Commands

### Setup and Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Interactive modular framework (recommended)
python main.py

# Standalone BBand+RSI optimization (reference implementation)
python draft_backtest.py

# Standalone data download utility
python download_data.py
```

### Environment Configuration
Create `.env` file with:
```
GLASSNODE_APIKEY=your_api_key_here
```

### Data Management
- Historical data stored in `data/` directory with format: `btc_{interval}_{start_date}_{end_date}.csv`
- Supported intervals: 10m, 1h, 24h
- Data range: 2010-07-17 to 2025-07-22

## Development Notes

### Modular Design Principles
- **Single Responsibility**: Each class handles one specific concern
- **Loose Coupling**: Components interact through well-defined interfaces
- **Reusability**: Individual functions can be used independently
- **Testability**: Each component can be tested in isolation

### Key Design Patterns
- **Strategy Pattern**: `Strategy` class coordinates different components
- **Composition**: `Strategy` uses `Backtester`, `Analyzer`, `Optimizer`, `Plotter`
- **Template Method**: `Analyzer` provides individual metric functions that can be combined

### Extending the Framework
- **New Strategies**: Extend `Strategy` class, implement `generate_signals()` method
- **New Metrics**: Add functions to `Analyzer` class following existing patterns
- **New Optimizers**: Extend `Optimizer` class with different search algorithms
- **New Visualizations**: Add methods to `Plotter` class

### Component APIs
- **Strategy**: `backtest(long_short, window, threshold)`, `optimize(window, threshold)`
- **Analyzer**: Individual metric functions + `calculate_all_metrics(df)`
- **Optimizer**: `optimize_parameters(param_ranges, metric, mode)`
- **Plotter**: `plot_equity_curve(df)`, `plot_optimization_heatmap(results_df)`