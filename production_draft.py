import ccxt
import time
import pandas as pd
import numpy as np
import datetime
from pprint import pprint

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
})

markets = exchange.load_markets()
symbol = 'BTCUSDT'
market = exchange.market(symbol)

### trade ###
def trade(signal):

    ### get account info before trade ###
    net_pos = current_pos()

    target_pos = max_pos * signal  # target_pos == 要買賣到幾多粒btc
    print('target_pos', target_pos)
    bet_size = round(target_pos - net_pos, 3)
    print('bet_size', bet_size)

    ### trade ###
    if target_pos > net_pos:
            print('long ed')
            # exchange.create_order('BTCUSDT', 'market', 'buy', bet_size, None)
            # time.sleep(1)
            # order = exchange.fetch_my_trades('BTCUSDT')
            # pprint(order[-1])
            # message = order[-1]
            # requests.get(base_url + message)

    elif target_pos < net_pos:
            print('short ed')
            # exchange.create_order('BTCUSDT', 'market', 'sell', abs(bet_size), None)
            # time.sleep(1)
            # order = exchange.fetch_my_trades('BTCUSDT')
            # pprint(order[-1])
            # message = order[-1]
            # requests.get(base_url + message)

    time.sleep(1)

    ### get account info after trade ###
    net_pos = current_pos()
    print('after signal')
    print('current_pos', net_pos)
    print('nav', datetime.datetime.now(), exchange.fetch_balance()['USDT']['total'])
    print('**********')

def current_pos():
    net_pos = 0

    if exchange.fetchPosition(symbol)['info']['side'] == 'Buy':
        net_pos = float(exchange.fetchPosition(symbol)['info']['size'])

    elif exchange.fetchPosition(symbol)['info']['side'] == 'Sell':
        net_pos = -1 * float(exchange.fetchPosition(symbol)['info']['size'])

    return net_pos

### define variables ###
pos = 0
max_pos = 0.002  # max amount of btc

while True:
    if datetime.datetime.now().second == 10:

        df = pd.read_csv(r'C:\Users\jarvi\Desktop\production_2\signal.csv')
        signal = df['pos'].iloc[-1] ### read the last row
        print('signal_from_csv', signal)

        trade(signal)

    time.sleep(1)
