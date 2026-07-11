"""
Unit tests for the ChangePointModel class.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.change_point_model import ChangePointModel

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    n = 200
    # Create data with a change point at index 100
    data = np.concatenate([
        np.random.normal(0, 0.1, 100),
        np.random.normal(0.2, 0.1, 100)
    ])
    dates = pd.date_range('2020-01-01', periods=n, freq='D')
    return data, dates

def test_change_point_initialization(sample_data):
    """Test ChangePointModel initialization."""
    data, dates = sample_data
    model = ChangePointModel(data, dates, model_type='single')
    assert model.data is not None
    assert model.n == len(data)

def test_change_point_build_model(sample_data):
    """Test model building."""
    data, dates = sample_data
    model = ChangePointModel(data, dates, model_type='single')
    model.build_single_change_point_model()
    assert model.model is not None

def test_change_point_fit(sample_data):
    """Test model fitting (small sample for speed)."""
    data, dates = sample_data
    model = ChangePointModel(data[:50], dates[:50], model_type='single')
    model.build_single_change_point_model()
    
    # Fit with small number of samples for testing
    trace = model.fit(n_samples=200, n_tune=100, n_chains=2)
    assert trace is not None

def test_change_point_convergence(sample_data):
    """Test convergence checking."""
    data, dates = sample_data
    model = ChangePointModel(data[:50], dates[:50], model_type='single')
    model.build_single_change_point_model()
    model.fit(n_samples=200, n_tune=100, n_chains=2)
    
    convergence = model.check_convergence()
    assert 'converged' in convergence
    assert 'max_r_hat' in convergence

def test_change_point_extraction(sample_data):
    """Test change point extraction."""
    data, dates = sample_data
    model = ChangePointModel(data[:50], dates[:50], model_type='single')
    model.build_single_change_point_model()
    model.fit(n_samples=200, n_tune=100, n_chains=2)
    
    cp_indices = model.get_change_points(threshold=0.5)
    assert isinstance(cp_indices, list)