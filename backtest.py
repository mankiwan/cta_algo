import pandas as pd
import numpy as np
from analyzer import Analyzer


class Backtester:
    def __init__(self):
        self.analyzer = Analyzer()
    
    def run_backtest(self, df, silent=False):
        """Run backtest and return results with equity curve"""
        df_test = df.copy()
        
        # Calculate returns
        df_test['returns'] = df_test['close'].pct_change().fillna(0)
        
        # Calculate PnL
        df_test['pnl'] = df_test['position'].shift(1) * df_test['returns']
        df_test['cumulative_pnl'] = df_test['pnl'].cumsum()
        df_test['equity_curve'] = (1 + df_test['pnl']).cumprod()
        
        # Calculate drawdown
        df_test['running_max'] = df_test['equity_curve'].cummax()
        df_test['drawdown'] = (df_test['equity_curve'] - df_test['running_max']) / df_test['running_max']
        
        # Calculate metrics using Analyzer
        metrics = self.analyzer.calculate_all_metrics(df_test)
        
        # Print results only if not silent
        if not silent:
            self._print_results(metrics, df_test)
        
        return df_test
    
    def calculate_metrics(self, df):
        """Calculate performance metrics using Analyzer (for backward compatibility)"""
        return self.analyzer.calculate_all_metrics(df)
    
    def _print_results(self, metrics, df):
        """Print backtest results"""
        print(f"\n=== Backtest Results ===")
        print(f"Total Return: {metrics['total_return']:.2f}%")
        print(f"Annualized Return: {metrics['annual_return']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe']:.3f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"Calmar Ratio: {metrics['calmar']:.3f}")
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print(f"Data Period: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
        print(f"Total Days: {len(df)}")