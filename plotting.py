import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class Plotter:
    def __init__(self):
        plt.style.use('default')
    
    def plot_equity_curve(self, df):
        """Plot equity curve and key indicators"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Price with Bollinger Bands and signals
        ax1.plot(df['timestamp'], df['close'], label='Price', color='black', linewidth=1)
        if 'bb_upper' in df.columns:
            ax1.plot(df['timestamp'], df['bb_upper'], label='BB Upper', color='red', alpha=0.7)
            ax1.plot(df['timestamp'], df['bb_ma'], label='BB Middle', color='blue', alpha=0.7)
            ax1.plot(df['timestamp'], df['bb_lower'], label='BB Lower', color='green', alpha=0.7)
            ax1.fill_between(df['timestamp'], df['bb_upper'], df['bb_lower'], alpha=0.1, color='gray')
        
        # Mark buy/sell signals
        buy_signals = df[df['position'] > df['position'].shift(1)]
        sell_signals = df[df['position'] < df['position'].shift(1)]
        ax1.scatter(buy_signals['timestamp'], buy_signals['close'], color='green', marker='^', s=50, label='Buy')
        ax1.scatter(sell_signals['timestamp'], sell_signals['close'], color='red', marker='v', s=50, label='Sell')
        
        ax1.set_title('Price with Bollinger Bands & Signals')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. RSI
        if 'rsi' in df.columns:
            ax2.plot(df['timestamp'], df['rsi'], color='purple', linewidth=1)
            ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
            ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
            ax2.fill_between(df['timestamp'], 70, 100, alpha=0.1, color='red')
            ax2.fill_between(df['timestamp'], 0, 30, alpha=0.1, color='green')
            ax2.set_title('RSI Indicator')
            ax2.set_ylabel('RSI')
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # 3. Equity Curve
        ax3.plot(df['timestamp'], df['equity_curve'], color='blue', linewidth=2, label='Strategy')
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
    
    def plot_optimization_heatmap(self, results_df, x_col, y_col, value_col):
        """Plot optimization results as heatmap"""
        # Create pivot table for heatmap
        pivot_data = results_df.pivot(index=y_col, columns=x_col, values=value_col)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='RdYlGn', center=0)
        plt.title(f'Strategy Optimization: {value_col.title()} by Parameters')
        plt.xlabel(f'{x_col.title()} (BB Multiplier)' if x_col == 'threshold' else x_col.title())
        plt.ylabel(f'{y_col.title()} (BB Window)' if y_col == 'window' else y_col.title())
        plt.show()
        
        # Additional summary plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Best parameters by Sharpe
        top_10 = results_df.head(10)
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top_10)))
        
        bars = ax1.bar(range(len(top_10)), top_10['sharpe'], color=colors)
        ax1.set_title('Top 10 Parameter Combinations (by Sharpe Ratio)')
        ax1.set_xlabel('Rank')
        ax1.set_ylabel('Sharpe Ratio')
        ax1.grid(True, alpha=0.3)
        
        # Add parameter labels
        for i, (idx, row) in enumerate(top_10.iterrows()):
            ax1.text(i, row['sharpe'] + 0.01, f'W:{int(row["window"])}\nT:{row["threshold"]:.2f}', 
                    ha='center', va='bottom', fontsize=8)
        
        # Correlation between parameters and performance
        ax2.scatter(results_df['window'], results_df['sharpe'], alpha=0.6, label='Window vs Sharpe')
        ax2.set_xlabel('BB Window')
        ax2.set_ylabel('Sharpe Ratio')
        ax2.set_title('Parameter vs Performance')
        ax2.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(results_df['window'], results_df['sharpe'], 1)
        p = np.poly1d(z)
        ax2.plot(results_df['window'], p(results_df['window']), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.show()