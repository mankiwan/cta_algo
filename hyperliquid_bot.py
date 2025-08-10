"""
Hyperliquid Bot - Main Trading Bot Execution Module

This is the main trading bot that combines the client and strategy modules
to execute automated trading on Hyperliquid exchange.

🔧 CONFIGURATION: All settings are in this file - no need to edit other files!
   - API credentials (wallet address, private key)
   - Trading strategy and parameters  
   - Risk management settings
   - Safety controls and dry-run mode

Features:
- Simple Z-Score mean reversion strategy (based on your strategy.py)
- Risk management and position sizing
- Account setup (leverage, margin mode)
- Real-time market data processing
- Position monitoring and exit management
- Comprehensive logging and error handling
- Safety controls (ignore flags)

Usage:
1. Edit the CONFIGURATION SECTION below
2. Run: python hyperliquid_bot.py

Author: Trading Bot System
"""

import sys
from datetime import datetime
import os
# Import our custom modules
from hyperliquid_client import HyperliquidClient, my_print
from hyperliquid_strategy import create_strategy
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CONFIGURATION SECTION - EDIT HERE FOR ALL SETTINGS
# ==========================================

# API Configuration
API_CONFIG = {
    "wallet_address": os.getenv("HYPERLIQUID_WALLET_ADDRESS"),
    "private_key": os.getenv("HYPERLIQUID_PRIVATE_KEY"),
}

# Strategy Configuration
STRATEGY_CONFIG = {
    "strategy_type": "zscore",        # Only "zscore" supported (simplified)
    "symbol": "BTC/USDC:USDC",        # Trading pair
    "timeframe": "1h",                # Candle timeframe (1h for more signals)
    "position_size_pct": 5.0,         # % of balance to risk per trade
    "leverage": 1,                    # Leverage multiplier
    "margin_mode": "isolated",        # "isolated" or "cross"
    
    # Z-Score Parameters (matching your strategy.py)
    "ma_window": 50,                  # Moving average window
    "zscore_threshold": 2.0,          # Entry when Z-score > threshold
    "zscore_exit": 0.5,              # Exit when Z-score < exit threshold
    
    # Risk Management
    "tp_pct": 5.0,                    # Take profit %
    "sl_pct": 3.0,                    # Stop loss %
}

# Safety Controls - Set to True to disable specific actions
SAFETY_FLAGS = {
    "ignore_longs": False,            # Disable long entries
    "ignore_shorts": True,            # Disable short entries (default: safer)
    "ignore_exits": False,            # Disable position exits
    "ignore_tp": False,               # Disable take profit orders
    "ignore_sl": False,               # Disable stop loss orders
    "dry_run": False,                 # Set True for simulation only
}

# Logging and Display
VERBOSE = True                        # Enable detailed logging


# ==========================================
# MAIN TRADING BOT CLASS
# ==========================================

