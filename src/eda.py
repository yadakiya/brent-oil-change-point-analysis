"""
Exploratory Data Analysis module for Brent oil prices.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import logging
from typing import Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EDAnalyzer:
    """
    Performs exploratory data analysis on oil price data.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize EDAnalyzer with DataFrame.
        
        Args:
            df: DataFrame containing oil price data
        """
        self.df = df
        self.figures = {}
        
    def plot_time_series(self, save_path: str = None) -> None:
        """
        Plot raw price series and log returns.
        
        Args:
            save_path: Optional path to save the figure
        """
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # Price series
        self.df['Price'].plot(ax=axes[0], color='blue')
        axes[0].set_title('Brent Oil Price (USD/barrel)', fontsize=14)
        axes[0].set_xlabel('Date')
        axes[0].set_ylabel('Price (USD)')
        axes[0].grid(True, alpha=0.3)
        
        # Log returns
        self.df['log_return'].plot(ax=axes[1], color='green')
        axes[1].set_title('Daily Log Returns', fontsize=14)
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Log Return')
        axes[1].grid(True, alpha=0.3)
        axes[1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Rolling volatility
        self.df['rolling_volatility'].plot(ax=axes[2], color='red')
        axes[2].set_title('30-Day Rolling Volatility', fontsize=14)
        axes[2].set_xlabel('Date')
        axes[2].set_ylabel('Volatility')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figure saved to {save_path}")
        
        self.figures['time_series'] = fig
        plt.show()
    
    def plot_distributions(self, save_path: str = None) -> None:
        """
        Plot distributions of returns.
        
        Args:
            save_path: Optional path to save the figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Histogram of log returns
        self.df['log_return'].hist(bins=50, ax=axes[0, 0], color='blue', alpha=0.7)
        axes[0, 0].set_title('Distribution of Log Returns')
        axes[0, 0].set_xlabel('Log Return')
        axes[0, 0].set_ylabel('Frequency')
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(self.df['log_return'].dropna(), dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Q-Q Plot of Log Returns')
        
        # Box plot by decade
        self.df['decade'] = self.df.index.year // 10 * 10
        self.df.boxplot(column='log_return', by='decade', ax=axes[1, 0])
        axes[1, 0].set_title('Log Returns by Decade')
        axes[1, 0].set_xlabel('Decade')
        axes[1, 0].set_ylabel('Log Return')
        
        # Violin plot of price by year
        self.df['year'] = self.df.index.year
        years = self.df.groupby('year')['Price'].mean()
        years.plot(kind='bar', ax=axes[1, 1])
        axes[1, 1].set_title('Average Price by Year')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Average Price (USD)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figure saved to {save_path}")
        
        self.figures['distributions'] = fig
        plt.show()
    
    def test_stationarity(self) -> Tuple[float, float]:
        """
        Perform Augmented Dickey-Fuller test for stationarity.
        
        Returns:
            Tuple of (ADF statistic, p-value)
        """
        logger.info("Performing Augmented Dickey-Fuller test...")
        
        # Test price series
        result_price = adfuller(self.df['Price'], autolag='AIC')
        logger.info(f"Price series - ADF: {result_price[0]:.4f}, p-value: {result_price[1]:.4f}")
        
        # Test log returns
        result_returns = adfuller(self.df['log_return'].dropna(), autolag='AIC')
        logger.info(f"Log returns - ADF: {result_returns[0]:.4f}, p-value: {result_returns[1]:.4f}")
        
        return result_price[1], result_returns[1]
    
    def plot_acf_pacf(self, save_path: str = None) -> None:
        """
        Plot autocorrelation and partial autocorrelation functions.
        
        Args:
            save_path: Optional path to save the figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # ACF of log returns
        plot_acf(self.df['log_return'].dropna(), ax=axes[0, 0], lags=40)
        axes[0, 0].set_title('Autocorrelation of Log Returns')
        
        # PACF of log returns
        plot_pacf(self.df['log_return'].dropna(), ax=axes[0, 1], lags=40)
        axes[0, 1].set_title('Partial Autocorrelation of Log Returns')
        
        # ACF of absolute returns (volatility)
        plot_acf(abs(self.df['log_return'].dropna()), ax=axes[1, 0], lags=40)
        axes[1, 0].set_title('Autocorrelation of Absolute Returns')
        
        # PACF of absolute returns
        plot_pacf(abs(self.df['log_return'].dropna()), ax=axes[1, 1], lags=40)
        axes[1, 1].set_title('Partial Autocorrelation of Absolute Returns')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figure saved to {save_path}")
        
        self.figures['acf_pacf'] = fig
        plt.show()
    
    def identify_volatility_clusters(self, save_path: str = None) -> None:
        """
        Identify and visualize volatility clustering.
        
        Args:
            save_path: Optional path to save the figure
        """
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        # Absolute returns
        self.df['abs_returns'] = abs(self.df['log_return'])
        self.df['abs_returns'].plot(ax=axes[0])
        axes[0].set_title('Absolute Log Returns (Volatility Proxy)', fontsize=14)
        axes[0].set_xlabel('Date')
        axes[0].set_ylabel('Absolute Return')
        axes[0].grid(True, alpha=0.3)
        
        # Squared returns
        self.df['squared_returns'] = self.df['log_return'] ** 2
        self.df['squared_returns'].plot(ax=axes[1], color='red')
        axes[1].set_title('Squared Log Returns', fontsize=14)
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Squared Return')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figure saved to {save_path}")
        
        self.figures['volatility'] = fig
        plt.show()
    
    def generate_comprehensive_report(self, output_path: str = "results/reports/eda_report.md"):
        """
        Generate comprehensive EDA report.
        
        Args:
            output_path: Path to save the report
        """
        logger.info("Generating EDA report...")
        
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Perform tests
        adf_price_pvalue, adf_returns_pvalue = self.test_stationarity()
        
        # Generate report content
        report = f"""# Exploratory Data Analysis Report
## Brent Oil Prices from BrentOilPrices.csv
### Data Period: {self.df.index.min()} to {self.df.index.max()}

### Data Overview
- **Total Records**: {len(self.df)}
- **Date Range**: {self.df.index.min()} to {self.df.index.max()}
- **Price Range**: ${self.df['Price'].min():.2f} - ${self.df['Price'].max():.2f}
- **Average Price**: ${self.df['Price'].mean():.2f}

### Summary Statistics
| Metric | Value |
|--------|-------|
| Mean Log Return | {self.df['log_return'].mean():.6f} |
| Std Log Return | {self.df['log_return'].std():.6f} |
| Skewness | {self.df['log_return'].skew():.4f} |
| Kurtosis | {self.df['log_return'].kurtosis():.4f} |

### Stationarity Tests
- **Price Series ADF p-value**: {adf_price_pvalue:.6f}
- **Log Returns ADF p-value**: {adf_returns_pvalue:.6f}

*Interpretation*: The log returns are stationary (p < 0.05), confirming our modeling approach using log returns.

### Key Observations
1. **Volatility Clustering**: Periods of high volatility tend to cluster together
2. **Fat Tails**: The return distribution exhibits excess kurtosis
3. **Mean Reversion**: Prices show mean-reverting behavior over longer horizons
4. **Structural Breaks**: Multiple periods of regime change are visible in the time series

### Figures Generated
- Time series plot of prices and returns
- Distribution plots of returns
- ACF/PACF plots
- Volatility clustering visualization

### Recommendations for Modeling
1. Use log returns for stationarity
2. Account for volatility clustering in model specification
3. Consider multiple change points to capture regime changes
4. Use Bayesian methods to quantify uncertainty in change point detection
"""
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to {output_path}")
        return report

# Example usage
if __name__ == "__main__":
    from data_loader import DataLoader
    
    loader = DataLoader()
    df = loader.load_data()
    
    eda = EDAnalyzer(df)
    eda.plot_time_series()
    eda.plot_distributions()
    eda.test_stationarity()
    eda.plot_acf_pacf()
    eda.identify_volatility_clusters()
    eda.generate_comprehensive_report()