import pandas as pd
import numpy as np

class Strategy:
    """
    Simplified CTA strategy using 40-day SMA, Bollinger Bands, and RSI
    Designed for 1-hour timeframe with 1-2x leverage support and max 1-2 concurrent positions
    """
    def __init__(self, sma_period=40, bb_period=20, bb_std=2, rsi_period=14,
                 risk_per_trade=0.02, max_leverage=2.0, max_positions=2):
        # Indicator parameters
        self.sma_period = sma_period          # 40-day SMA
        self.bb_period = bb_period            # 20-day Bollinger Bands
        self.bb_std = bb_std                  # Bollinger Bands standard deviation multiplier
        self.rsi_period = rsi_period          # 14-day RSI
        
        # Risk management parameters
        self.risk_per_trade = risk_per_trade  # Risk 2% per trade
        self.max_leverage = max_leverage      # Maximum 2x leverage
        self.max_positions = max_positions    # Maximum 2 concurrent positions

    def sma(self, series, period):
        """Simple Moving Average"""
        return series.rolling(window=period).mean()

    def rsi(self, df, period=None):
        """RSI Relative Strength Index"""
        period = period or self.rsi_period
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df

    def bollinger_bands(self, df, period=None, std_dev=None):
        """Bollinger Bands"""
        period = period or self.bb_period
        std_dev = std_dev or self.bb_std
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        df['bb_std'] = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + std_dev * df['bb_std']
        df['bb_lower'] = df['bb_middle'] - std_dev * df['bb_std']
        return df

    def calculate_atr(self, df, period=14):
        """Calculate ATR for stop loss calculation"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(period).mean()

    def generate_signals(self, df):
        """
        Generate trading signals (simplified version)
        Uses strategy combinations with at least 2 indicator confirmations
        
        Buy signals:
        1. Trend following: Price > 40-day SMA + RSI < 70 + Price near BB lower band
        2. Oversold bounce: Price < BB lower band + RSI < 30  
        3. Trend support: Price > 40-day SMA + Price > BB middle + RSI between 40-60
        
        Sell signals:
        1. Trend reversal: Price < 40-day SMA + RSI > 30 + Price near BB upper band
        2. Overbought pullback: Price > BB upper band + RSI > 70
        3. Trend resistance: Price < 40-day SMA + Price < BB middle + RSI between 40-60
        """
        # Calculate indicators
        df['sma_40'] = self.sma(df['close'], self.sma_period)
        df = self.rsi(df)
        df = self.bollinger_bands(df)
        df['atr'] = self.calculate_atr(df)
        
        # Initialize signals
        df['signal'] = 0
        df['signal_type'] = 'hold'
        
        # Buy signal combinations
        # Combo 1: Trend following + near lower band (buy the dip)
        buy_combo1 = (
            (df['close'] > df['sma_40']) & 
            (df['rsi'] < 70) & 
            (df['close'] <= df['bb_lower'] * 1.02)  # Near or below lower band
        )
        
        # Combo 2: Oversold bounce (mean reversion)
        buy_combo2 = (
            (df['close'] < df['bb_lower']) & 
            (df['rsi'] < 30)
        )
        
        # Combo 3: Trend + middle band support
        buy_combo3 = (
            (df['close'] > df['sma_40']) & 
            (df['close'] > df['bb_middle']) & 
            (df['rsi'] >= 40) & (df['rsi'] <= 60)
        )
        
        # Sell signal combinations
        # Combo 1: Trend reversal + near upper band (sell the rally)
        sell_combo1 = (
            (df['close'] < df['sma_40']) & 
            (df['rsi'] > 30) & 
            (df['close'] >= df['bb_upper'] * 0.98)  # Near or above upper band
        )
        
        # Combo 2: Overbought pullback (mean reversion)
        sell_combo2 = (
            (df['close'] > df['bb_upper']) & 
            (df['rsi'] > 70)
        )
        
        # Combo 3: Trend reversal + middle band resistance
        sell_combo3 = (
            (df['close'] < df['sma_40']) & 
            (df['close'] < df['bb_middle']) & 
            (df['rsi'] >= 40) & (df['rsi'] <= 60)
        )
        
        # Apply signals
        df.loc[buy_combo1, ['signal', 'signal_type']] = [1, 'trend_dip_buy']
        df.loc[buy_combo2, ['signal', 'signal_type']] = [1, 'oversold_buy'] 
        df.loc[buy_combo3, ['signal', 'signal_type']] = [1, 'trend_support_buy']
        
        df.loc[sell_combo1, ['signal', 'signal_type']] = [-1, 'trend_peak_sell']
        df.loc[sell_combo2, ['signal', 'signal_type']] = [-1, 'overbought_sell']
        df.loc[sell_combo3, ['signal', 'signal_type']] = [-1, 'trend_resistance_sell']
        
        return df[['timestamp', 'signal', 'signal_type']]
    
    def calculate_position_size(self, current_price, leverage=1.0):
        """
        Calculate position size
        Considers leverage and maximum position limits
        """
        # Base position (2% risk)
        base_position = self.risk_per_trade
        
        # Apply leverage (1-2x)
        leverage = min(max(leverage, 1.0), self.max_leverage)
        position_size = base_position * leverage
        
        # Consider maximum position limits (total capital / max positions)
        max_single_position = 1.0 / self.max_positions  # If max 2 positions, 50% each max
        position_size = min(position_size, max_single_position)
        
        # Minimum position threshold
        min_size = 0.01  # 1%
        position_size = max(position_size, min_size) if position_size > 0 else 0
        
        return position_size
    
    def calculate_stop_loss(self, df, entry_price, direction, atr_multiplier=1.5):
        """
        Calculate stop loss based on ATR (conservative 1.5x ATR)
        direction: 1 for long, -1 for short
        """
        current_atr = df['atr'].iloc[-1] if 'atr' in df.columns and len(df) > 0 else entry_price * 0.015
        
        if direction == 1:  # Long position
            stop_loss = entry_price - (atr_multiplier * current_atr)
        else:  # Short position
            stop_loss = entry_price + (atr_multiplier * current_atr)
        
        return stop_loss
    
    def calculate_take_profit(self, entry_price, stop_loss, reward_ratio=2.0):
        """
        Calculate take profit based on risk-reward ratio (2:1)
        """
        risk = abs(entry_price - stop_loss)
        
        if entry_price > stop_loss:  # Long position
            take_profit = entry_price + (reward_ratio * risk)
        else:  # Short position
            take_profit = entry_price - (reward_ratio * risk)
        
        return take_profit
    
    def generate_signals_with_risk_management(self, df, leverage=1.0):
        """
        Generate signals with risk management
        Includes position sizing, stop loss and take profit calculations
        """
        # Get basic signals
        signals_df = self.generate_signals(df)
        
        # Add risk management for each signal
        position_sizes = []
        stop_losses = []
        take_profits = []
        leverages = []
        
        for idx, row in signals_df.iterrows():
            if row['signal'] != 0:
                # Get current price
                current_price = df.loc[df['timestamp'] == row['timestamp'], 'close'].iloc[0]
                
                # Calculate position size
                position_size = self.calculate_position_size(current_price, leverage)
                
                # Calculate stop loss
                stop_loss = self.calculate_stop_loss(df, current_price, row['signal'])
                
                # Calculate take profit
                take_profit = self.calculate_take_profit(current_price, stop_loss)
                
                leverages.append(leverage)
            else:
                position_size = 0
                stop_loss = None
                take_profit = None
                leverages.append(0)
            
            position_sizes.append(position_size)
            stop_losses.append(stop_loss)
            take_profits.append(take_profit)
        
        # Add risk management columns
        signals_df['position_size'] = position_sizes
        signals_df['stop_loss'] = stop_losses  
        signals_df['take_profit'] = take_profits
        signals_df['leverage'] = leverages
        
        return signals_df
    
    def get_strategy_summary(self):
        """Return strategy summary"""
        return {
            "Strategy Type": "Simplified CTA Strategy",
            "Indicators": ["40-day SMA", "20-day Bollinger Bands", "14-day RSI"],
            "Timeframe": "1 hour",
            "Max Leverage": f"{self.max_leverage}x",
            "Max Positions": f"{self.max_positions}",
            "Risk per Trade": f"{self.risk_per_trade*100}%",
            "Risk-Reward Ratio": "1:2",
            "Stop Loss Method": "1.5x ATR"
        }