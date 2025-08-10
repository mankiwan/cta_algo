# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a Bitcoin trading strategy project focused on **Z-Score Mean Reversion strategy** - a simplified long-only approach:

### Core Files:
- **main.py**: Interactive framework entry point with data selection and user preferences
- **strategy.py**: Core strategy class implementing Z-Score signals for long-only mean reversion
- **backtest.py**: Backtesting engine for running simulations and equity curve generation
- **analyzer.py**: Modular metrics calculation with individual functions for each metric
- **optimizer.py**: Parameter optimization engine with grid search and sensitivity analysis
- **plotting.py**: Visualization components for equity curves and optimization heatmaps
- **api.py**: GlassnodeAPI class for fetching Bitcoin price data from external API
- **draft_backtest.py**: Original standalone implementation (reference)
- **download_data.py**: Standalone data fetching utility

### Strategy Logic (Z-Score Mean Reversion):
- **Z-Score Calculation**: `(price - moving_average) / standard_deviation`
- **Long Entry**: When `z-score > threshold` (price significantly above MA)
- **Position Logic**: `position = 1` if z-score > threshold, else `position = 0`
- **Parameters**: MA window (10-100), Z-Score threshold (0-3.0)
- **Long-Only**: No short positions, either fully invested (1) or cash (0)

### Modular Architecture Flow:
1. **Data**: User selects data source (local CSV or Glassnode API via `api.py`)
2. **Strategy** (`strategy.py`): Calculates Z-Score indicators and generates long-only signals
3. **Backtesting** (`backtest.py`): Simulates trades, calculates PnL and equity curve
4. **Analysis** (`analyzer.py`): Computes individual performance metrics (Sharpe, Calmar, etc.)
5. **Optimization** (`optimizer.py`): Grid search across parameter ranges
6. **Visualization** (`plotting.py`): Charts equity curves and optimization heatmaps

### Component Interactions:
- `Strategy` coordinates `Backtester`, `Analyzer`, `Optimizer`, and `Plotter`
- `Backtester` uses `Analyzer` for metrics calculation
- `Optimizer` uses `Backtester` for proper data preparation and metrics calculation
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

# Original BBand+RSI implementation (reference)
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
- **New Strategies**: Extend `Strategy` class, implement `generate_signals(window, threshold)` method
- **New Metrics**: Add functions to `Analyzer` class following existing patterns
- **New Optimizers**: Extend `Optimizer` class with different search algorithms (ensure they use `Backtester`)
- **New Visualizations**: Add methods to `Plotter` class

### Architecture Improvements Made
- **Eliminated Code Duplication**: `Optimizer` now properly uses `Backtester` instead of duplicating metrics calculation
- **Fixed Look-Ahead Bias**: Removed complex signal processing that could peek at future data
- **Simplified Strategy**: Pure vectorized Z-Score approach with `np.where()` for learning clarity
- **Modular Design**: Clean separation where `Optimizer` delegates to `Backtester` for consistency
- **Enhanced Metrics**: Added 6 additional performance metrics for comprehensive analysis
- **Fixed Drawdown Calculation**: Corrected calculation errors that were showing 0% drawdown

### Performance Metrics Available
- **Core Returns**: Total Return, Annualized Return
- **Risk-Adjusted**: Sharpe Ratio, Sortino Ratio, Calmar Ratio
- **Risk Metrics**: Max Drawdown, Recovery Time, Max Consecutive Losses
- **Trading Efficiency**: Profit Factor, Win Rate, Total Trades
- **Market Exposure**: Time in Market, Average Trade Duration

### Visualization Updates
- **Replaced RSI Chart**: Now shows Z-Score with threshold lines and entry markers
- **Updated Price Chart**: Shows Moving Average with standard deviation bands
- **Enhanced Signals**: Clear long entry/exit markers with position highlighting
- **Improved Labels**: All charts reflect Z-Score strategy instead of Bollinger Bands

## Strategy Analysis & Improvement Recommendations

### Current Strategy Assessment

