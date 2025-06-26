import requests
import pandas as pd

class GlassnodeAPI:
    """
    Handles fetching data from Glassnode API.
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.glassnode.com/v1/metrics/market/price_usd_close'

    def fetch_btc_data(self):
        """
        Fetch Bitcoin price data from Glassnode API and return as DataFrame.
        """
        params = {
            'a': 'BTC',
            'api_key': self.api_key,
            'i': '24h',
            's': '1609459200'  # Example: 2021-01-01
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df.columns = ['timestamp', 'close']
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.to_csv('test_data.csv', index=False)
            return df
        else:
            print('Failed to fetch data from Glassnode:', response.text)
            return pd.DataFrame() 