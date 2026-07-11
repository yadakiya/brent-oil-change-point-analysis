#!/usr/bin/env python
"""
Main analysis script to run the complete Brent oil price analysis pipeline.
Data file: BrentOilPrices.csv
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from datetime import datetime

from src.data_loader import DataLoader
from src.eda import EDAnalyzer
from src.change_point_model import ChangePointModel
from src.event_analysis import EventAnalyzer
from src.utils import setup_logging, print_section_header, save_figure

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
setup_logging(log_file=str(log_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))

# Set plot style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create directories
for dir_name in ["results/figures", "results/reports", "data/processed"]:
    Path(dir_name).mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

def main():
    """
    Main analysis pipeline for BrentOilPrices.csv data.
    """
    print_section_header("Brent Oil Price Analysis Pipeline")
    logger.info("Starting analysis pipeline for BrentOilPrices.csv...")
    
    # Step 1: Load and prepare data
    print_section_header("Step 1: Data Loading")
    loader = DataLoader("data/raw/BrentOilPrices.csv")
    df = loader.load_data()
    logger.info(f"Loaded {len(df)} records from {df.index.min()} to {df.index.max()}")
    
    # Show first few rows to verify
    print("\nFirst 5 rows of data:")
    print(df.head())
    
    # Step 2: Exploratory Data Analysis
    print_section_header("Step 2: Exploratory Data Analysis")
    eda = EDAnalyzer(df)
    
    # Generate EDA plots
    eda.plot_time_series("results/figures/time_series.png")
    eda.plot_distributions("results/figures/distributions.png")
    eda.plot_acf_pacf("results/figures/acf_pacf.png")
    eda.identify_volatility_clusters("results/figures/volatility.png")
    
    # Test stationarity
    price_pvalue, returns_pvalue = eda.test_stationarity()
    logger.info(f"Price ADF p-value: {price_pvalue:.6f}")
    logger.info(f"Returns ADF p-value: {returns_pvalue:.6f}")
    
    # Generate EDA report
    eda.generate_comprehensive_report("results/reports/eda_report.md")
    
    # Step 3: Event compilation
    print_section_header("Step 3: Event Compilation")
    event_analyzer = EventAnalyzer("data/processed/events.csv")
    events = event_analyzer.load_events()
    logger.info(f"Compiled {len(events)} events")
    
    # Step 4: Change Point Detection
    print_section_header("Step 4: Change Point Detection")
    
    returns = loader.get_log_returns()
    dates = loader.get_dates()
    
    # Single change point model
    cp_model = ChangePointModel(returns, dates, model_type='single')
    cp_model.build_single_change_point_model()
    trace = cp_model.fit(n_samples=2000, n_tune=1000, n_chains=4)
    
    # Check convergence
    convergence = cp_model.check_convergence()
    logger.info(f"Model converged: {convergence['converged']}")
    logger.info(f"Max R-hat: {convergence['max_r_hat']:.4f}")
    
    # Extract change points
    cp_indices = cp_model.get_change_points(threshold=0.7)
    
    if cp_indices:
        cp_dates = [dates[i] for i in cp_indices]
        logger.info(f"Found {len(cp_dates)} change points")
        for cp_date in cp_dates:
            logger.info(f"  - {cp_date}")
        
        # Save change points
        cp_df = pd.DataFrame({
            'index': cp_indices,
            'date': cp_dates,
            'price': [df['Price'].iloc[i] for i in cp_indices]
        })
        cp_df.to_csv("results/change_points.csv", index=False)
        
        # Plot results
        cp_model.plot_results("results/figures/change_point_results.png")
        
        # Generate impact statement
        statement = cp_model.generate_impact_statement(df)
        with open("results/reports/impact_statement.md", 'w') as f:
            f.write(statement)
        
        # Step 5: Event Association
        print_section_header("Step 5: Event Association")
        
        for cp_date in cp_dates:
            nearby = event_analyzer.find_events_near_change_point(cp_date, window_days=30)
            if len(nearby) > 0:
                logger.info(f"\nEvents near {cp_date}:")
                for _, event in nearby.iterrows():
                    logger.info(f"  - {event['date']}: {event['name']}")
                    logger.info(f"    Category: {event['category']}")
                    logger.info(f"    Days from CP: {event['days_from_change']} days")
        
        # Generate event report
        event_analyzer.generate_event_report(df, cp_dates, "results/reports/event_impact_report.md")
    
    else:
        logger.warning("No significant change points detected")
    
    # Step 6: Save model results
    print_section_header("Step 6: Saving Results")
    cp_model.save_results("results/")
    
    # Save parameter estimates
    estimates = cp_model.get_parameter_estimates()
    estimates_df = pd.DataFrame(estimates).T
    estimates_df.to_csv("results/parameter_estimates.csv")
    
    print_section_header("Analysis Complete!")
    logger.info("All results saved to the 'results' directory")
    
    # Print summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"Data file: BrentOilPrices.csv")
    print(f"Total records analyzed: {len(df)}")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    print(f"Price range: ${df['Price'].min():.2f} to ${df['Price'].max():.2f}")
    print(f"Average price: ${df['Price'].mean():.2f}")
    print(f"Events compiled: {len(events)}")
    print(f"Change points detected: {len(cp_indices) if cp_indices else 0}")
    print("="*60)
    print("\nOutput files:")
    print("  - results/figures/         : All generated plots")
    print("  - results/reports/         : Analysis reports")
    print("  - results/change_points.csv: Detected change points")
    print("  - results/parameter_estimates.csv: Model parameters")
    print("="*60)

if __name__ == "__main__":
    main()