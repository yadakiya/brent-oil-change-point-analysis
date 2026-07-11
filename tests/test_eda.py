"""
Unit tests for the EDAnalyzer class.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.eda import EDAnalyzer
from src.data_loader import DataLoader

@pytest.fixture
def sample_df():
    """Create sample DataFrame for testing."""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    prices = 50 + np.cumsum(np.random.randn(100) * 0.5)
    df = pd.DataFrame({
        'Price': prices,
        'log_return': np.random.randn(100) * 0.02
    }, index=dates)
    return df

def test_eda_initialization(sample_df):
    """Test EDAnalyzer initialization."""
    eda = EDAnalyzer(sample_df)
    assert eda.df is not None
    assert len(eda.df) == 100

def test_eda_stationarity(sample_df):
    """Test stationarity testing."""
    eda = EDAnalyzer(sample_df)
    price_pvalue, returns_pvalue = eda.test_stationarity()
    assert isinstance(price_pvalue, float)
    assert isinstance(returns_pvalue, float)

def test_eda_plot_functions(sample_df, tmp_path):
    """Test plotting functions."""
    eda = EDAnalyzer(sample_df)
    
    # Test that plotting doesn't raise errors
    try:
        eda.plot_time_series(str(tmp_path / "time_series.png"))
        eda.plot_distributions(str(tmp_path / "distributions.png"))
        eda.plot_acf_pacf(str(tmp_path / "acf_pacf.png"))
        eda.identify_volatility_clusters(str(tmp_path / "volatility.png"))
    except Exception as e:
        pytest.fail(f"Plotting failed: {e}")

def test_eda_report_generation(sample_df, tmp_path):
    """Test report generation."""
    eda = EDAnalyzer(sample_df)
    report_path = str(tmp_path / "report.md")
    eda.generate_comprehensive_report(report_path)
    
    import os
    assert os.path.exists(report_path)