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
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices, window, multiplier):
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        upper = ma + (multiplier * std)
        lower = ma - (multiplier * std)
        return ma, upper, lower
    
    def generate_signals(self, window, threshold, long_short="long short"):
        """Generate BBand+RSI trading signals"""
        df = self.data.copy()
        
        # Calculate indicators
        df['bb_ma'], df['bb_upper'], df['bb_lower'] = self.calculate_bollinger_bands(
            df['close'], window, threshold
        )
        df['rsi'] = self.calculate_rsi(df['close'], 14)
        
        # Initialize positions
        df['position'] = 0
        
        # Trading signals based on draft_backtest.py logic
        if long_short in ["long", "long short"]:
            # Long signal: price touches lower band AND RSI < 30
            long_condition = (df['close'] <= df['bb_lower']) & (df['rsi'] < 30)
            df.loc[long_condition, 'position'] = 1
            
            # Exit long when price returns to middle band
            exit_long = (df['close'] >= df['bb_ma']) & (df['position'].shift(1) == 1)
            df.loc[exit_long, 'position'] = 0
        
        if long_short in ["short", "long short"]:
            # Short signal: price touches upper band AND RSI > 70
            short_condition = (df['close'] >= df['bb_upper']) & (df['rsi'] > 70)
            df.loc[short_condition, 'position'] = -1
            
            # Exit short when price returns to middle band
            exit_short = (df['close'] <= df['bb_ma']) & (df['position'].shift(1) == -1)
            df.loc[exit_short, 'position'] = 0
        
        # Forward fill positions (hold until exit signal)
        df['position'] = df['position'].replace(0, np.nan).fillna(method='ffill').fillna(0)
        
        return df
    
    def backtest(self, long_short="long short", window=20, threshold=2.0):
        """Run backtest with given parameters"""
        print(f"\n=== Backtesting BBand+RSI Strategy ===")
        print(f"Parameters: BB Window={window}, BB Multiplier={threshold}, Mode={long_short}")
        
        # Generate signals
        df_signals = self.generate_signals(window, threshold, long_short)
        
        # Run backtest
        results = self.backtester.run_backtest(df_signals)
        
        # Plot results
        self.plotter.plot_equity_curve(results)
        
        return results
    
    def optimize(self, window=(10, 60, 5), threshold=(1.0, 3.5, 0.25), metric='sharpe'):
        """Optimize strategy parameters using the Optimizer class"""
        param_ranges = {
            'window': window,
            'threshold': threshold
        }
        
        # Run optimization
        results_df = self.optimizer.optimize_parameters(param_ranges, metric, 'long short')
        
        # Plot optimization heatmap
        self.plotter.plot_optimization_heatmap(results_df, 'window', 'threshold', metric)
        
        return results_df