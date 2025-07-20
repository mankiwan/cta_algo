# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modular CTA (Commodity Trading Advisor) strategy framework for Bitcoin trading. The system fetches data from the Glassnode API, generates trading signals using momentum and mean reversion strategies, performs backtesting, and provides performance analysis with visualization.

## Core Components

- **main.py**: Entry point that orchestrates the entire workflow (data loading, signal generation, backtesting, analysis, plotting)
- **strategy.py**: Contains the `Strategy` class with technical indicators (Supertrend, RSI, Bollinger Bands) and signal generation logic
- **api.py**: `GlassnodeAPI` class for fetching Bitcoin price data from Glassnode API
- **backtest.py**: `Backtester` class that simulates trading with position management and equity tracking
- **analyzer.py**: `Analyzer` class that computes performance metrics (Sharpe, Calmar, drawdown, returns)
- **plotting.py**: `Plotter` class for visualizing equity curves and performance results
- **test_data.csv**: Sample/cached data file for offline testing

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run the main strategy
python main.py
```

### Environment Configuration
Create a `.env` file in the project root with:
```
GLASSNODE_APIKEY=your_actual_api_key
```

## Data Flow Architecture

1. **Data Loading**: Checks for `test_data.csv` first, falls back to Glassnode API if not found
2. **Signal Generation**: Applies technical indicators (Supertrend, RSI, Bollinger Bands) to generate buy/sell/hold signals
3. **Backtesting**: Simulates trading positions and tracks equity changes based on signals
4. **Analysis**: Computes risk-adjusted performance metrics
5. **Visualization**: Plots equity curve and displays performance statistics

## Key Technical Details

- The strategy combines momentum (Supertrend + RSI) and mean reversion (Bollinger Bands) approaches
- Backtesting uses simple position tracking (1=long, -1=short, 0=flat) 
- Performance metrics include Sharpe ratio, Calmar ratio, max drawdown, and annualized returns
- Data is timestamped and merged between components using pandas DataFrames
- The Supertrend indicator implementation is currently a placeholder (returns dummy value of 1)

## Dependencies

Core packages: numpy, pandas, matplotlib, yfinance, scipy, requests, python-dotenv