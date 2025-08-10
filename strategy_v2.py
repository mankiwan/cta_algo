import pandas as pd
import numpy as np
from backtest import Backtester
from plotting import Plotter
from optimizer import Optimizer


class StrategyV2:
    """
    Advanced Z-Score Mean Reversion Strategy (Version 2)
    
    Key Improvements over v1:
    1. Fixed mean reversion logic (buy dips, not breakouts)
    2. Added transaction costs
    3. Added basic position sizing
    4. Added trend filter for market regime awareness
    
    Educational Focus: Gradual improvements while maintaining clean code
    """
    
    def __init__(self, data, transaction_cost=0.001, position_size=0.25):
        self.data = data.copy()
        self.transaction_cost = transaction_cost  # 0.1% per trade
        self.position_size = position_size        # Risk 25% of capital per trade
        self.backtester = Backtester()
        self.plotter = Plotter()
        self.optimizer = Optimizer(self, self.backtester)
    
    def calculate_zscore(self, prices, window):
        """Calculate z-score: (price - moving_average) / standard_deviation"""
        ma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        zscore = (prices - ma) / std
        return zscore, ma
    
    def calculate_trend_filter(self, prices, trend_window=200):
        """Calculate long-term trend filter"""
        long_term_ma = prices.rolling(trend_window).mean()
        trend_up = prices > long_term_ma
        return trend_up, long_term_ma
    
    def generate_signals(self, window, threshold, use_trend_filter=True):
        """Generate improved mean reversion signals"""
        df = self.data.copy()
        
        # Calculate z-score and moving average
        df['zscore'], df['ma'] = self.calculate_zscore(df['close'], window)
        
        # Calculate trend filter (optional)
        if use_trend_filter:
            df['trend_up'], df['long_term_ma'] = self.calculate_trend_filter(df['close'])
        else:
            df['trend_up'] = True  # Always allow trades
            df['long_term_ma'] = df['ma']  # Use short-term MA as placeholder
        
        # FIXED LOGIC: True mean reversion
        # Buy when price is BELOW moving average (oversold condition)
        # Only trade in the direction of the long-term trend
        long_signal = (df['zscore'] < -threshold) & df['trend_up']  # Buy dips in uptrend
        
        # Apply position sizing
        df['position'] = np.where(long_signal, self.position_size, 0.0)
        
        return df
    
    def calculate_transaction_costs(self, df):
        """Calculate realistic transaction costs"""
        # Position changes trigger transactions
        position_changes = df['position'].diff().abs().fillna(0)
        transaction_costs = position_changes * self.transaction_cost
        return transaction_costs
    
    def backtest(self, window=20, threshold=2.0, use_trend_filter=True):
        """Run backtest with given parameters"""
        print(f"\n=== Backtesting Advanced Z-Score Strategy V2 ===")
        print(f"Parameters: MA Window={window}, Z-Score Threshold={threshold}")
        print(f"Transaction Cost: {self.transaction_cost*100:.2f}% per trade")
        print(f"Position Size: {self.position_size*100:.0f}% of capital")
        print(f"Trend Filter: {'Enabled' if use_trend_filter else 'Disabled'}")
        
        # Generate signals
        df_signals = self.generate_signals(window, threshold, use_trend_filter)
        
        # Add transaction costs to the backtest
        df_signals['transaction_costs'] = self.calculate_transaction_costs(df_signals)
        
        # Run backtest with custom transaction cost handling
        results = self._run_backtest_with_costs(df_signals)
        
        # Plot results
        self.plotter.plot_equity_curve(results)
        
        return results
    
    def _run_backtest_with_costs(self, df):
        """Run backtest with transaction costs included"""
        df_test = df.copy()
        
        # Calculate returns
        df_test['returns'] = df_test['close'].pct_change().fillna(0)
        
        # Calculate PnL with transaction costs
        gross_pnl = df_test['position'].shift(1) * df_test['returns']
        net_pnl = gross_pnl - df_test['transaction_costs']
        df_test['pnl'] = net_pnl
        
        # Calculate cumulative performance
        df_test['cumulative_pnl'] = df_test['pnl'].cumsum()
        df_test['equity_curve'] = (1 + df_test['pnl']).cumprod()
        
        # Calculate drawdown
        df_test['running_max'] = df_test['equity_curve'].cummax()
        df_test['drawdown'] = (df_test['equity_curve'] - df_test['running_max']) / df_test['running_max']
        
        # Calculate metrics using Analyzer
        metrics = self.backtester.calculate_metrics(df_test)
        
        # Print enhanced results
        self._print_v2_results(metrics, df_test)
        
        return df_test
    
    def _print_v2_results(self, metrics, df):
        """Print enhanced backtest results with V2 improvements"""
        print(f"\n=== Advanced Strategy Results (V2) ===")
        print(f"Total Return: {metrics['total_return']:.2f}%")
        print(f"Annualized Return: {metrics['annual_return']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe']:.3f}")
        print(f"Sortino Ratio: {metrics['sortino']:.3f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"Calmar Ratio: {metrics['calmar']:.3f}")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        
        # Enhanced trading statistics
        print(f"\n=== Trading Statistics ===")
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print(f"Time in Market: {metrics['time_in_market']:.1f}%")
        print(f"Avg Trade Duration: {metrics['avg_trade_duration']:.1f} days")
        
        # V2 specific metrics
        total_transaction_costs = df['transaction_costs'].sum() * 100
        print(f"Total Transaction Costs: {total_transaction_costs:.2f}%")
        
        trend_periods = (df['trend_up'] == True).sum() / len(df) * 100
        print(f"Uptrend Periods: {trend_periods:.1f}% of time")
        
        print(f"\n=== Strategy Logic ===")
        print(f"Logic: Buy when z-score < -{metrics.get('threshold', 'N/A')} (price below MA)")
        print(f"Risk Management: {self.position_size*100:.0f}% position sizing + transaction costs")
        
        recovery_time = metrics['recovery_time']
        if recovery_time == float('inf'):
            print(f"Recovery Time: Never recovered from max drawdown")
        else:
            print(f"Recovery Time: {recovery_time:.0f} days")
        
        print(f"\n=== Data Period ===")
        print(f"Period: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
        print(f"Total Days: {len(df)}")
    
    def optimize(self, window=(10, 60, 5), threshold=(0.5, 3.0, 0.25), metric='sharpe'):
        """Optimize strategy parameters using the Optimizer class"""
        print(f"\n=== V2 Strategy Parameter Optimization ===")
        param_ranges = {
            'window': window,
            'threshold': threshold
        }
        
        # Run optimization
        results_df = self.optimizer.optimize_parameters(param_ranges, metric)
        
        # Plot optimization heatmap
        self.plotter.plot_optimization_heatmap(results_df, 'window', 'threshold', metric)
        
        return results_df

    def compare_with_v1(self, window=20, threshold=2.0):
        """Compare V2 strategy with V1 logic"""
        print(f"\n=== V1 vs V2 Strategy Comparison ===")
        
        # V1 Logic (momentum/breakout)
        df_v1 = self.data.copy()
        df_v1['zscore'], df_v1['ma'] = self.calculate_zscore(df_v1['close'], window)
        df_v1['position'] = np.where(df_v1['zscore'] > threshold, 1, 0)  # Buy breakouts
        
        # V2 Logic (mean reversion)
        df_v2 = self.generate_signals(window, threshold, use_trend_filter=True)
        
        print(f"V1 (Momentum): Buy when z-score > {threshold} (price ABOVE MA)")
        print(f"V2 (Mean Rev): Buy when z-score < -{threshold} (price BELOW MA)")
        
        v1_trades = (df_v1['position'] == 1).sum()
        v2_trades = (df_v2['position'] > 0).sum()
        
        print(f"V1 Trading Days: {v1_trades} ({v1_trades/len(df_v1)*100:.1f}% time in market)")
        print(f"V2 Trading Days: {v2_trades} ({v2_trades/len(df_v2)*100:.1f}% time in market)")
        
        return df_v1, df_v2