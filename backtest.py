import pandas as pd

class Backtester:
    """
    Simulates backtesting logic for CTA strategies.
    """
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital

    def run_backtest(self, df, signals):
        """
        Simulate positions, PnL, and equity curve.
        Returns a DataFrame with equity and positions.
        """
        df = df.copy()
        df = df.merge(signals, on='timestamp', how='left')
        if 'signal' not in df.columns:
            df['signal'] = 0
        else:
            df['signal'] = df['signal'].fillna(0)
        df['position'] = 0
        df['cash'] = self.initial_capital
        df['equity'] = self.initial_capital
        position = 0
        for i in range(1, len(df)):
            if df['signal'].iloc[i] == 1:
                position = 1
            elif df['signal'].iloc[i] == -1:
                position = -1
            df.at[df.index[i], 'position'] = position
            df.at[df.index[i], 'cash'] = df['cash'].iloc[i-1]
            df.at[df.index[i], 'equity'] = df['cash'].iloc[i-1] + position * (df['close'].iloc[i] - df['close'].iloc[i-1])
        return df 