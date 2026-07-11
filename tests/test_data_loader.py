"""
Unit tests for the DataLoader class.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.data_loader import DataLoader

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    prices = 50 + np.cumsum(np.random.randn(100) * 0.5)
    df = pd.DataFrame({
        'Date': dates,
        'Price': prices
    })
    return df

def test_data_loader_initialization():
    """Test DataLoader initialization."""
    loader = DataLoader()
    assert loader.data_path == Path("data/raw/BrentOilPrices.csv")
    assert loader.df is None

def test_data_loader_preprocessing(sample_data, tmp_path):
    """Test data preprocessing functionality."""
    test_path = tmp_path / "test_data.csv"
    sample_data.to_csv(test_path, index=False)
    
    loader = DataLoader(str(test_path))
    df = loader.load_data()
    
    assert 'log_return' in df.columns
    assert 'returns' in df.columns
    assert 'rolling_volatility' in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)

def test_data_loader_get_returns(sample_data, tmp_path):
    """Test getting log returns."""
    test_path = tmp_path / "test_data.csv"
    sample_data.to_csv(test_path, index=False)
    
    loader = DataLoader(str(test_path))
    loader.load_data()
    
    returns = loader.get_log_returns()
    assert isinstance(returns, np.ndarray)
    assert len(returns) > 0

def test_data_loader_get_prices(sample_data, tmp_path):
    """Test getting prices."""
    test_path = tmp_path / "test_data.csv"
    sample_data.to_csv(test_path, index=False)
    
    loader = DataLoader(str(test_path))
    loader.load_data()
    
    prices = loader.get_prices()
    assert isinstance(prices, np.ndarray)
    assert len(prices) > 0

def test_data_loader_summary_statistics(sample_data, tmp_path):
    """Test getting summary statistics."""
    test_path = tmp_path / "test_data.csv"
    sample_data.to_csv(test_path, index=False)
    
    loader = DataLoader(str(test_path))
    loader.load_data()
    
    stats = loader.get_summary_statistics()
    assert isinstance(stats, pd.DataFrame)
    assert 'mean_price' in stats.columns