#!/usr/bin/env python
"""
Generate comprehensive reports from analysis results.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import os
from datetime import datetime

def generate_report():
    """
    Generate a comprehensive report from all analysis results.
    """
    print("📊 Generating Comprehensive Report...")
    print("="*60)
    
    # Create reports directory
    os.makedirs("../results/reports", exist_ok=True)
    
    # Load results
    results = {}
    
    # Load change points
    cp_path = "../results/change_points.csv"
    if os.path.exists(cp_path):
        results['change_points'] = pd.read_csv(cp_path)
        print(f"✅ Loaded {len(results['change_points'])} change points")
    
    # Load parameter estimates
    est_path = "../results/parameter_estimates.txt"
    if os.path.exists(est_path):
        with open(est_path, 'r') as f:
            results['parameters'] = f.read()
        print("✅ Loaded parameter estimates")
    
    # Load summary
    summary_path = "../results/analysis_summary.txt"
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            results['summary'] = f.read()
        print("✅ Loaded analysis summary")
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Brent Oil Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f7fa; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #1a3a5c; border-bottom: 3px solid #2d6a9f; padding-bottom: 10px; }}
            h2 {{ color: #2d6a9f; margin-top: 30px; }}
            .section {{ background: #f8faff; padding: 20px; border-radius: 8px; margin: 15px 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #2d6a9f; color: white; }}
            .highlight {{ background: #fef9e7; padding: 10px; border-left: 4px solid #f39c12; }}
            .footer {{ margin-top: 40px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #ddd; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛢️ Brent Oil Price Analysis Report</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="section">
                <h2>📊 Summary</h2>
                <pre style="white-space: pre-wrap;">{results.get('summary', 'No summary available')}</pre>
            </div>
            
            <div class="section">
                <h2>🎯 Change Points Detected</h2>
                {results['change_points'].to_html(index=False) if 'change_points' in results else '<p>No change points detected</p>'}
            </div>
            
            <div class="section">
                <h2>📈 Parameter Estimates</h2>
                <pre style="white-space: pre-wrap;">{results.get('parameters', 'No parameters available')}</pre>
            </div>
            
            <div class="highlight">
                <h3>💡 Recommendations</h3>
                <ul>
                    <li>Monitor geopolitical events in oil-producing regions</li>
                    <li>Use Bayesian uncertainty for risk management</li>
                    <li>Consider multiple change points for complex analysis</li>
                    <li>Extend model with macroeconomic indicators</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>© 2026 Birhan Energies - Data Science Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    report_path = "../results/reports/comprehensive_report.html"
    with open(report_path, 'w') as f:
        f.write(html_content)
    print(f"✅ HTML report saved to {report_path}")
    
    # Also save as Markdown
    md_content = f"""
    # Brent Oil Price Analysis Report
    
    **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ## Summary
    
    {results.get('summary', 'No summary available')}
    
    ## Change Points Detected
    
    {results['change_points'].to_markdown(index=False) if 'change_points' in results else 'No change points detected'}
    
    ## Parameter Estimates
    
    {results.get('parameters', 'No parameters available')}
    
    ## Recommendations
    
    - Monitor geopolitical events in oil-producing regions
    - Use Bayesian uncertainty for risk management
    - Consider multiple change points for complex analysis
    - Extend model with macroeconomic indicators
    
    ---
    *© 2026 Birhan Energies - Data Science Team*
    """
    
    md_path = "../results/reports/comprehensive_report.md"
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"✅ Markdown report saved to {md_path}")
    
    print("\n" + "="*60)
    print("✅ Reports generated successfully!")
    print(f"📁 Check the 'results/reports' folder")

if __name__ == "__main__":
    generate_report()