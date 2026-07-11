"""
Utility functions for the Brent oil analysis project.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import yaml
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Path to log file
    """
    level = getattr(logging, log_level.upper())
    
    handlers = [logging.StreamHandler()]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def save_figure(fig, save_path: str, dpi: int = 300, **kwargs):
    """
    Save a matplotlib figure.
    
    Args:
        fig: Matplotlib figure
        save_path: Path to save the figure
        dpi: Resolution
        **kwargs: Additional arguments for savefig
    """
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=dpi, bbox_inches='tight', **kwargs)
    logger.info(f"Figure saved to {save_path}")

def create_event_markers(ax, events_df, color: str = 'red', alpha: float = 0.7):
    """
    Add event markers to a matplotlib axis.
    
    Args:
        ax: Matplotlib axis
        events_df: DataFrame with event dates
        color: Marker color
        alpha: Marker transparency
    """
    for _, event in events_df.iterrows():
        ax.axvline(x=event['date'], color=color, alpha=alpha, linestyle='--', linewidth=1)
        ax.text(event['date'], ax.get_ylim()[1] * 0.95, 
                event['name'], rotation=45, ha='right', va='top', fontsize=8)

def calculate_rolling_statistics(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    Calculate rolling statistics for price data.
    
    Args:
        df: DataFrame with price data
        window: Rolling window size
        
    Returns:
        DataFrame with rolling statistics
    """
    df_roll = df.copy()
    
    # Rolling statistics
    df_roll['rolling_mean'] = df_roll['Price'].rolling(window).mean()
    df_roll['rolling_std'] = df_roll['Price'].rolling(window).std()
    df_roll['rolling_volatility'] = df_roll['log_return'].rolling(window).std()
    df_roll['rolling_skew'] = df_roll['log_return'].rolling(window).skew()
    df_roll['rolling_kurt'] = df_roll['log_return'].rolling(window).kurt()
    
    # Rolling quantiles
    df_roll['rolling_lower'] = df_roll['Price'].rolling(window).quantile(0.05)
    df_roll['rolling_upper'] = df_roll['Price'].rolling(window).quantile(0.95)
    
    # Rolling min/max
    df_roll['rolling_min'] = df_roll['Price'].rolling(window).min()
    df_roll['rolling_max'] = df_roll['Price'].rolling(window).max()
    
    return df_roll

def detect_outliers(data: np.ndarray, method: str = 'iqr', threshold: float = 3) -> np.ndarray:
    """
    Detect outliers in data.
    
    Args:
        data: Input array
        method: 'iqr' or 'zscore'
        threshold: Threshold for outlier detection
        
    Returns:
        Boolean array of outliers
    """
    if method == 'iqr':
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = (data < lower_bound) | (data > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((data - np.mean(data)) / np.std(data))
        outliers = z_scores > threshold
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return outliers

def format_price(price: float) -> str:
    """
    Format price with USD symbol.
    
    Args:
        price: Price value
        
    Returns:
        Formatted price string
    """
    return f"${price:,.2f}"

def format_percent(value: float) -> str:
    """
    Format percentage.
    
    Args:
        value: Percentage value
        
    Returns:
        Formatted percentage string
    """
    return f"{value:+.1f}%"

def print_section_header(title: str, width: int = 80):
    """
    Print a formatted section header.
    
    Args:
        title: Section title
        width: Width of the header
    """
    print(f"\n{'=' * width}")
    print(f"{title.center(width)}")
    print(f"{'=' * width}\n")

def print_impact_statement(impact_data: dict):
    """
    Print a formatted impact statement.
    
    Args:
        impact_data: Dictionary with impact metrics
    """
    print("\n" + "-" * 60)
    print("IMPACT ANALYSIS")
    print("-" * 60)
    
    print(f"Event: {impact_data.get('event_name', 'Unknown')}")
    print(f"Date: {impact_data.get('event_date', 'Unknown')}")
    print(f"Pre-Event Price: ${impact_data.get('pre_price', 0):.2f}")
    print(f"Post-Event Price: ${impact_data.get('post_price', 0):.2f}")
    print(f"Price Change: ${impact_data.get('price_change', 0):.2f}")
    print(f"Percent Change: {impact_data.get('percent_change', 0):.1f}%")
    print(f"Confidence: {impact_data.get('confidence', 0):.1f}%")
    
    print("-" * 60)

def export_results_to_csv(results: dict, output_path: str):
    """
    Export results to CSV.
    
    Args:
        results: Dictionary of results
        output_path: Path to output CSV
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to DataFrame
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_path, index=False)
    logger.info(f"Results exported to {output_path}")

def export_results_to_json(results: dict, output_path: str):
    """
    Export results to JSON.
    
    Args:
        results: Dictionary of results
        output_path: Path to output JSON
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert datetime to string
    json_results = {}
    for key, value in results.items():
        if isinstance(value, pd.Timestamp):
            json_results[key] = value.strftime('%Y-%m-%d')
        elif isinstance(value, pd.DatetimeIndex):
            json_results[key] = [d.strftime('%Y-%m-%d') for d in value]
        elif isinstance(value, np.ndarray):
            json_results[key] = value.tolist()
        else:
            json_results[key] = value
    
    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    logger.info(f"Results exported to {output_path}")

# Example usage
if __name__ == "__main__":
    # Test utility functions
    print_section_header("Testing Utilities")
    
    # Test formatting
    print(format_price(85.75))
    print(format_percent(12.5))