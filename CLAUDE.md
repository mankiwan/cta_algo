# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modular CTA (Commodity Trading Advisor) strategy backtest framework for Bitcoin trading. The system fetches historical Bitcoin price data from the Glassnode API, generates trading signals using momentum and mean reversion strategies, performs backtesting, and provides performance analysis with visualization. This is a research-focused project for strategy development, not for live trading.

## Core Components

- **download_data.py**: Standalone script for downloading Bitcoin price data from Glassnode API with flexible parameters
- **api.py**: `GlassnodeAPI` class for fetching Bitcoin price data with support for multiple timeframes and date ranges
- **main.py**: Entry point that orchestrates the backtest workflow (data loading, signal generation, backtesting, analysis, plotting)
- **strategy.py**: Contains the `Strategy` class with technical indicators (Supertrend, RSI, Bollinger Bands) and signal generation logic
- **backtest.py**: `Backtester` class that simulates trading with position management and equity tracking
- **analyzer.py**: `Analyzer` class that computes performance metrics (Sharpe, Calmar, drawdown, returns)
- **plotting.py**: `Plotter` class for visualizing equity curves and performance results

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

### Data Download (Primary Workflow)
```bash
# Download data with specific date range (required parameters)
python download_data.py 2024-01-01 2024-06-01              # 1h data, JSON API format
python download_data.py 2024-01-01 2024-01-31 10m          # 10m data, JSON API format
python download_data.py 2024-01-01 2024-12-31 24h csv      # Daily data, CSV API format

# Available intervals: 10m, 1h, 24h, 1w, 1month
# Available API formats: json, csv (output is always CSV file)
```

### Running Backtest
```bash
# Run backtest with downloaded data
python main.py
```

### Environment Configuration
Create a `.env` file in the project root with:
```
GLASSNODE_APIKEY=your_actual_api_key
```

## Data Flow Architecture

1. **Data Download**: Use `download_data.py` to fetch Bitcoin price data from Glassnode API with custom date ranges and intervals
2. **Data Storage**: Data is saved as CSV files with descriptive names (e.g., `btc_1h_2024-01-01_2024-06-01.csv`)
3. **Data Loading**: `main.py` loads data from CSV files for backtesting
4. **Signal Generation**: Applies technical indicators (Supertrend, RSI, Bollinger Bands) to generate buy/sell/hold signals
5. **Backtesting**: Simulates trading positions and tracks equity changes based on signals
6. **Analysis**: Computes risk-adjusted performance metrics
7. **Visualization**: Plots equity curve and displays performance statistics

## Glassnode API Integration

- **Endpoint**: `/v1/metrics/market/price_usd_close`
- **Supported Intervals**: 10m, 1h, 24h, 1w, 1month
- **Required Parameters**: start_time (s), end_time (u) as unix timestamps
- **Optional Parameters**: interval (i), format (f: json/csv)
- **Authentication**: API key via query parameter

## Key Technical Details

- The strategy combines momentum (Supertrend + RSI) and mean reversion (Bollinger Bands) approaches
- Backtesting uses simple position tracking (1=long, -1=short, 0=flat) 
- Performance metrics include Sharpe ratio, Calmar ratio, max drawdown, and annualized returns
- Data is timestamped and merged between components using pandas DataFrames
- The Supertrend indicator implementation is currently a placeholder (returns dummy value of 1)
- CSV files are named descriptively with format: `btc_{interval}_{start_date}_{end_date}.csv`

## Dependencies

Core packages: numpy, pandas, matplotlib, yfinance, scipy, requests, python-dotenv