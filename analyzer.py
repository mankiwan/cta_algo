import numpy as np
import pandas as pd

class Analyzer:
    """
    Analyzes backtest results and computes performance metrics.
    """
    def __init__(self):
        pass

    def evaluate(self, df):
        """
        Calculate Sharpe ratio, Calmar ratio, max drawdown, annualized return, etc.
        Returns a dictionary of metrics.
        """
        metrics = {}
        df['returns'] = df['equity'].pct_change().fillna(0)
        metrics['Total Return'] = f"{(df['equity'].iloc[-1] / df['equity'].iloc[0] - 1) * 100:.2f}%"
        metrics['Annualized Return'] = f"{(df['returns'].mean() * 365):.2%}"
        metrics['Annualized Volatility'] = f"{(df['returns'].std() * np.sqrt(365)):.2%}"
        sharpe = (df['returns'].mean() / df['returns'].std()) * np.sqrt(365) if df['returns'].std() > 0 else 0
        metrics['Sharpe Ratio'] = f"{sharpe:.2f}"
        # Max Drawdown
        cummax = df['equity'].cummax()
        drawdown = (df['equity'] - cummax) / cummax
        metrics['Max Drawdown'] = f"{drawdown.min() * 100:.2f}%"
        # Calmar Ratio
        calmar = (df['returns'].mean() * 365) / abs(drawdown.min()) if drawdown.min() < 0 else 0
        metrics['Calmar Ratio'] = f"{calmar:.2f}"
        return metrics 