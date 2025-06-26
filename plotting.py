import matplotlib.pyplot as plt

class Plotter:
    """
    Handles plotting of results and performance metrics.
    """
    def __init__(self):
        pass

    def plot_all(self, df, metrics):
        """
        Plot equity curve and print metrics.
        """
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['equity'], label='Equity Curve')
        plt.title('Equity Curve')
        plt.xlabel('Time')
        plt.ylabel('Equity')
        plt.legend()
        plt.grid(True)
        plt.show()
        print('Performance Metrics:')
        for k, v in metrics.items():
            print(f'{k}: {v}') 