class HyperliquidTradingBot:
    """Main trading bot class that orchestrates client and strategy."""
    
    def __init__(self, api_config: dict, strategy_config: dict, safety_flags: dict, verbose: bool = True):
        """Initialize the trading bot.
        
        Args:
            api_config: API credentials (wallet_address, private_key)
            strategy_config: Strategy parameters dictionary
            safety_flags: Safety control flags
            verbose: Enable verbose logging
        """
        self.config = strategy_config
        self.safety = safety_flags
        self.verbose = verbose
        
        # Initialize client and strategy
        try:
            self.client = HyperliquidClient(
                wallet_address=api_config["wallet_address"],
                private_key=api_config["private_key"]
            )
            self.strategy = create_strategy(
                strategy_type=strategy_config["strategy_type"],
                custom_params=strategy_config
            )
            my_print("✓ Bot initialized successfully", self.verbose)
        except Exception as e:
            my_print(f"✗ Bot initialization failed: {e}", True)
            raise
    
    def setup_account(self):
        """Setup trading account with leverage and margin mode."""
        try:
            symbol = self.config["symbol"]
            leverage = self.config["leverage"]
            margin_mode = self.config["margin_mode"]
            
            if not self.safety["dry_run"]:
                self.client.set_leverage(symbol, leverage)
                self.client.set_margin_mode(symbol, margin_mode, leverage)
                
            my_print(f"✓ Account setup: {leverage}x {margin_mode} margin for {symbol}", self.verbose)
            return True
            
        except Exception as e:
            my_print(f"✗ Account setup failed: {e}", True)
            return False
    
    def get_market_data(self):
        """Fetch and process market data with indicators."""
        try:
            symbol = self.config["symbol"]
            timeframe = self.config["timeframe"]
            
            # Fetch OHLCV data
            df = self.client.fetch_ohlcv(symbol, timeframe, limit=200)
            
            # Compute technical indicators
            df = self.strategy.compute_indicators(df)
            
            # Get current and previous candle
            current_candle = df.iloc[-2]  # Latest complete candle
            previous_candle = df.iloc[-3] # Previous candle
            current_price = current_candle['close']
            
            my_print(f"✓ Market data fetched: {symbol} @ ${current_price:.2f}", self.verbose)
            
            return df, current_candle, previous_candle, current_price
            
        except Exception as e:
            my_print(f"✗ Market data fetch failed: {e}", True)
            return None, None, None, None
    
    def get_account_status(self):
        """Get current account balance and positions."""
        try:
            # Fetch balance
            balance_info = self.client.fetch_balance()
            balance = float(balance_info["total"]["USDC"])
            
            # Fetch positions
            positions = self.client.fetch_positions([self.config["symbol"]])
            current_position = positions[0] if positions else None
            
            my_print(f"✓ Account: {balance:.2f} USDC, Positions: {len(positions)}", self.verbose)
            
            return balance, current_position
            
        except Exception as e:
            my_print(f"✗ Account status fetch failed: {e}", True)
            return 0, None
    
    def manage_existing_position(self, current_position, current_candle, previous_candle):
        """Manage existing positions - check for exit signals."""
        try:
            position_side = current_position["side"].lower()
            position_size = abs(float(current_position["contracts"]))
            symbol = self.config["symbol"]
            
            my_print(f"Managing {position_side} position: {position_size} contracts", self.verbose)
            
            # Check long exit
            if position_side == "long" and not self.safety["ignore_longs"] and not self.safety["ignore_exits"]:
                if self.strategy.check_long_exit_condition(current_candle, previous_candle):
                    my_print("🔴 Long exit signal detected", self.verbose)
                    
                    if not self.safety["dry_run"]:
                        order = self.client.place_market_order(
                            symbol, "sell", position_size, reduce_only=True
                        )
                        my_print(f"✓ Long position closed: {order.get('market_order', {}).get('resting')}", self.verbose)
                    else:
                        my_print("📋 DRY RUN: Would close long position", self.verbose)
                    
                    return True
            
            # Check short exit
            elif position_side == "short" and not self.safety["ignore_shorts"] and not self.safety["ignore_exits"]:
                if self.strategy.check_short_exit_condition(current_candle, previous_candle):
                    my_print("🔴 Short exit signal detected", self.verbose)
                    
                    if not self.safety["dry_run"]:
                        order = self.client.place_market_order(
                            symbol, "buy", position_size, reduce_only=True
                        )
                        my_print(f"✓ Short position closed: {order.get('market_order', {}).get('resting')}", self.verbose)
                    else:
                        my_print("📋 DRY RUN: Would close short position", self.verbose)
                    
                    return True
            
            return False
            
        except Exception as e:
            my_print(f"✗ Position management failed: {e}", True)
            return False
    
    def check_entry_signals(self, balance, current_candle, previous_candle, current_price):
        """Check for entry signals and open new positions."""
        try:
            symbol = self.config["symbol"]
            
            # Check long entry
            if not self.safety["ignore_longs"] and self.strategy.check_long_entry_condition(current_candle, previous_candle):
                my_print("🟢 Long entry signal detected", self.verbose)
                return self._open_long_position(balance, current_price)
            
            # Check short entry
            elif not self.safety["ignore_shorts"] and self.strategy.check_short_entry_condition(current_candle, previous_candle):
                my_print("🟢 Short entry signal detected", self.verbose)
                return self._open_short_position(balance, current_price)
            
            return False
            
        except Exception as e:
            my_print(f"✗ Entry signal check failed: {e}", True)
            return False
    
    def _open_long_position(self, balance, current_price):
        """Open a long position with risk management."""
        try:
            symbol = self.config["symbol"]
            
            # Calculate position size
            position_size_usd = self.strategy.calculate_position_size(balance)
            amount = position_size_usd / current_price
            
            # Calculate TP/SL levels
            tp_price = None if self.safety["ignore_tp"] else self.strategy.compute_long_tp_level(current_price)
            sl_price = None if self.safety["ignore_sl"] else self.strategy.compute_long_sl_level(current_price)
            
            my_print(f"Opening long: ${position_size_usd:.2f} ({amount:.6f} BTC)", self.verbose)
            my_print(f"Entry: ${current_price:.2f}, TP: ${tp_price:.2f if tp_price else 'None'}, SL: ${sl_price:.2f if sl_price else 'None'}", self.verbose)
            
            if not self.safety["dry_run"]:
                orders = self.client.place_market_order(
                    symbol, "buy", amount,
                    take_profit_price=tp_price,
                    stop_loss_price=sl_price
                )
                
                if orders.get("market_order"):
                    my_print(f"✓ Long position opened: {orders['market_order'].get('resting')}", self.verbose)
                    if orders.get("take_profit_order"):
                        my_print(f"✓ Take profit set: {orders['take_profit_order'].get('resting')}", self.verbose)
                    if orders.get("stop_loss_order"):
                        my_print(f"✓ Stop loss set: {orders['stop_loss_order'].get('resting')}", self.verbose)
            else:
                my_print("📋 DRY RUN: Would open long position", self.verbose)
            
            return True
            
        except Exception as e:
            my_print(f"✗ Long position opening failed: {e}", True)
            return False
    
    def _open_short_position(self, balance, current_price):
        """Open a short position with risk management."""
        try:
            symbol = self.config["symbol"]
            
            # Calculate position size
            position_size_usd = self.strategy.calculate_position_size(balance)
            amount = position_size_usd / current_price
            
            # Calculate TP/SL levels
            tp_price = None if self.safety["ignore_tp"] else self.strategy.compute_short_tp_level(current_price)
            sl_price = None if self.safety["ignore_sl"] else self.strategy.compute_short_sl_level(current_price)
            
            my_print(f"Opening short: ${position_size_usd:.2f} ({amount:.6f} BTC)", self.verbose)
            my_print(f"Entry: ${current_price:.2f}, TP: ${tp_price:.2f if tp_price else 'None'}, SL: ${sl_price:.2f if sl_price else 'None'}", self.verbose)
            
            if not self.safety["dry_run"]:
                orders = self.client.place_market_order(
                    symbol, "sell", amount,
                    take_profit_price=tp_price,
                    stop_loss_price=sl_price
                )
                
                if orders.get("market_order"):
                    my_print(f"✓ Short position opened: {orders['market_order'].get('resting')}", self.verbose)
                    if orders.get("take_profit_order"):
                        my_print(f"✓ Take profit set: {orders['take_profit_order'].get('resting')}", self.verbose)
                    if orders.get("stop_loss_order"):
                        my_print(f"✓ Stop loss set: {orders['stop_loss_order'].get('resting')}", self.verbose)
            else:
                my_print("📋 DRY RUN: Would open short position", self.verbose)
            
            return True
            
        except Exception as e:
            my_print(f"✗ Short position opening failed: {e}", True)
            return False
    
    def run_single_iteration(self):
        """Run a single iteration of the trading bot."""
        my_print(f"\n{'='*50}", self.verbose)
        my_print(f"🤖 Bot Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.verbose)
        my_print(f"Strategy: {self.config['strategy_type'].upper()} | Symbol: {self.config['symbol']}", self.verbose)
        my_print(f"{'='*50}", self.verbose)
        
        try:
            # 1. Get market data
            df, current_candle, previous_candle, current_price = self.get_market_data()
            if df is None:
                return False
            
            # 2. Get account status
            balance, current_position = self.get_account_status()
            if balance == 0:
                return False
            
            # 3. Manage existing positions
            if current_position:
                position_closed = self.manage_existing_position(current_position, current_candle, previous_candle)
                if position_closed:
                    my_print("✓ Position management completed", self.verbose)
                    return True
            
            # 4. Setup account for new positions
            else:
                if not self.setup_account():
                    return False
                
                # 5. Check for entry signals
                entry_executed = self.check_entry_signals(balance, current_candle, previous_candle, current_price)
                if entry_executed:
                    my_print("✓ Entry signal executed", self.verbose)
                    return True
                else:
                    my_print("⏸ No entry signals detected", self.verbose)
            
            return True
            
        except Exception as e:
            my_print(f"✗ Bot iteration failed: {e}", True)
            return False


# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    """Main execution function."""
    my_print("🚀 Starting Hyperliquid Trading Bot", True)
    my_print(f"Strategy: {STRATEGY_CONFIG['strategy_type'].upper()}", True)
    my_print(f"Symbol: {STRATEGY_CONFIG['symbol']}", True)
    
    if SAFETY_FLAGS["dry_run"]:
        my_print("📋 DRY RUN MODE - No real trades will be executed", True)
    
    try:
        # Initialize bot
        bot = HyperliquidTradingBot(API_CONFIG, STRATEGY_CONFIG, SAFETY_FLAGS, VERBOSE)
        
        # Run single iteration (for cron job or scheduled execution)
        success = bot.run_single_iteration()
        
        if success:
            my_print("✅ Bot run completed successfully", True)
            sys.exit(0)
        else:
            my_print("❌ Bot run failed", True)
            sys.exit(1)
            
    except KeyboardInterrupt:
        my_print("\n⏹ Bot stopped by user", True)
        sys.exit(0)
    except Exception as e:
        my_print(f"💥 Critical error: {e}", True)
        sys.exit(1)


if __name__ == "__main__":
    main()