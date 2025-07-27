import pandas as pd
import numpy as np
from backtest import Backtester
from plotting import Plotter
from optimizer import Optimizer


class Strategy:
    def __init__(self, data):
        self.data = data.copy()
        self.backtester = Backtester()
        self.plotter = Plotter()
        self.optimizer = Optimizer(self, self.backtester)
    
    def calculate_zscore(self, prices, window):
        """Calculate z-score: (price - moving_average) / standard_deviation"""
        ma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        zscore = (prices - ma) / std
        return zscore, ma
    
    def calculate_bollinger_bands(self, prices, window, multiplier):
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        upper = ma + (multiplier * std)
        lower = ma - (multiplier * std)
        return ma, upper, lower
    
    def generate_signals(self, window, threshold):
        """Generate simple long-only z-score signals"""
        df = self.data.copy()
        
        # Calculate z-score
        df['zscore'], df['ma'] = self.calculate_zscore(df['close'], window)
        
        # Simple vectorized position logic: 1 if zscore > threshold, else 0
        df['position'] = np.where(df['zscore'] > threshold, 1, 0)
        
        return df
    
    def backtest(self, window=20, threshold=2.0):
        """Run backtest with given parameters"""
        print(f"\n=== Backtesting Long-Only Z-Score Strategy ===")
        print(f"Parameters: MA Window={window}, Z-Score Threshold={threshold}")
        
        # Generate signals
        df_signals = self.generate_signals(window, threshold)
        
        # Run backtest
        results = self.backtester.run_backtest(df_signals)
        
        # Plot results
        self.plotter.plot_equity_curve(results)
        
        return results
    
    def optimize(self, window=(10, 60, 5), threshold=(1.0, 3.0, 0.25), metric='sharpe'):
        """Optimize strategy parameters using the Optimizer class"""
        param_ranges = {
            'window': window,
            'threshold': threshold
        }
        
        # Run optimization
        results_df = self.optimizer.optimize_parameters(param_ranges, metric)
        
        # Plot optimization heatmap
        self.plotter.plot_optimization_heatmap(results_df, 'window', 'threshold', metric)
        
        return results_df