#### ✅ Strengths
- **Clean Architecture**: Excellent modular design with clear separation of concerns
- **Educational Value**: Simple, understandable logic perfect for learning
- **Comprehensive Metrics**: 13 metrics provide thorough performance analysis
- **Fixed Biases**: Eliminated look-ahead bias and code duplication
- **Vectorized Implementation**: Efficient `np.where()` approach

#### ⚠️ Areas for Improvement

##### 1. Strategy Logic Issues
**Current Problem**: Strategy contradicts typical mean reversion logic
```python
# Current: Buy when price is HIGH above moving average (momentum/breakout)
position = 1 if zscore > threshold else 0  # zscore > 2 = price way above MA
```

**Mean Reversion Should**: Buy when price is LOW (cheap), sell when HIGH
```python
# Typical Mean Reversion: Buy when price is below MA
position = 1 if zscore < -threshold else 0  # zscore < -2 = price way below MA
```

##### 2. Risk Management Gaps
- **No Stop Losses**: Can hold losing positions indefinitely
- **No Position Sizing**: Always uses 100% capital (very risky)
- **No Volatility Adjustment**: Same parameters across all market conditions
- **No Maximum Position Duration**: Could hold for years

##### 3. Market Reality Issues
- **No Transaction Costs**: Real trading has 0.1%+ fees per trade
- **No Slippage**: Market orders don't fill at exact backtest prices
- **No Liquidity Constraints**: Assumes infinite liquidity
- **24/7 Bitcoin Trading**: Overnight gaps not considered

##### 4. Strategy Robustness
- **Over-reliance on Z-Score**: No confirmation signals
- **No Market Regime Detection**: Same logic in bull/bear/sideways markets
- **No Adaptive Parameters**: Fixed window/threshold regardless of volatility

### Improvement Roadmap

#### Priority 1: Fix Strategy Logic
```python
# Option A: True Mean Reversion
position = 1 if zscore < -threshold else 0  # Buy dips

# Option B: Mean Reversion with Exit
if zscore < -threshold:     # Price below MA (oversold)
    position = 1            # Buy
elif zscore > 0.5:          # Price returns to MA  
    position = 0            # Exit
```

#### Priority 2: Add Risk Management
```python
# Add position sizing
capital_per_trade = 0.1  # Risk only 10% per trade
position = position * capital_per_trade

# Add stop loss
if current_loss > 0.05:  # 5% stop loss
    position = 0
```

#### Priority 3: Add Transaction Costs
```python
# In backtest.py
transaction_cost = 0.001  # 0.1% per trade
df['pnl'] = df['position'].shift(1) * df['returns'] - transaction_cost * abs(df['position'].diff())
```

#### Priority 4: Multiple Timeframes
```python
# Add confirmation from longer timeframe
long_term_ma = df['close'].rolling(200).mean()
trend_filter = df['close'] > long_term_ma  # Only trade with long-term trend
position = position * trend_filter
```

#### Priority 5: Regime Detection
```python
# Adjust parameters based on volatility
current_vol = df['returns'].rolling(30).std()
adaptive_threshold = base_threshold * (current_vol / historical_avg_vol)
```

### Implementation Timeline
- **Week 1**: Fix mean reversion logic (buy dips, not breakouts)
- **Week 2**: Add transaction costs and position sizing
- **Week 3**: Implement stop losses and maximum holding periods
- **Week 4**: Add trend filter and volatility adjustment

### Learning Recommendations
1. **Keep current version** for educational comparison
2. **Create `strategy_v2.py`** with improvements
3. **Compare performance** between versions
4. **Gradually add complexity** while maintaining clean code

**Note**: Current framework is excellent for learning fundamentals. The main issues are strategy logic (momentum vs mean reversion) and missing risk management components.

### Component APIs
- **Strategy**: `backtest(window, threshold)`, `optimize(window, threshold)`
- **Analyzer**: Individual metric functions + `calculate_all_metrics(df)`
- **Optimizer**: `optimize_parameters(param_ranges, metric)` (uses Backtester internally)
- **Plotter**: `plot_equity_curve(df)`, `plot_optimization_heatmap(results_df)`
- **Backtester**: `run_backtest(df, silent=False)`, `calculate_metrics(df)`