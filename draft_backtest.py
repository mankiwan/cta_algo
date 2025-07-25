import csv
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv('GLASSNODE_APIKEY')

since = 1672502400  # 2023 Jan 1
until = 1735660800  # 2025 Jan 1
resolution = "24h"

res = requests.get("https://api.glassnode.com/v1/metrics/market/price_usd_close",
                   params={"a": "BTC", "s": since, "u": until, "api_key": API_KEY, "i": resolution})
df = pd.read_json(res.text, convert_dates=['t'])
df = df.rename(columns={'t': 'Date', 'v': 'price'})
df['chg'] = df['price'].pct_change().fillna(0)


def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def backtesting(bb_window, bb_sd_multiplier):
    df_test = df.copy()
    
    # Bollinger Bands
    df_test['bb_ma'] = df_test['price'].rolling(bb_window).mean()
    df_test['bb_std'] = df_test['price'].rolling(bb_window).std()
    df_test['bb_upper'] = df_test['bb_ma'] + (bb_sd_multiplier * df_test['bb_std'])
    df_test['bb_lower'] = df_test['bb_ma'] - (bb_sd_multiplier * df_test['bb_std'])
    
    # RSI (fixed 14-day window)
    df_test['rsi'] = calculate_rsi(df_test['price'], 14)
    
    # Trading signals
    df_test['pos'] = 0
    
    # Long signal: price touches lower band AND RSI < 30 (oversold)
    long_condition = (df_test['price'] <= df_test['bb_lower']) & (df_test['rsi'] < 30)
    df_test.loc[long_condition, 'pos'] = 1
    
    # Short signal: price touches upper band AND RSI > 70 (overbought)
    short_condition = (df_test['price'] >= df_test['bb_upper']) & (df_test['rsi'] > 70)
    df_test.loc[short_condition, 'pos'] = -1
    
    # Exit when price returns to middle band
    exit_condition = (df_test['price'] <= df_test['bb_ma']) & (df_test['pos'].shift(1) == -1)
    df_test.loc[exit_condition, 'pos'] = 0
    
    exit_condition_long = (df_test['price'] >= df_test['bb_ma']) & (df_test['pos'].shift(1) == 1)
    df_test.loc[exit_condition_long, 'pos'] = 0
    
    # Forward fill positions (hold until exit signal)
    df_test['pos'] = df_test['pos'].replace(0, np.nan).fillna(method='ffill').fillna(0)
    
    # PnL calculation
    df_test['pnl'] = df_test['pos'].shift(1) * df_test['chg']
    df_test['cumu'] = df_test['pnl'].cumsum()
    df_test['dd'] = df_test['cumu'].cummax() - df_test['cumu']
    
    # Performance metrics
    ar = round(df_test['pnl'].mean() * 365, 3)
    sr = round(df_test['pnl'].mean() / df_test['pnl'].std() * np.sqrt(365), 3) if df_test['pnl'].std() != 0 else 0
    mdd = df_test['dd'].max()
    cr = round(ar / mdd, 3) if mdd != 0 else 0
    
    return pd.Series([bb_window, bb_sd_multiplier, sr, ar, mdd, cr], 
                     index=['bb_window', 'bb_sd_multiplier', 'sr', 'ar', 'mdd', 'cr'])


# Parameter ranges for optimization - Simplified
bb_window_list = np.arange(10, 60, 5)  # BB window: 10,15,20,25,30,35,40,45,50,55
bb_sd_list = np.arange(1.0, 3.5, 0.25)  # SD multiplier: 1.0,1.25,1.5,1.75,2.0,2.25,2.5,2.75,3.0,3.25

result_list = []

for bb_window in bb_window_list:
    for bb_sd in bb_sd_list:
        result_list.append(backtesting(bb_window, bb_sd))

result_df = pd.DataFrame(result_list)
result_df = result_df.sort_values(by='sr', ascending=False)
print('Best parameters by Sharpe Ratio:')
print(result_df.head(10))

# Create heatmap for BB window vs SD multiplier
data_table = result_df.pivot(index='bb_window', columns='bb_sd_multiplier', values='sr')
print('\nHeatmap data (Sharpe Ratio):')
print(data_table)

plt.figure(figsize=(12, 8))
sns.heatmap(data_table, cmap='RdYlGn', annot=True, fmt='.3f')
plt.title('Bollinger Bands + RSI Strategy Optimization\nRSI Filter: Long when RSI<30, Short when RSI>70')
plt.xlabel('Bollinger Bands SD Multiplier')
plt.ylabel('Bollinger Bands Window')
plt.show()