import pandas as pd
import numpy as np
from itertools import product


class Optimizer:
    def __init__(self, strategy_instance, backtester):
        self.strategy = strategy_instance
        self.backtester = backtester
    
    def optimize_parameters(self, param_ranges, metric='sharpe'):
        """
        Optimize strategy parameters using grid search
        
        Args:
            param_ranges: dict with parameter ranges
                e.g., {'window': (10, 60, 5), 'threshold': (1.0, 3.5, 0.25)}
            metric: optimization target ('sharpe', 'calmar', 'annual_return')
        
        Returns:
            DataFrame with optimization results
        """
        print(f"\n=== Optimizing Strategy Parameters ===")
        print(f"Target metric: {metric}")
        
        # Generate parameter combinations
        param_combinations = self._generate_param_combinations(param_ranges)
        print(f"Total combinations to test: {len(param_combinations)}")
        
        results = []
        
        for i, params in enumerate(param_combinations):
            if (i + 1) % 10 == 0 or i == 0:
                print(f"Progress: {i + 1}/{len(param_combinations)}")
            
            try:
                # Generate signals with current parameters
                df_signals = self.strategy.generate_signals(
                    window=params['window'],
                    threshold=params['threshold']
                )
                
                # Run full backtest using Backtester (includes data prep + metrics)
                df_backtest = self.backtester.run_backtest(df_signals, silent=True)
                
                # Extract metrics from backtest results
                metrics = self.backtester.calculate_metrics(df_backtest)
                
                # Store results
                result = {
                    'window': params['window'],
                    'threshold': params['threshold'],
                    **metrics
                }
                results.append(result)
                
            except Exception as e:
                print(f"Error with params {params}: {e}")
                continue
        
        # Convert to DataFrame and sort by target metric
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(metric, ascending=False)
        
        # Print top results
        print(f"\nTop 10 parameter combinations by {metric}:")
        display_cols = ['window', 'threshold', 'sharpe', 'annual_return', 'max_drawdown', 'calmar']
        print(results_df[display_cols].head(10).to_string(index=False))
        
        return results_df
    
    def _generate_param_combinations(self, param_ranges):
        """Generate all parameter combinations from ranges"""
        param_lists = {}
        
        for param, param_range in param_ranges.items():
            if isinstance(param_range, tuple) and len(param_range) == 3:
                # (start, stop, step) format
                start, stop, step = param_range
                param_lists[param] = np.arange(start, stop + step, step)
            elif isinstance(param_range, (list, tuple)):
                # List of values
                param_lists[param] = param_range
            else:
                # Single value
                param_lists[param] = [param_range]
        
        # Generate all combinations
        param_names = list(param_lists.keys())
        param_values = list(param_lists.values())
        
        combinations = []
        for combo in product(*param_values):
            combinations.append(dict(zip(param_names, combo)))
        
        return combinations
    
    def find_best_parameters(self, param_ranges, metric='sharpe'):
        """Find the best parameters for a given metric"""
        results_df = self.optimize_parameters(param_ranges, metric)
        
        if len(results_df) == 0:
            return None
        
        best_params = results_df.iloc[0]
        
        print(f"\n=== Best Parameters (by {metric}) ===")
        print(f"Window: {best_params['window']}")
        print(f"Threshold: {best_params['threshold']}")
        print(f"Sharpe Ratio: {best_params['sharpe']:.3f}")
        print(f"Annual Return: {best_params['annual_return']:.2f}%")
        print(f"Max Drawdown: {best_params['max_drawdown']:.2f}%")
        print(f"Calmar Ratio: {best_params['calmar']:.3f}")
        
        return best_params
    
    def analyze_parameter_sensitivity(self, param_ranges, metric='sharpe'):
        """Analyze how sensitive the strategy is to parameter changes"""
        results_df = self.optimize_parameters(param_ranges, metric)
        
        if len(results_df) == 0:
            return None
        
        print(f"\n=== Parameter Sensitivity Analysis ===")
        
        # Analyze each parameter individually
        for param in ['window', 'threshold']:
            if param in results_df.columns:
                param_stats = results_df.groupby(param)[metric].agg(['mean', 'std', 'min', 'max'])
                print(f"\n{param.title()} sensitivity:")
                print(param_stats.round(3))
        
        # Overall statistics
        print(f"\nOverall {metric} statistics:")
        print(f"Mean: {results_df[metric].mean():.3f}")
        print(f"Std: {results_df[metric].std():.3f}")
        print(f"Min: {results_df[metric].min():.3f}")
        print(f"Max: {results_df[metric].max():.3f}")
        
        return results_df
    
    def walk_forward_optimization(self, param_ranges, window_months=6, step_months=1):
        """
        Perform walk-forward optimization
        
        Args:
            param_ranges: parameter ranges to optimize
            window_months: optimization window in months
            step_months: step size in months
        """
        print(f"\n=== Walk-Forward Optimization ===")
        print(f"Optimization window: {window_months} months")
        print(f"Step size: {step_months} months")
        
        # This is a placeholder for walk-forward optimization
        # Implementation would require more complex date handling
        print("Walk-forward optimization not implemented yet.")
        print("Use optimize_parameters() for static optimization.")
        
        return None