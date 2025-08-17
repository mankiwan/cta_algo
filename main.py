from strategy import Strategy
from strategy_v3 import Strategy3
from api import GlassnodeAPI
from backtest import Backtester
from plotting import Plotter
from dotenv import load_dotenv
import pandas as pd
import os
import glob
from datetime import datetime

# Load environment variables from .env file
load_dotenv()
GLASSNODE_APIKEY = os.getenv('GLASSNODE_APIKEY')

def select_data_file():
    """
    Prompt user to select a CSV file from data folder or fetch from Glassnode API.
    """
    # Check if data folder exists and has CSV files
    data_dir = "data"
    if os.path.exists(data_dir):
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        if csv_files:
            print("Available CSV files in data folder:")
            for i, file in enumerate(csv_files, 1):
                filename = os.path.basename(file)
                print(f"{i}: {filename}")
            
            print(f"{len(csv_files) + 1}: Fetch new data from Glassnode API")
            
            while True:
                try:
                    choice = int(input("Select an option: "))
                    if 1 <= choice <= len(csv_files):
                        selected_file = csv_files[choice - 1]
                        print(f"Loading data from {os.path.basename(selected_file)}...")
                        return pd.read_csv(selected_file, parse_dates=['timestamp'])
                    elif choice == len(csv_files) + 1:
                        break
                    else:
                        print(f"Invalid choice. Please enter 1-{len(csv_files) + 1}")
                except ValueError:
                    print("Please enter a valid number")
    
    # Fallback to API
    print('Fetching data from Glassnode API...')
    api = GlassnodeAPI(api_key=GLASSNODE_APIKEY)
    data = api.fetch_btc_data()
    data.to_csv('glassnode_data.csv', index=False)
    return data

def get_date_range():
    """Get date range for backtesting"""
    print("\n=== Date Range Selection ===")
    print("Data available from 2010-07-17 to 2025-7-22")
    
    while True:
        try:
            start_date_str = input("Enter start date (YYYY-MM-DD) or press Enter for 2020-01-01: ") or "2020-01-01"
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            
            # Validate start date
            min_date = datetime(2010, 7, 17)
            if start_date < min_date:
                print(f"Start date cannot be before 2010-07-17")
                continue
                
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
    
    while True:
        try:
            end_date_str = input("Enter end date (YYYY-MM-DD) or press Enter for 2025-07-21: ") or "2025-07-21"
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Validate end date
            if end_date <= start_date:
                print("End date must be after start date")
                continue
                
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
    
    return start_date, end_date

def get_user_preferences():
    """Get user preferences for backtesting"""
    print("\n=== Simple Backtesting Configuration ===")
    
    # Capital
    while True:
        try:
            capital = float(input("Enter initial capital ($): ") or "10000")
            if capital > 0:
                break
            else:
                print("Please enter a positive amount")
        except ValueError:
            print("Please enter a valid number")
    
    return capital

def filter_data_by_date_range(df, start_date, end_date):
    """Filter DataFrame by date range"""
    print(f"\n=== Filtering Data ===")
    print(f"Original data: {len(df)} records from {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
    
    # Filter by date range
    mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
    filtered_df = df[mask].copy().reset_index(drop=True)
    
    print(f"Filtered data: {len(filtered_df)} records from {filtered_df['timestamp'].min().date()} to {filtered_df['timestamp'].max().date()}")
    
    if len(filtered_df) == 0:
        print("Warning: No data found in the specified date range!")
        return df  # Return original data if no match
    
    return filtered_df

def main():
    """
    Main function to run the simple BBand and RSI strategy for Bitcoin.
    """
    # Load data with selection prompt
    data = select_data_file()
    
    # Prompt to get date range for backtesting
    # start_date, end_date = get_date_range()
    # Manual input to get data range
    start_date = datetime.strptime('2020-05-11', '%Y-%m-%d')
    end_date = datetime.strptime('2025-07-21', '%Y-%m-%d')

    # Filter data by selected date range
    data = filter_data_by_date_range(data, start_date, end_date)
    
    # Get user preferences
    # initial_capital = get_user_preferences()

    # Initialize strategy with data (generates buy/sell signals)
    # strategy = Strategy(data)  # Z-Score strategy
    strategy = Strategy3(data)  # RSI strategy

    # Backtest the strategy by editing manual params and generate metrics like Sharpe, Calmar, MDD, Annualized Return, Total Trades, Win Rate etc.
    # Plot the equity curve as well
    strategy.backtest()

    # Optimize the strategy by enter manual window and threshold range
    # Plot the heat map of sharpe for each combination
    # strategy.optimize(
    #     window=(10, 100, 10),
    #     threshold=(0, 2.5, 0.25),
    # )


if __name__ == '__main__':
    main()
