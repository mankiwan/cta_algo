import requests
import pandas as pd
from datetime import datetime, timedelta

class GlassnodeAPI:
    """
    Handles fetching data from Glassnode API.
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.glassnode.com/v1/metrics/market/price_usd_ohlc'

    def fetch_btc_data(self, start_time, end_time, interval='1h', 
                      save_file='test_data.csv', format='json'):
        """
        Fetch Bitcoin price data from Glassnode API and return as DataFrame.
        
        Args:
            interval: Data interval ('10m', '1h', '24h', '1w', '1month')
            start_time: Start time (datetime object or unix timestamp) - REQUIRED
            end_time: End time (datetime object or unix timestamp) - REQUIRED
            save_file: Output CSV filename
            format: Response format ('json' or 'csv')
        """
        if start_time is None or end_time is None:
            raise ValueError("start_time and end_time are required parameters")
        
        # Convert to datetime objects if needed
        start_dt = datetime.fromtimestamp(start_time) if isinstance(start_time, (int, float)) else start_time
        end_dt = datetime.fromtimestamp(end_time) if isinstance(end_time, (int, float)) else end_time
        
        start_timestamp = int(start_dt.timestamp())
        end_timestamp = int(end_dt.timestamp())
        
        params = {
            'a': 'BTC',
            'api_key': self.api_key,
            'i': interval,
            # 's': start_timestamp,
            # 'u': end_timestamp,
            'f': format
        }
        
        print(f"Fetching BTC data: {interval} interval")
        print(f"Period: {start_dt.date()} to {end_dt.date()}")
        print(f"Format: {format}")
        
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            if format == 'csv':
                # Handle CSV response from API
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                
                # Handle different CSV column formats
                if 't' in df.columns and 'v' in df.columns:
                    # Old format: timestamp, value
                    df = df.rename(columns={'t': 'timestamp', 'v': 'close'})
                elif 't' in df.columns and any(col in df.columns for col in ['o', 'h', 'l', 'c']):
                    # New format: timestamp, open, high, low, close
                    column_mapping = {'t': 'timestamp'}
                    if 'o' in df.columns:
                        column_mapping['o'] = 'open'
                    if 'h' in df.columns:
                        column_mapping['h'] = 'high' 
                    if 'l' in df.columns:
                        column_mapping['l'] = 'low'
                    if 'c' in df.columns:
                        column_mapping['c'] = 'close'
                    df = df.rename(columns=column_mapping)
                    
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                
            else:
                # Handle JSON response with new data structure
                # Format: [{"t": 1279407600, "o": {"c": 0.04951, "h": 0.04951, "l": 0.04951, "o": 0.04951}}, ...]
                data = response.json()
                if not data:
                    print('No data returned from API')
                    return pd.DataFrame()
                
                # Parse new data structure
                parsed_data = []
                for item in data:
                    if 't' in item and 'o' in item:
                        ohlc = item['o']
                        parsed_data.append({
                            'timestamp': item['t'],
                            'open': ohlc.get('o', 0),
                            'high': ohlc.get('h', 0), 
                            'low': ohlc.get('l', 0),
                            'close': ohlc.get('c', 0)
                        })
                
                if not parsed_data:
                    print('No valid OHLC data found in response')
                    return pd.DataFrame()
                    
                df = pd.DataFrame(parsed_data)
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Ensure we have all required columns for strategy
            required_columns = ['timestamp', 'open', 'high', 'low', 'close']
            for col in required_columns:
                if col not in df.columns:
                    if col != 'timestamp':  # Fill missing OHLC with close price
                        df[col] = df.get('close', 0)
            
            # Reorder columns for consistency
            available_columns = [col for col in required_columns if col in df.columns]
            df = df[available_columns]
            
            # Save to file regardless of API format
            if save_file:
                df.to_csv(save_file, index=False)
                print(f"Data saved to {save_file} ({len(df)} records)")
            
            return df
            
        else:
            print(f'Failed to fetch data from Glassnode: {response.status_code}')
            print(f'Response: {response.text}')
            return pd.DataFrame()
    
    def get_available_intervals(self):
        """Return available data intervals"""
        return ['10m', '1h', '24h', '1w', '1month'] 