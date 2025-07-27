import pandas as pd
import numpy as np


class Analyzer:
    def __init__(self):
        pass
    
    def calculate_all_metrics(self, df):
        """Calculate all performance metrics for a backtest DataFrame"""
        # Ensure required columns exist
        if 'pnl' not in df.columns:
            df = self._prepare_data(df)
        
        pnl_series = df['pnl'].dropna()
        
        if len(pnl_series) == 0 or pnl_series.std() == 0:
            return self._get_empty_metrics()
        
        # Calculate all metrics
        metrics = {
            'total_return': self.calculate_total_return(df),
            'annual_return': self.calculate_annual_return(pnl_series),
            'sharpe': self.calculate_sharpe_ratio(pnl_series),
            'max_drawdown': self.calculate_max_drawdown(df),
            'calmar': self.calculate_calmar_ratio(pnl_series, df),
            'total_trades': self.calculate_total_trades(df),
            'win_rate': self.calculate_win_rate(df),
            'sortino': self.calculate_sortino_ratio(pnl_series),
            'profit_factor': self.calculate_profit_factor(df),
            'time_in_market': self.calculate_time_in_market(df),
            'avg_trade_duration': self.calculate_avg_trade_duration(df),
            'max_consecutive_losses': self.calculate_max_consecutive_losses(df),
            'recovery_time': self.calculate_recovery_time(df)
        }
        
        return metrics
    
    def calculate_total_return(self, df):
        """Calculate total return percentage"""
        if 'equity_curve' not in df.columns:
            df = self._prepare_data(df)
        
        if len(df) == 0:
            return 0.0
        
        total_return = (df['equity_curve'].iloc[-1] - 1) * 100
        return round(total_return, 2)
    
    def calculate_annual_return(self, pnl_series):
        """Calculate annualized return percentage"""
        if len(pnl_series) == 0:
            return 0.0
        
        annual_return = pnl_series.mean() * 365 * 100
        return round(annual_return, 2)
    
    def calculate_sharpe_ratio(self, pnl_series):
        """Calculate Sharpe ratio (annualized)"""
        if len(pnl_series) == 0 or pnl_series.std() == 0:
            return 0.0
        
        sharpe = pnl_series.mean() / pnl_series.std() * np.sqrt(365)
        return round(sharpe, 3)
    
    def calculate_max_drawdown(self, df):
        """Calculate maximum drawdown percentage"""
        if 'drawdown' not in df.columns:
            df = self._prepare_data(df)
        
        if len(df) == 0:
            return 0.0
        
        # Max drawdown is the most negative value (largest loss)
        max_drawdown = df['drawdown'].min() * 100
        return round(abs(max_drawdown), 2)
    
    def calculate_calmar_ratio(self, pnl_series, df):
        """Calculate Calmar ratio (Annual Return / Max Drawdown)"""
        annual_return = self.calculate_annual_return(pnl_series)
        max_drawdown = self.calculate_max_drawdown(df)
        
        if max_drawdown == 0 or max_drawdown < 0.01:
            return float('inf') if annual_return > 0 else 0.0
        
        calmar = annual_return / max_drawdown
        return round(calmar, 3)
    
    def calculate_total_trades(self, df):
        """Calculate total number of trades (position changes)"""
        if 'position' not in df.columns:
            return 0
        
        position_changes = df['position'].diff().fillna(0)
        total_trades = (position_changes != 0).sum()
        return int(total_trades)
    
    def calculate_win_rate(self, df):
        """Calculate win rate percentage"""
        if 'position' not in df.columns or 'pnl' not in df.columns:
            return 0.0
        
        trade_pnls = self._extract_trade_pnls(df)
        
        if len(trade_pnls) == 0:
            return 0.0
        
        win_rate = (np.array(trade_pnls) > 0).mean() * 100
        return round(win_rate, 2)
    
    def calculate_volatility(self, pnl_series):
        """Calculate annualized volatility"""
        if len(pnl_series) == 0:
            return 0.0
        
        volatility = pnl_series.std() * np.sqrt(365) * 100
        return round(volatility, 2)
    
    def calculate_sortino_ratio(self, pnl_series):
        """Calculate Sortino ratio (downside deviation)"""
        if len(pnl_series) == 0:
            return 0.0
        
        downside_returns = pnl_series[pnl_series < 0]
        
        if len(downside_returns) == 0:
            return 0.0
        
        downside_std = downside_returns.std()
        
        if downside_std == 0:
            return 0.0
        
        sortino = pnl_series.mean() / downside_std * np.sqrt(365)
        return round(sortino, 3)
    
    def calculate_profit_factor(self, df):
        """Calculate profit factor (gross profit / gross loss)"""
        trade_pnls = self._extract_trade_pnls(df)
        
        if len(trade_pnls) == 0:
            return 0.0
        
        gross_profit = sum([pnl for pnl in trade_pnls if pnl > 0])
        gross_loss = abs(sum([pnl for pnl in trade_pnls if pnl < 0]))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        profit_factor = gross_profit / gross_loss
        return round(profit_factor, 2)
    
    def calculate_average_trade(self, df):
        """Calculate average trade return"""
        trade_pnls = self._extract_trade_pnls(df)
        
        if len(trade_pnls) == 0:
            return 0.0
        
        avg_trade = np.mean(trade_pnls) * 100
        return round(avg_trade, 3)
    
    def calculate_recovery_factor(self, df):
        """Calculate recovery factor (Total Return / Max Drawdown)"""
        total_return = self.calculate_total_return(df)
        max_drawdown = self.calculate_max_drawdown(df)
        
        if max_drawdown == 0:
            return 0.0
        
        recovery_factor = total_return / max_drawdown
        return round(recovery_factor, 2)
    
    def _prepare_data(self, df):
        """Prepare DataFrame with required columns for analysis"""
        df = df.copy()
        
        # Calculate returns if not present
        if 'returns' not in df.columns:
            df['returns'] = df['close'].pct_change().fillna(0)
        
        # Calculate PnL if not present
        if 'pnl' not in df.columns:
            df['pnl'] = df['position'].shift(1) * df['returns']
        
        # Calculate equity curve if not present
        if 'equity_curve' not in df.columns:
            df['equity_curve'] = (1 + df['pnl']).cumprod()
        
        # Calculate drawdown if not present
        if 'drawdown' not in df.columns:
            df['running_max'] = df['equity_curve'].cummax()
            df['drawdown'] = (df['equity_curve'] - df['running_max']) / df['running_max']
        
        return df
    
    def _extract_trade_pnls(self, df):
        """Extract individual trade PnLs from position changes"""
        trade_pnls = []
        current_trade_pnl = 0
        in_trade = False
        
        for i, pos in enumerate(df['position']):
            if pos != 0 and not in_trade:
                # Entering a trade
                in_trade = True
                current_trade_pnl = 0
            elif pos != 0 and in_trade:
                # In a trade
                current_trade_pnl += df['pnl'].iloc[i]
            elif pos == 0 and in_trade:
                # Exiting a trade
                current_trade_pnl += df['pnl'].iloc[i]
                trade_pnls.append(current_trade_pnl)
                in_trade = False
                current_trade_pnl = 0
        
        return trade_pnls
    
    def _get_empty_metrics(self):
        """Return empty metrics dictionary"""
        return {
            'total_return': 0.0,
            'annual_return': 0.0,
            'sharpe': 0.0,
            'max_drawdown': 0.0,
            'calmar': 0.0,
            'total_trades': 0,
            'win_rate': 0.0,
            'sortino': 0.0,
            'profit_factor': 0.0,
            'time_in_market': 0.0,
            'avg_trade_duration': 0.0,
            'max_consecutive_losses': 0,
            'recovery_time': 0.0
        }
    
    def print_detailed_analysis(self, df):
        """Print comprehensive analysis report"""
        metrics = self.calculate_all_metrics(df)
        
        print(f"\n=== Detailed Performance Analysis ===")
        print(f"Total Return: {metrics['total_return']:.2f}%")
        print(f"Annualized Return: {metrics['annual_return']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe']:.3f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"Calmar Ratio: {metrics['calmar']:.3f}")
        
        # Additional metrics
        pnl_series = df['pnl'].dropna()
        print(f"Volatility: {self.calculate_volatility(pnl_series):.2f}%")
        print(f"Sortino Ratio: {self.calculate_sortino_ratio(pnl_series):.3f}")
        print(f"Profit Factor: {self.calculate_profit_factor(df):.2f}")
        print(f"Recovery Factor: {self.calculate_recovery_factor(df):.2f}")
        
        # Trading statistics
        print(f"\n=== Trading Statistics ===")
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print(f"Average Trade: {self.calculate_average_trade(df):.3f}%")
        
        # Data period
        if 'timestamp' in df.columns:
            print(f"\n=== Data Period ===")
            print(f"From: {df['timestamp'].min().date()}")
            print(f"To: {df['timestamp'].max().date()}")
            print(f"Total Days: {len(df)}")
        
        return metrics
    
    def calculate_time_in_market(self, df):
        """Calculate percentage of time strategy is invested vs cash"""
        if 'position' not in df.columns:
            return 0.0
        
        total_periods = len(df)
        invested_periods = (df['position'] != 0).sum()
        
        if total_periods == 0:
            return 0.0
            
        time_in_market = (invested_periods / total_periods) * 100
        return round(time_in_market, 2)
    
    def calculate_avg_trade_duration(self, df):
        """Calculate average trade duration in days"""
        if 'position' not in df.columns:
            return 0.0
        
        trade_durations = []
        current_duration = 0
        in_trade = False
        
        for pos in df['position']:
            if pos != 0 and not in_trade:
                # Entering a trade
                in_trade = True
                current_duration = 1
            elif pos != 0 and in_trade:
                # In a trade
                current_duration += 1
            elif pos == 0 and in_trade:
                # Exiting a trade
                trade_durations.append(current_duration)
                in_trade = False
                current_duration = 0
        
        # If still in trade at end
        if in_trade:
            trade_durations.append(current_duration)
        
        if len(trade_durations) == 0:
            return 0.0
        
        avg_duration = np.mean(trade_durations)
        return round(avg_duration, 1)
    
    def calculate_max_consecutive_losses(self, df):
        """Calculate maximum consecutive losing trades"""
        trade_pnls = self._extract_trade_pnls(df)
        
        if len(trade_pnls) == 0:
            return 0
        
        max_consecutive = 0
        current_consecutive = 0
        
        for pnl in trade_pnls:
            if pnl < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return int(max_consecutive)
    
    def calculate_recovery_time(self, df):
        """Calculate time (days) to recover from maximum drawdown"""
        if 'drawdown' not in df.columns or 'timestamp' not in df.columns:
            return 0.0
        
        # Find the point of maximum drawdown
        max_dd_idx = df['drawdown'].idxmin()
        
        # Find when drawdown returns to 0 (recovery)
        recovery_data = df.loc[max_dd_idx:].copy()
        recovery_idx = recovery_data[recovery_data['drawdown'] >= -0.001].index
        
        if len(recovery_idx) == 0:
            # Never recovered
            return float('inf')
        
        recovery_start = df.loc[max_dd_idx, 'timestamp']
        recovery_end = df.loc[recovery_idx[0], 'timestamp']
        
        recovery_days = (recovery_end - recovery_start).days
        return max(0, recovery_days)