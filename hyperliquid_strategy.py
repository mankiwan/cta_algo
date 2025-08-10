"""
Hyperliquid Strategy - Z-Score Strategy Module  

Strategy Logic:
- Calculate Z-Score: (price - moving_average) / standard_deviation
- Long Entry: When Z-score > threshold (price above MA)
- Position: 1 if z-score > threshold, else 0 (long-only)

Author: Trading Bot System
"""

import pandas as pd
import numpy as np


class ZScoreStrategy:
    """Simple Z-Score mean reversion strategy."""
    
    def __init__(self, params: dict):
        """Initialize strategy with parameters.
        
        Args:
            params: Dictionary containing strategy parameters
                - ma_window: Moving average window (default: 50)
                - zscore_threshold: Z-score threshold for entry (default: 2.0)
                - position_size_pct: Position size as % of balance (default: 5.0)
                - tp_pct: Take profit percentage (default: 5.0)
                - sl_pct: Stop loss percentage (default: 3.0)
        """
        self.params = params
        
    def calculate_zscore(self, prices: pd.Series, window: int) -> tuple:
        """Calculate z-score: (price - moving_average) / standard_deviation
        
        Args:
            prices: Price series
            window: Moving average window
            
        Returns:
            Tuple of (zscore, moving_average)
        """
        ma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        zscore = (prices - ma) / std
        return zscore, ma
    
    def compute_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Compute Z-score and moving average indicators.
        
        Args:
            data: OHLCV DataFrame with timestamp index
            
        Returns:
            DataFrame with added zscore and ma columns
        """
        df = data.copy()
        window = self.params.get('ma_window', 50)
        
        # Calculate Z-score and moving average
        df['zscore'], df['ma'] = self.calculate_zscore(df['close'], window)
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on Z-score.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            DataFrame with position signals (1 = long, 0 = neutral)
        """
        df = self.compute_indicators(data)
        threshold = self.params.get('zscore_threshold', 2.0)
        
        # Simple vectorized position logic: 1 if zscore > threshold, else 0
        df['position'] = np.where(df['zscore'] > threshold, 1, 0)
        
        return df
    
    def check_long_entry_condition(self, current_candle: pd.Series, previous_candle: pd.Series) -> bool:
        """Check if long entry conditions are met.
        
        Args:
            current_candle: Latest candle data with indicators
            previous_candle: Previous candle data with indicators
            
        Returns:
            True if should enter long position
        """
        threshold = self.params.get('zscore_threshold', 2.0)
        
        # Entry when Z-score crosses above threshold
        return (previous_candle.get('zscore', 0) <= threshold < current_candle.get('zscore', 0))
    
    def check_long_exit_condition(self, current_candle: pd.Series, previous_candle: pd.Series) -> bool:
        """Check if long exit conditions are met.
        
        Args:
            current_candle: Latest candle data with indicators
            previous_candle: Previous candle data with indicators
            
        Returns:
            True if should exit long position
        """
        exit_threshold = self.params.get('zscore_exit', 0.5)
        
        # Exit when Z-score drops below exit threshold (back to normal)
        return current_candle.get('zscore', 0) < exit_threshold
    
    def check_short_entry_condition(self, current_candle: pd.Series, previous_candle: pd.Series) -> bool:
        """Check if short entry conditions are met.
        
        For Z-score mean reversion, shorts would be when price is way below MA (oversold).
        This is opposite of the current logic.
        """
        return False  # Disabled for long-only strategy
    
    def check_short_exit_condition(self, current_candle: pd.Series, previous_candle: pd.Series) -> bool:
        """Check if short exit conditions are met."""
        return False  # Disabled for long-only strategy
    
    def compute_long_tp_level(self, entry_price: float) -> float:
        """Calculate long position take profit level."""
        return entry_price * (1 + self.params.get("tp_pct", 5.0) / 100)
    
    def compute_long_sl_level(self, entry_price: float) -> float:
        """Calculate long position stop loss level."""
        return entry_price * (1 - self.params.get("sl_pct", 3.0) / 100)
    
    def compute_short_tp_level(self, entry_price: float) -> float:
        """Calculate short position take profit level."""
        return entry_price * (1 - self.params.get("tp_pct", 5.0) / 100)
    
    def compute_short_sl_level(self, entry_price: float) -> float:
        """Calculate short position stop loss level."""
        return entry_price * (1 + self.params.get("sl_pct", 3.0) / 100)
    
    def calculate_position_size(self, balance: float) -> float:
        """Calculate position size based on account balance.
        
        Args:
            balance: Available account balance in USDC
            
        Returns:
            Position size in USD value
        """
        return balance * self.params.get("position_size_pct", 5.0) / 100


# Default parameters matching your existing strategy
DEFAULT_ZSCORE_PARAMS = {
    "symbol": "BTC/USDC:USDC",
    "timeframe": "1h",
    "position_size_pct": 5.0,
    "leverage": 1,
    "margin_mode": "isolated",
    "ma_window": 50,                  # Moving average window
    "zscore_threshold": 2.0,          # Entry threshold
    "zscore_exit": 0.5,              # Exit threshold
    "tp_pct": 5.0,                   # Take profit %
    "sl_pct": 3.0,                   # Stop loss %
}


def create_strategy(strategy_type: str = "zscore", custom_params: dict = None) -> ZScoreStrategy:
    """Create a Z-Score strategy instance.
    
    Args:
        strategy_type: Only "zscore" supported (kept for compatibility)
        custom_params: Optional custom parameters to override defaults
        
    Returns:
        ZScoreStrategy instance
    """
    # Use default Z-Score parameters
    params = DEFAULT_ZSCORE_PARAMS.copy()
    
    # Override with custom parameters
    if custom_params:
        params.update(custom_params)
    
    return ZScoreStrategy(params)


if __name__ == "__main__":
    # Simple test with sample data
    import datetime
    
    print("=== Testing Z-Score Strategy ===")
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='h')
    sample_data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 42000,
        'high': np.random.randn(100).cumsum() + 42200,
        'low': np.random.randn(100).cumsum() + 41800,
        'close': np.random.randn(100).cumsum() + 42000,
        'volume': np.random.rand(100) * 100
    }, index=dates)
    
    # Test strategy
    try:
        strategy = create_strategy("zscore", {"ma_window": 20, "zscore_threshold": 1.5})
        
        # Generate signals
        df_with_signals = strategy.generate_signals(sample_data)
        
        print(f"✓ Strategy created successfully")
        print(f"✓ Indicators computed: {[col for col in df_with_signals.columns if col not in sample_data.columns]}")
        print(f"✓ Long signals generated: {df_with_signals['position'].sum()} out of {len(df_with_signals)}")
        
        # Test entry/exit conditions
        current = df_with_signals.iloc[-1]
        previous = df_with_signals.iloc[-2]
        
        long_entry = strategy.check_long_entry_condition(current, previous)
        long_exit = strategy.check_long_exit_condition(current, previous)
        
        print(f"✓ Current Z-Score: {current.get('zscore', 0):.2f}")
        print(f"✓ Long entry signal: {long_entry}")
        print(f"✓ Long exit signal: {long_exit}")
        
    except Exception as e:
        print(f"✗ Strategy test failed: {e}")