#!/usr/bin/env python3
"""
Simple data download script for CTA project
Usage: python download_data.py <start_date> <end_date> [interval] [format]
Examples:
  python download_data.py 2024-01-01 2024-06-01              # 1h data, JSON format
  python download_data.py 2024-01-01 2024-01-31 10m          # 10m data, JSON format
  python download_data.py 2024-01-01 2024-12-31 24h csv      # Daily data, CSV format
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from api import GlassnodeAPI

def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid date format: {date_str}. Use YYYY-MM-DD")
        return None

def main():
    # Check required arguments
    if len(sys.argv) < 3:
        print("Error: start_date and end_date are required")
        print("Usage: python download_data.py <start_date> <end_date> [interval] [format]")
        print("Example: python download_data.py 2024-01-01 2024-06-01 1h json")
        return
    
    # Load API key
    load_dotenv()
    api_key = os.getenv('GLASSNODE_APIKEY')
    
    if not api_key:
        print("Error: GLASSNODE_APIKEY not found in .env file")
        return
    
    # Parse command line arguments
    start_date_str = sys.argv[1]
    end_date_str = sys.argv[2]
    interval = sys.argv[3] if len(sys.argv) > 3 else '1h'
    format_type = sys.argv[4] if len(sys.argv) > 4 else 'json'
    
    # Parse dates
    start_time = parse_date(start_date_str)
    end_time = parse_date(end_date_str)
    
    if start_time is None or end_time is None:
        return
    
    # Validate inputs
    api = GlassnodeAPI(api_key)
    valid_intervals = api.get_available_intervals()
    if interval not in valid_intervals:
        print(f"Invalid interval: {interval}. Use: {', '.join(valid_intervals)}")
        return
    
    if format_type not in ['json', 'csv']:
        print(f"Invalid format: {format_type}. Use: json or csv")
        return
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate filename with path
    filename = os.path.join(data_dir, f"btc_{interval}_{start_date_str}_{end_date_str}.csv")
    
    # Show what we're downloading
    print(f"Downloading BTC {interval} data from {start_date_str} to {end_date_str}")
    print(f"API Format: {format_type}, Output: {filename}")
    
    # Download data
    df = api.fetch_btc_data(
        start_time=start_time,
        end_time=end_time,
        interval=interval,
        save_file=filename,
        format=format_type
    )
    
    if not df.empty:
        print(f"✅ Downloaded {len(df)} records to {filename}")
        print(f"Date range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
        print(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    else:
        print("❌ Download failed")

if __name__ == '__main__':
    main()