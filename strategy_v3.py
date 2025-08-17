import pandas as pd
import numpy as np
import ta
from backtest import Backtester
from plotting import Plotter
from optimizer import Optimizer


class Strategy3:
    """RSI Momentum Strategy based on hyperliquid-trading-live-bot.py
    
    Strategy Logic:
    - Long Entry: RSI crosses above 70 (overbought level)
    - Long Exit: RSI crosses below 70
    - Long-only momentum/breakout strategy
    """
    
    def __init__(self, data):
        self.data = data.copy()
        self.backtester = Backtester()
        self.plotter = Plotter()
        self.optimizer = Optimizer(self, self.backtester)
    
    def calculate_rsi(self, prices, window):
        """Calculate RSI using ta library"""
        return ta.momentum.rsi(prices, window=window)
    
    def generate_signals(self, rsi_length=14, rsi_overbought=70):
        """Generate RSI momentum signals
        
        Args:
            rsi_length: RSI calculation period (default: 14)
            rsi_overbought: RSI threshold level (default: 70)
        
        Returns:
            DataFrame with RSI values and position signals
        """
        df = self.data.copy()
        
        # Calculate RSI
        df['rsi'] = self.calculate_rsi(df['close'], rsi_length)
        
        # Initialize position column
        df['position'] = 0
        
        # Generate signals using vectorized approach
        # Long entry: RSI crosses above threshold
        # Long exit: RSI crosses below threshold
        for i in range(1, len(df)):
            current_rsi = df.iloc[i]['rsi']
            previous_rsi = df.iloc[i-1]['rsi']
            previous_position = df.iloc[i-1]['position']
            
            # Long entry condition: RSI crosses above overbought level
            if previous_rsi <= rsi_overbought < current_rsi:
                df.iloc[i, df.columns.get_loc('position')] = 1
            
            # Long exit condition: RSI crosses below overbought level  
            elif previous_rsi >= rsi_overbought > current_rsi:
                df.iloc[i, df.columns.get_loc('position')] = 0
            
            # Hold previous position if no signal
            else:
                df.iloc[i, df.columns.get_loc('position')] = previous_position
        
        return df
    
    def backtest(self, rsi_length=14, rsi_overbought=70):
        """Run backtest with given parameters"""
        print(f"\n=== Backtesting RSI Momentum Strategy ===")
        print(f"Parameters: RSI Length={rsi_length}, RSI Threshold={rsi_overbought}")
        
        # Generate signals
        df_signals = self.generate_signals(rsi_length, rsi_overbought)
        
        # Run backtest using existing Backtester
        results = self.backtester.run_backtest(df_signals)
        
        # Plot results using existing Plotter (adapted for RSI)
        self.plot_rsi_strategy(results)
        
        return results
    
    def optimize(self, rsi_length=(5, 30, 1), rsi_overbought=(60, 85, 2.5), metric='sharpe'):
        """Optimize RSI strategy parameters
        
        Args:
            rsi_length: tuple (start, stop, step) for RSI period
            rsi_overbought: tuple (start, stop, step) for RSI threshold
            metric: optimization target ('sharpe', 'calmar', 'annual_return')
        
        Returns:
            DataFrame with optimization results
        """
        print(f"\n=== Optimizing RSI Strategy Parameters ===")
        print(f"RSI Length range: {rsi_length}")
        print(f"RSI Threshold range: {rsi_overbought}")
        
        param_ranges = {
            'rsi_length': rsi_length,
            'rsi_overbought': rsi_overbought
        }
        
        # Use modified optimizer for RSI parameters
        results_df = self._optimize_rsi_parameters(param_ranges, metric)
        
        # Plot optimization heatmap
        self.plot_rsi_optimization_heatmap(results_df, 'rsi_length', 'rsi_overbought', metric)
        
        return results_df
    
    def _optimize_rsi_parameters(self, param_ranges, metric='sharpe'):
        """Optimize RSI parameters using modified grid search"""
        from itertools import product
        
        # Generate parameter combinations
        param_lists = {}
        for param, param_range in param_ranges.items():
            if isinstance(param_range, tuple) and len(param_range) == 3:
                start, stop, step = param_range
                param_lists[param] = np.arange(start, stop + step, step)
            else:
                param_lists[param] = param_range
        
        param_combinations = []
        for combo in product(*param_lists.values()):
            param_combinations.append(dict(zip(param_lists.keys(), combo)))
        
        print(f"Total combinations to test: {len(param_combinations)}")
        
        results = []
        
        for i, params in enumerate(param_combinations):
            if (i + 1) % 10 == 0 or i == 0:
                print(f"Progress: {i + 1}/{len(param_combinations)}")
            
            try:
                # Generate signals with current parameters
                df_signals = self.generate_signals(
                    rsi_length=int(params['rsi_length']),
                    rsi_overbought=params['rsi_overbought']
                )
                
                # Run backtest using Backtester
                df_backtest = self.backtester.run_backtest(df_signals, silent=True)
                
                # Extract metrics
                metrics = self.backtester.calculate_metrics(df_backtest)
                
                # Store results
                result = {
                    'rsi_length': int(params['rsi_length']),
                    'rsi_overbought': params['rsi_overbought'],
                    **metrics
                }
                results.append(result)
                
            except Exception as e:
                print(f"Error with params {params}: {e}")
                continue
        
        # Convert to DataFrame and sort
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(metric, ascending=False)
        
        # Print top results
        print(f"\nTop 10 parameter combinations by {metric}:")
        display_cols = ['rsi_length', 'rsi_overbought', 'sharpe', 'sortino', 'annual_return', 'max_drawdown', 'calmar', 'profit_factor']
        available_cols = [col for col in display_cols if col in results_df.columns]
        print(results_df[available_cols].head(10).to_string(index=False))
        
        return results_df
    
    def plot_rsi_strategy(self, df):
        """Plot RSI strategy results using modified Plotter"""
        import matplotlib.pyplot as plt
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Price with RSI signals
        ax1.plot(df['timestamp'], df['close'], label='Price', color='black', linewidth=1.5)
        
        # Mark long entry/exit signals
        long_entries = df[(df['position'] == 1) & (df['position'].shift(1) != 1)]
        long_exits = df[(df['position'] == 0) & (df['position'].shift(1) == 1)]
        
        ax1.scatter(long_entries['timestamp'], long_entries['close'], 
                   color='green', marker='^', s=60, label='Long Entry', zorder=5)
        ax1.scatter(long_exits['timestamp'], long_exits['close'], 
                   color='red', marker='v', s=60, label='Long Exit', zorder=5)
        
        # Highlight periods when long
        long_periods = df[df['position'] == 1]
        if len(long_periods) > 0:
            ax1.fill_between(df['timestamp'], df['close'].min(), df['close'].max(),
                           where=(df['position'] == 1), alpha=0.05, color='green',
                           label='Long Position Periods')
        
        ax1.set_title('Price with RSI Momentum Strategy Signals')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. RSI with threshold
        ax2.plot(df['timestamp'], df['rsi'], color='purple', linewidth=1, label='RSI')
        ax2.axhline(y=70, color='red', linestyle='--', alpha=0.8, label='Overbought (70)')
        ax2.axhline(y=30, color='green', linestyle='--', alpha=0.8, label='Oversold (30)')
        ax2.axhline(y=50, color='black', linestyle='-', alpha=0.5, label='Neutral (50)')
        
        # Highlight overbought zone
        ax2.fill_between(df['timestamp'], 70, 100, alpha=0.1, color='red', label='Overbought Zone')
        ax2.fill_between(df['timestamp'], 0, 30, alpha=0.1, color='green', label='Oversold Zone')
        
        # Mark actual entry points
        entry_points = df[df['position'] == 1]
        if len(entry_points) > 0:
            ax2.scatter(entry_points['timestamp'], entry_points['rsi'], 
                      color='orange', marker='o', s=30, alpha=0.8, 
                      label='Long Positions', zorder=5)
        
        ax2.set_title('RSI with Entry/Exit Levels')
        ax2.set_ylabel('RSI')
        ax2.set_ylim(0, 100)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Equity Curve
        ax3.plot(df['timestamp'], df['equity_curve'], color='blue', linewidth=2, label='RSI Strategy')
        ax3.plot(df['timestamp'], (df['close'] / df['close'].iloc[0]), color='gray', alpha=0.7, label='Buy & Hold')
        ax3.set_title('Equity Curve Comparison')
        ax3.set_ylabel('Cumulative Return')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Drawdown
        ax4.fill_between(df['timestamp'], df['drawdown'] * 100, 0, color='red', alpha=0.3)
        ax4.plot(df['timestamp'], df['drawdown'] * 100, color='red', linewidth=1)
        ax4.set_title('Drawdown')
        ax4.set_ylabel('Drawdown (%)')
        ax4.set_xlabel('Date')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_rsi_optimization_heatmap(self, results_df, x_col, y_col, value_col):
        """Plot RSI optimization results as heatmap"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Create pivot table for heatmap
        pivot_data = results_df.pivot(index=y_col, columns=x_col, values=value_col)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='RdYlGn', center=0)
        plt.title(f'RSI Strategy Optimization: {value_col.title()} by Parameters')
        plt.xlabel(f'{x_col.title().replace("_", " ")}')
        plt.ylabel(f'{y_col.title().replace("_", " ")}')
        plt.show()
        
        # Additional summary plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Best parameters by target metric
        top_10 = results_df.head(10)
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top_10)))
        
        bars = ax1.bar(range(len(top_10)), top_10[value_col], color=colors)
        ax1.set_title(f'Top 10 Parameter Combinations (by {value_col.title()})')
        ax1.set_xlabel('Rank')
        ax1.set_ylabel(value_col.title())
        ax1.grid(True, alpha=0.3)
        
        # Add parameter labels
        for i, (idx, row) in enumerate(top_10.iterrows()):
            ax1.text(i, row[value_col] + 0.01, f'L:{int(row["rsi_length"])}\nT:{row["rsi_overbought"]:.1f}', 
                    ha='center', va='bottom', fontsize=8)
        
        # Correlation between RSI length and performance
        ax2.scatter(results_df['rsi_length'], results_df[value_col], alpha=0.6, label=f'RSI Length vs {value_col.title()}')
        ax2.set_xlabel('RSI Length')
        ax2.set_ylabel(value_col.title())
        ax2.set_title(f'RSI Length vs Performance')
        ax2.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(results_df['rsi_length'], results_df[value_col], 1)
        p = np.poly1d(z)
        ax2.plot(results_df['rsi_length'], p(results_df['rsi_length']), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.show()