from strategy import Strategy
from api import GlassnodeAPI
from analyzer import Analyzer
from backtest import Backtester
from plotting import Plotter
from dotenv import load_dotenv
import pandas as pd
import os

# Load environment variables from .env file
load_dotenv()
GLASSNODE_APIKEY = os.getenv('GLASSNODE_APIKEY')

def main():
    """
    Main function to run the CTA Bitcoin strategy.
    """
    # Load data (from API or test_data.csv)
    if os.path.exists('test_data.csv'):
        print('Loading test data...')
        data = pd.read_csv('test_data.csv', parse_dates=['timestamp'])
    else:
        print('Fetching data from Glassnode API...')
        api = GlassnodeAPI(api_key=GLASSNODE_APIKEY)
        data = api.fetch_btc_data()
        data.to_csv('test_data.csv', index=False)

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
