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
        
        # 1. Price with Moving Average and signals
        ax1.plot(df['timestamp'], df['close'], label='Price', color='black', linewidth=1.5)
        
        # Add moving average if available
        if 'ma' in df.columns:
            ax1.plot(df['timestamp'], df['ma'], label='Moving Average', color='blue', linewidth=2, alpha=0.8)
            
            # Add price bands (MA ± 1 and 2 standard deviations) if zscore data available
            if 'zscore' in df.columns:
                # Calculate approximate price bands from z-score
                price_std = (df['close'] - df['ma']).std()
                upper_1std = df['ma'] + price_std
                lower_1std = df['ma'] - price_std
                upper_2std = df['ma'] + 2 * price_std
                lower_2std = df['ma'] - 2 * price_std
                
                ax1.plot(df['timestamp'], upper_2std, color='red', alpha=0.5, linestyle='--', label='MA + 2σ')
                ax1.plot(df['timestamp'], upper_1std, color='orange', alpha=0.5, linestyle='--', label='MA + 1σ')
                ax1.plot(df['timestamp'], lower_1std, color='orange', alpha=0.5, linestyle='--', label='MA - 1σ')
                ax1.plot(df['timestamp'], lower_2std, color='green', alpha=0.5, linestyle='--', label='MA - 2σ')
                
                # Fill areas
                ax1.fill_between(df['timestamp'], upper_1std, upper_2std, alpha=0.1, color='red')
                ax1.fill_between(df['timestamp'], lower_1std, lower_2std, alpha=0.1, color='green')
        
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
        
        ax1.set_title('Price with Moving Average & Z-Score Strategy Signals')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Z-Score
        if 'zscore' in df.columns:
            ax2.plot(df['timestamp'], df['zscore'], color='purple', linewidth=1, label='Z-Score')
            
            # Add threshold lines
            zscore_max = df['zscore'].max()
            zscore_min = df['zscore'].min()
            
            # Common threshold levels
            for threshold in [1.0, 1.5, 2.0, 2.5, 3.0]:
                if threshold <= zscore_max:
                    ax2.axhline(y=threshold, color='red', linestyle='--', alpha=0.6, 
                               label=f'Entry +{threshold}' if threshold == 2.0 else '')
                if -threshold >= zscore_min:
                    ax2.axhline(y=-threshold, color='green', linestyle='--', alpha=0.6,
                               label=f'Entry -{threshold}' if threshold == 2.0 else '')
            
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5, label='Mean (MA)')
            
            # Highlight long entry zones with background shading
            ax2.fill_between(df['timestamp'], 0, df['zscore'].max(), 
                           where=(df['zscore'] > 1.5), alpha=0.1, color='orange', 
                           label='Long Entry Zone')
            
            # Mark actual entry points
            entry_points = df[df['position'] == 1]
            if len(entry_points) > 0:
                ax2.scatter(entry_points['timestamp'], entry_points['zscore'], 
                          color='orange', marker='o', s=30, alpha=0.8, 
                          label='Long Positions', zorder=5)
            
            ax2.set_title('Z-Score (Price Deviation from MA)')
            ax2.set_ylabel('Z-Score')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        elif 'ma' in df.columns:
            # Fallback: show price vs MA
            ax2.plot(df['timestamp'], df['close'], color='black', linewidth=1, label='Price')
            ax2.plot(df['timestamp'], df['ma'], color='blue', linewidth=1.5, label='Moving Average')
            ax2.set_title('Price vs Moving Average')
            ax2.set_ylabel('Price ($)')
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
        plt.title(f'Z-Score Strategy Optimization: {value_col.title()} by Parameters')
        plt.xlabel(f'{x_col.title()} (Z-Score Threshold)' if x_col == 'threshold' else x_col.title())
        plt.ylabel(f'{y_col.title()} (MA Window)' if y_col == 'window' else y_col.title())
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
        ax2.set_xlabel('MA Window')
        ax2.set_ylabel('Sharpe Ratio')
        ax2.set_title('MA Window vs Performance')
        ax2.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(results_df['window'], results_df['sharpe'], 1)
        p = np.poly1d(z)
        ax2.plot(results_df['window'], p(results_df['window']), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.show()