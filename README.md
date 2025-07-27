# Bitcoin Z-Score Mean Reversion Strategy

A simplified educational framework for Bitcoin trading using Z-Score mean reversion. This project demonstrates clean, modular architecture with comprehensive backtesting and analysis capabilities.

## Strategy Overview

**Z-Score Mean Reversion** - A long-only strategy that:
- Calculates z-score: `(price - moving_average) / standard_deviation`
- Enters long positions when `z-score > threshold` (price significantly above MA)
- Stays in cash when `z-score ≤ threshold`
- Simple logic: `position = 1 if zscore > threshold else 0`

## Project Structure

- `main.py`: Interactive framework with data selection and user preferences
- `strategy.py`: Z-Score strategy implementation with signal generation
- `backtest.py`: Backtesting engine with comprehensive metrics calculation
- `analyzer.py`: 13 performance metrics including Sharpe, Sortino, and drawdown analysis
- `optimizer.py`: Parameter optimization with grid search (uses Backtester internally)
- `plotting.py`: Visualization with Z-Score charts and equity curves
- `api.py`: Glassnode API integration for fetching Bitcoin price data
- `download_data.py`: Standalone data fetching utility
- `draft_backtest.py`: Original BBand+RSI implementation (reference)

## Quick Start Guide

### 1. Clone the repository
```bash
git clone <repository-url>
cd cta_algo
```

### 2. Create and activate a virtual environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your Glassnode API key
- Create a file named `.env` in the project root directory:
  ```
  GLASSNODE_APIKEY=your_actual_api_key
  ```
- Make sure `.env` is in your `.gitignore` (already set by default).

### 5. Run the strategy
```bash
python main.py
```

The framework will:
- Prompt you to select data source (local CSV or Glassnode API)
- Allow date range selection for backtesting
- Run optimization across parameter ranges
- Display comprehensive metrics and visualizations

### 6. Example Usage

**Single Backtest:**
```python
# Edit main.py to uncomment backtest section
strategy.backtest(window=40, threshold=1.75)
```

**Parameter Optimization:**
```python
strategy.optimize(
    window=(10, 100, 10),      # MA window: 10, 20, 30, ..., 100
    threshold=(0, 2.5, 0.25)   # Z-Score threshold: 0, 0.25, 0.5, ..., 2.5
)
```

### 7. Deactivate the virtual environment (when done)
```bash
deactivate
```

## Performance Metrics

The framework calculates 13 comprehensive metrics:

**Returns & Risk-Adjusted:**
- Total Return, Annualized Return
- Sharpe Ratio, Sortino Ratio, Calmar Ratio

**Risk Analysis:**
- Max Drawdown, Recovery Time
- Max Consecutive Losses

**Trading Efficiency:**
- Profit Factor, Win Rate, Total Trades
- Time in Market, Average Trade Duration

## Visualization Features

- **Price Chart**: Moving average with standard deviation bands
- **Z-Score Chart**: Threshold lines and position markers
- **Equity Curve**: Strategy vs buy-and-hold comparison
- **Drawdown Chart**: Portfolio risk visualization
- **Optimization Heatmap**: Parameter performance analysis

## Educational Focus

This project emphasizes:
- ✅ Clean, readable code for learning
- ✅ Modular architecture (easy to extend)
- ✅ Comprehensive documentation
- ✅ Fixed common backtesting biases
- ✅ Simple vectorized strategy logic