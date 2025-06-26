# CTA Bitcoin Strategy

A modular CTA (Commodity Trading Advisor) strategy framework for Bitcoin, supporting both momentum and mean reversion models. Data is fetched from Glassnode API or local CSV, and the framework includes backtesting, analysis, and plotting modules.

## Project Structure

- `main.py`: Main entry point to run the strategy
- `strategy.py`: Contains momentum and mean reversion models (e.g., Supertrend+RSI, Bollinger Bands)
- `api.py`: Fetches data from Glassnode API and saves to CSV
- `analyzer.py`: Analyzes backtest results (Sharpe, Calmar, drawdown, annual return, etc.)
- `backtest.py`: Backtesting logic (positions, PnL, equity)
- `plotting.py`: Plots equity curve and performance metrics
- `requirements.txt`: Required Python packages
- `test_data.csv`: Example data for offline testing

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

- If `test_data.csv` exists, it will use that for backtesting.
- If not, it will fetch data from Glassnode using your API key and save it as `test_data.csv`.

### 6. Deactivate the virtual environment (when done)
```bash
deactivate
```