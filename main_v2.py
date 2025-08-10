from strategy import Strategy
from strategy_v2 import StrategyV2
from api import GlassnodeAPI
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
    Compare V1 and V2 strategies
    """
    print("=== Bitcoin Z-Score Strategy Comparison: V1 vs V2 ===")
    
    # Load data
    data = select_data_file()
    
    # Set date range for testing
    start_date = datetime.strptime('2020-05-11', '%Y-%m-%d')
    end_date = datetime.strptime('2024-12-01', '%Y-%m-%d')
    data = filter_data_by_date_range(data, start_date, end_date)
    
    # Initialize both strategies
    strategy_v1 = Strategy(data)
    strategy_v2 = StrategyV2(data, transaction_cost=0.001, position_size=0.25)
    
    # Compare strategies side by side
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)
    
    # Test parameters
    window = 40
    threshold = 1.75
    
    print(f"\nTesting with: MA Window={window}, Threshold={threshold}")
    
    # Run V1 Strategy (Original)
    print("\n" + "-"*30 + " V1 RESULTS " + "-"*30)
    results_v1 = strategy_v1.backtest(window=window, threshold=threshold)
    
    # Run V2 Strategy (Advanced)
    print("\n" + "-"*30 + " V2 RESULTS " + "-"*30)
    results_v2 = strategy_v2.backtest(window=window, threshold=threshold, use_trend_filter=True)
    
    # Show comparison
    print("\n" + "="*60)
    print("STRATEGY LOGIC COMPARISON")
    print("="*60)
    strategy_v2.compare_with_v1(window=window, threshold=threshold)
    
    # Optional: Run optimization on V2
    optimize_choice = input("\nRun V2 parameter optimization? (y/n): ").lower()
    if optimize_choice == 'y':
        print("\n" + "-"*30 + " V2 OPTIMIZATION " + "-"*30)
        strategy_v2.optimize(
            window=(20, 80, 10),
            threshold=(0.5, 2.5, 0.25),
            metric='sharpe'
        )

if __name__ == '__main__':
    main()