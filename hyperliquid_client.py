"""
Hyperliquid Client - Exchange Interface Module

This module provides a clean interface to interact with Hyperliquid exchange
using CCXT. Handles authentication, market data, order execution, and account management.

Features:
- Account balance and positions fetching
- Market and limit order execution  
- OHLCV data retrieval
- Leverage and margin mode management
- Precision formatting for exchange requirements
- Comprehensive error handling

Author: Trading Bot System
"""

import os
import ccxt
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class HyperliquidClient:
    """Simple synchronous client for Hyperliquid exchange using CCXT."""
    
    def __init__(self, wallet_address: str, private_key: str):
        """Initialize the Hyperliquid client.
        
        Args:
            wallet_address: Your Hyperliquid wallet address
            private_key: Your wallet's private key
        """
        # Initializes the client with wallet credentials, creates CCXT exchange instance 
        # with rate limiting enabled, and loads market data
        if not wallet_address:
            raise ValueError("wallet_address is required")
        
        if not private_key:
            raise ValueError("private_key is required")
            
        try:
            self.exchange = ccxt.hyperliquid({
                "walletAddress": wallet_address,
                "privateKey": private_key,
                "enableRateLimit": True,
            })
            self.markets = {}
            self._load_markets()
        except Exception as e:
            raise Exception(f"Failed to initialize exchange: {str(e)}")

    def _load_markets(self) -> None:
        """Load market data from the exchange."""
        # Loads market information from the exchange to cache symbol data and trading requirements
        try:
            self.markets = self.exchange.load_markets()
        except Exception as e:
            raise Exception(f"Failed to load markets: {str(e)}")

    def _amount_to_precision(self, symbol: str, amount: float) -> float:
        """Convert amount to exchange precision requirements.
        
        Args:
            symbol: Trading pair symbol
            amount: Order amount to format
            
        Returns:
            Amount formatted with correct precision as float
        """
        # Formats order amounts according to exchange precision requirements to avoid order rejection
        try:
            result = self.exchange.amount_to_precision(symbol, amount)
            return float(result)
        except Exception as e:
            raise Exception(f"Failed to format amount precision: {str(e)}")

    def _price_to_precision(self, symbol: str, price: float) -> float:
        """Convert price to exchange precision requirements.
        
        Args:
            symbol: Trading pair symbol
            price: Order price to format
            
        Returns:
            Price formatted with correct precision as float
        """
        # Formats prices according to exchange precision requirements for proper order formatting
        try:
            result = self.exchange.price_to_precision(symbol, price)
            return float(result)
        except Exception as e:
            raise Exception(f"Failed to format price precision: {str(e)}")

    def get_current_price(self, symbol: str) -> float:
        """Get the current market price for a symbol.
        
        Args:
            symbol: Trading pair (e.g., "ETH/USDC:USDC")
            
        Returns:
            Current market price
        """
        # Retrieves current market price for a trading pair using the midpoint price from market info
        try:
            return float(self.markets[symbol]["info"]["midPx"])
        except Exception as e:
            raise Exception(f"Failed to get price for {symbol}: {str(e)}")

    def fetch_balance(self) -> dict:
        """Fetch account balance information.
        
        Returns:
            Account balance data with 'total', 'free', 'used' for each currency
        """
        # Fetches account balance showing total, free, and used amounts for each currency
        try:
            result = self.exchange.fetch_balance()
            return result
        except Exception as e:
            raise Exception(f"Failed to fetch balance: {str(e)}")

    def fetch_positions(self, symbols: list[str] = None) -> list:
        """Fetch open positions for specified symbols.
        
        Args:
            symbols: List of trading pairs (optional, fetches all if None)
            
        Returns:
            List of position dictionaries with active positions only
        """
        # Fetches active positions, filtering out zero-size positions to show only actual holdings
        try:
            positions = self.exchange.fetch_positions(symbols)
            return [pos for pos in positions if float(pos["contracts"]) != 0]
        except Exception as e:
            raise Exception(f"Failed to fetch positions: {str(e)}")

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 100) -> pd.DataFrame:
        """Fetch OHLCV candlestick data.
        
        Args:
            symbol: Trading pair symbol
            timeframe: Candle interval (1m, 5m, 15m, 30m, 1h, 4h, 12h, 1d)
            limit: Maximum number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data indexed by timestamp
        """
        # Fetches historical OHLCV candlestick data and returns a pandas DataFrame with timestamp index and numeric columns
        try:
            ohlcv_data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(
                data=ohlcv_data,
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.set_index("timestamp").sort_index()
            
            numeric_cols = ["open", "high", "low", "close", "volume"]
            df[numeric_cols] = df[numeric_cols].astype(float)
            
            return df
        except Exception as e:
            raise Exception(f"Failed to fetch OHLCV data: {str(e)}")
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for a symbol.
        
        Args:
            symbol: Trading pair symbol
            leverage: Leverage multiplier (1-50)
            
        Returns:
            True if successful
        """
        # Sets leverage multiplier (1-50x) for a specific trading pair
        try:
            self.exchange.set_leverage(leverage, symbol)
            return True
        except Exception as e:
            raise Exception(f"Failed to set leverage: {str(e)}")

    def set_margin_mode(self, symbol: str, margin_mode: str, leverage: int) -> bool:
        """Set margin mode for a symbol.
        
        Args:
            symbol: Trading pair symbol
            margin_mode: "isolated" or "cross"
            leverage: Required leverage multiplier for Hyperliquid
            
        Returns:
            True if successful
        """
        # Configures margin mode ("isolated" or "cross") with required leverage parameter
        try:
            self.exchange.set_margin_mode(margin_mode, symbol, params={"leverage": leverage})
            return True
        except Exception as e:
            raise Exception(f"Failed to set margin mode: {str(e)}")

    def place_market_order(
        self, 
        symbol: str, 
        side: str, 
        amount: float,
        reduce_only: bool = False,
        take_profit_price: float = None,
        stop_loss_price: float = None
    ) -> dict:
        """Place a market order with optional take profit and stop loss.
        
        Args:
            symbol: Trading pair symbol
            side: "buy" or "sell"
            amount: Order size in contracts
            reduce_only: If True, order will only reduce position size
            take_profit_price: Optional price level to take profit
            stop_loss_price: Optional price level to stop loss
            
        Returns:
            Order execution details
        """
        # Places market orders with optional take-profit and stop-loss levels. Formats amounts/prices and handles order chaining for TP/SL
        try:
            formatted_amount = self._amount_to_precision(symbol, amount)
            
            price = self.get_current_price(symbol)
            formatted_price = self._price_to_precision(symbol, price)
            
            params = {"reduceOnly": reduce_only}
            
            if take_profit_price is not None:
                formatted_tp_price = self._price_to_precision(symbol, take_profit_price)
                params["takeProfitPrice"] = formatted_tp_price
                
            if stop_loss_price is not None:
                formatted_sl_price = self._price_to_precision(symbol, stop_loss_price)
                params["stopLossPrice"] = formatted_sl_price
            
            order_info = {}
            order_info_final = {}
            
            order_info["market_order"] = self.exchange.create_order(
                symbol=symbol,
                type="market",
                side=side,
                amount=formatted_amount,
                price=formatted_price,
                params=params
            )
            order_info_final["market_order"] = order_info["market_order"]["info"]
            
            if take_profit_price is not None:
                order_info["take_profit_order"] = self._place_take_profit_order(symbol, side, formatted_amount, formatted_price, take_profit_price)
                order_info_final["take_profit_order"] = order_info["take_profit_order"]["info"]
                
            if stop_loss_price is not None:
                order_info["stop_loss_order"] = self._place_stop_loss_order(symbol, side, formatted_amount, formatted_price, stop_loss_price)
                order_info_final["stop_loss_order"] = order_info["stop_loss_order"]["info"]
            
            return order_info_final
        except Exception as e:
            raise Exception(f"Failed to place market order: {str(e)}")

    def place_limit_order(
        self,
        symbol: str,
        side: str, 
        amount: float,
        price: float,
        reduce_only: bool = False
    ) -> dict:
        """Place a limit order.
        
        Args:
            symbol: Trading pair symbol
            side: "buy" or "sell"
            amount: Order size in contracts  
            price: Limit price
            reduce_only: If True, order will only reduce position size
            
        Returns:
            Order details
        """
        # Places limit orders at specific price levels with reduce-only option support
        try:
            formatted_amount = self._amount_to_precision(symbol, amount)
            formatted_price = self._price_to_precision(symbol, price)
            
            params = {"reduceOnly": reduce_only}
            
            order = self.exchange.create_order(
                symbol=symbol,
                type="limit",
                side=side,
                amount=formatted_amount,
                price=formatted_price,
                params=params
            )
            
            return order["info"]
        except Exception as e:
            raise Exception(f"Failed to place limit order: {str(e)}")

    def place_usd_market_order(
        self,
        symbol: str,
        side: str,
        usd_amount: float,
        reduce_only: bool = False,
        take_profit_price: float = None,
        stop_loss_price: float = None
    ) -> dict:
        """Place a market order using USD amount instead of contract amount.
        
        Args:
            symbol: Trading pair symbol
            side: "buy" or "sell" 
            usd_amount: Order size in USD value
            reduce_only: If True, order will only reduce position size
            take_profit_price: Optional price level to take profit
            stop_loss_price: Optional price level to stop loss
            
        Returns:
            Order execution details
        """
        # Convenience function to place market orders using USD amounts instead of contract quantities - automatically converts based on current price
        try:
            current_price = self.get_current_price(symbol)
            contract_amount = usd_amount / current_price
            
            return self.place_market_order(
                symbol=symbol,
                side=side,
                amount=contract_amount,
                reduce_only=reduce_only,
                take_profit_price=take_profit_price,
                stop_loss_price=stop_loss_price
            )
        except Exception as e:
            raise Exception(f"Failed to place USD market order: {str(e)}")

    def _place_take_profit_order(self, symbol: str, side: str, amount: float, price: float, take_profit_price: float) -> dict:
        """Internal method to place a take-profit order."""
        # Internal helper to create take-profit orders with opposite side and reduce-only flag
        tp_price = self._price_to_precision(symbol, take_profit_price)
        close_side = "sell" if side == "buy" else "buy"
        return self.exchange.create_order(
                symbol=symbol,
                type="market",
                side=close_side,
                amount=amount,
                price=price,
                params={"takeProfitPrice": tp_price, "reduceOnly": True},
            )

    def _place_stop_loss_order(self, symbol: str, side: str, amount: float, price: float, stop_loss_price: float) -> dict:
        """Internal method to place a stop-loss order."""
        # Internal helper to create stop-loss orders with opposite side and reduce-only flag
        sl_price = self._price_to_precision(symbol, stop_loss_price)
        close_side = "sell" if side == "buy" else "buy"
        return self.exchange.create_order(
                symbol=symbol,
                type="market",
                side=close_side,
                amount=amount,
                price=price,
                params={"stopLossPrice": sl_price, "reduceOnly": True},
            )


# Utility function for printing with verbosity control
def my_print(message: str, verbose: bool = True):
    """Print message if verbose is True."""
    # Simple print function with verbosity control for conditional logging
    if verbose:
        print(message)


if __name__ == "__main__":
    # Simple test of the client
    try:
        # You'll need to provide credentials for testing
        wallet_address = os.getenv('HYPERLIQUID_WALLET_ADDRESS')
        private_key = os.getenv('HYPERLIQUID_PRIVATE_KEY')
        
        if wallet_address and private_key:
            client = HyperliquidClient(wallet_address, private_key)
            balance = client.fetch_balance()
            print(f"Account Balance: {balance['total']['USDC']} USDC")
            
            btc_price = client.get_current_price("BTC/USDC:USDC")
            print(f"BTC Price: ${btc_price}")
        else:
            print("Please set HYPERLIQUID_WALLET_ADDRESS and HYPERLIQUID_PRIVATE_KEY in .env for testing")
        
    except Exception as e:
        print(f"Test failed: {e}")