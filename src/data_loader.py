"""
Data loading and preprocessing module for Brent oil price analysis.
Data file: BrentOilPrices.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    Handles loading and preprocessing of Brent oil price data from BrentOilPrices.csv.
    """
    
    def __init__(self, data_path: str = "data/raw/BrentOilPrices.csv"):
        """
        Initialize DataLoader with path to CSV file.
        
        Args:
            data_path: Path to the raw data CSV file (default: BrentOilPrices.csv)
        """
        self.data_path = Path(data_path)
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Load Brent oil prices from BrentOilPrices.csv file.
        
        Returns:
            DataFrame with processed price data
        """
        logger.info(f"Loading data from {self.data_path}")
        
        try:
            # Try different date formats that might be in BrentOilPrices.csv
            self.df = pd.read_csv(self.data_path)
            logger.info(f"Successfully loaded {len(self.df)} records")
        except FileNotFoundError:
            logger.error(f"Data file not found at {self.data_path}")
            raise
        
        return self._preprocess_data()
    
    def _preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the loaded data from BrentOilPrices.csv.
        
        Returns:
            Preprocessed DataFrame
        """
        # The BrentOilPrices.csv might have different column names
        # Common formats: 'Date', 'date', 'Price', 'price'
        
        # Find the date column
        date_col = None
        for col in self.df.columns:
            if col.lower() in ['date', 'day', 'datetime']:
                date_col = col
                break
        
        if date_col is None:
            # Try to guess the first column as date
            date_col = self.df.columns[0]
            logger.warning(f"No date column found. Using '{date_col}' as date.")
        
        # Find the price column
        price_col = None
        for col in self.df.columns:
            if col.lower() in ['price', 'brent', 'oil', 'value']:
                price_col = col
                break
        
        if price_col is None:
            # Try the second column as price
            price_col = self.df.columns[1]
            logger.warning(f"No price column found. Using '{price_col}' as price.")
        
        # Convert Date column to datetime - try multiple formats
        try:
            self.df[date_col] = pd.to_datetime(self.df[date_col], format='%d-%b-%y')
        except:
            try:
                self.df[date_col] = pd.to_datetime(self.df[date_col], format='%Y-%m-%d')
            except:
                try:
                    self.df[date_col] = pd.to_datetime(self.df[date_col])
                except:
                    logger.error("Could not parse dates. Please check the date format.")
                    raise
        
        # Set date as index
        self.df.set_index(date_col, inplace=True)
        self.df.sort_index(inplace=True)
        
        # Rename price column to 'Price' for consistency
        if price_col != 'Price':
            self.df.rename(columns={price_col: 'Price'}, inplace=True)
        
        # Check for missing values
        missing = self.df['Price'].isnull().sum()
        if missing > 0:
            logger.warning(f"Found {missing} missing values in Price column")
            self.df = self.df.dropna(subset=['Price'])
        
        # Calculate log returns
        self.df['log_return'] = np.log(self.df['Price']) - np.log(self.df['Price'].shift(1))
        self.df['returns'] = self.df['Price'].pct_change()
        
        # Calculate rolling statistics
        self.df['rolling_volatility'] = self.df['log_return'].rolling(30).std()
        self.df['rolling_mean'] = self.df['Price'].rolling(30).mean()
        self.df['rolling_std'] = self.df['Price'].rolling(30).std()
        
        # Drop NA from rolling calculations
        self.df = self.df.dropna()
        
        logger.info(f"Preprocessed {len(self.df)} records")
        logger.info(f"Date range: {self.df.index.min()} to {self.df.index.max()}")
        logger.info(f"Price range: ${self.df['Price'].min():.2f} to ${self.df['Price'].max():.2f}")
        
        return self.df
    
    def get_log_returns(self) -> np.ndarray:
        """
        Extract log returns for modeling.
        
        Returns:
            Array of log returns
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return self.df['log_return'].values
    
    def get_prices(self) -> np.ndarray:
        """
        Extract price data.
        
        Returns:
            Array of prices
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return self.df['Price'].values
    
    def get_dates(self) -> pd.DatetimeIndex:
        """
        Extract date index.
        
        Returns:
            DatetimeIndex of the data
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return self.df.index
    
    def get_summary_statistics(self) -> pd.DataFrame:
        """
        Get summary statistics of the data.
        
        Returns:
            DataFrame with summary statistics
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        stats = {
            'total_records': len(self.df),
            'start_date': self.df.index.min(),
            'end_date': self.df.index.max(),
            'mean_price': self.df['Price'].mean(),
            'std_price': self.df['Price'].std(),
            'min_price': self.df['Price'].min(),
            'max_price': self.df['Price'].max(),
            'mean_log_return': self.df['log_return'].mean(),
            'std_log_return': self.df['log_return'].std(),
            'skewness': self.df['log_return'].skew(),
            'kurtosis': self.df['log_return'].kurtosis()
        }
        
        return pd.DataFrame([stats])

# Example usage
if __name__ == "__main__":
    loader = DataLoader()
    df = loader.load_data()
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nSummary Statistics:")
    print(loader.get_summary_statistics())