from strategy import Strategy
from api import GlassnodeAPI
from analyzer import Analyzer
from backtest import Backtester
from plotting import Plotter
from dotenv import load_dotenv
import pandas as pd
import os
import glob

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

def main():
    """
    Main function to run the CTA Bitcoin strategy.
    """
    # Load data with selection prompt
    data = select_data_file()

    # Initialize strategy
    strategy = Strategy()
    signals = strategy.generate_signals(data)

    # Backtest
    backtester = Backtester()
    results = backtester.run_backtest(data, signals)
    
    # Analyze
    analyzer = Analyzer()
    metrics = analyzer.evaluate(results)

    # # Plot
    plotter = Plotter()
    plotter.plot_all(results, metrics)

    # Print metrics
    print('Performance Metrics:')
    for k, v in metrics.items():
        print(f'{k}: {v}')

if __name__ == '__main__':
    main()
