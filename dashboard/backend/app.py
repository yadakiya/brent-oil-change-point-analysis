"""
Flask backend for Brent Oil Analysis Dashboard.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# Load data
try:
    # Load price data
    price_df = pd.read_csv(DATA_DIR / "raw" / "BrentOilPrices.csv")
    
    # FIX: Changed format='%d-%b-%y' to format='mixed' to cleanly parse formats like "Apr 22, 2020"
    price_df['Date'] = pd.to_datetime(price_df['Date'], format='mixed')
    
    price_df.set_index('Date', inplace=True)
    price_df.sort_index(inplace=True)
    logger.info(f"Loaded price data: {len(price_df)} records")
    
    # Load events
    events_df = pd.read_csv(DATA_DIR / "processed" / "events.csv")
    events_df['date'] = pd.to_datetime(events_df['date'])
    logger.info(f"Loaded events: {len(events_df)} events")
    
    # Load change points if available
    cp_path = RESULTS_DIR / "change_points.csv"
    if cp_path.exists():
        cp_df = pd.read_csv(cp_path)
        cp_df['date'] = pd.to_datetime(cp_df['date'])
        logger.info(f"Loaded change points: {len(cp_df)} points")
    else:
        cp_df = pd.DataFrame(columns=['index', 'date', 'price'])
        logger.warning("No change points file found")
        
except Exception as e:
    logger.error(f"Error loading data: {e}")
    price_df = pd.DataFrame()
    events_df = pd.DataFrame()
    cp_df = pd.DataFrame()

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """
    Get price data with optional date filtering.
    """
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        
        if price_df.empty:
            return jsonify({'error': 'No price data available'}), 404
        
        # Filter by date
        if start:
            start_date = pd.to_datetime(start)
            filtered = price_df[price_df.index >= start_date]
        else:
            filtered = price_df.copy()
            
        if end:
            end_date = pd.to_datetime(end)
            filtered = filtered[filtered.index <= end_date]
        
        # Prepare response
        response = {
            'dates': filtered.index.strftime('%Y-%m-%d').tolist(),
            'prices': filtered['Price'].values.tolist(),
            'returns': filtered['log_return'].values.tolist() if 'log_return' in filtered.columns else []
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_prices: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Get event data with optional filtering.
    """
    try:
        if events_df.empty:
            return jsonify({'error': 'No events data available'}), 404
        
        category = request.args.get('category')
        
        filtered = events_df.copy()
        if category:
            filtered = filtered[filtered['category'] == category]
        
        response = {
            'events': filtered.to_dict('records')
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/change_points', methods=['GET'])
def get_change_points():
    """
    Get change point data.
    """
    try:
        if cp_df.empty:
            return jsonify({'error': 'No change points available'}), 404
        
        response = {
            'change_points': cp_df.to_dict('records')
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_change_points: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/event_impact/<event_date>', methods=['GET'])
def get_event_impact(event_date):
    """
    Get impact analysis for a specific event.
    """
    try:
        event_date = pd.to_datetime(event_date)
        
        # Get price data around event
        pre_window = 30
        post_window = 30
        
        pre_start = event_date - pd.Timedelta(days=pre_window)
        post_end = event_date + pd.Timedelta(days=post_window)
        
        pre_prices = price_df.loc[pre_start:event_date, 'Price'] if event_date in price_df.index else []
        post_prices = price_df.loc[event_date:post_end, 'Price'] if event_date in price_df.index else []
        
        if len(pre_prices) > 0 and len(post_prices) > 0:
            pre_mean = pre_prices.mean()
            post_mean = post_prices.mean()
            price_change = post_mean - pre_mean
            percent_change = (price_change / pre_mean) * 100
            
            response = {
                'event_date': event_date.strftime('%Y-%m-%d'),
                'pre_mean': float(pre_mean),
                'post_mean': float(post_mean),
                'price_change': float(price_change),
                'percent_change': float(percent_change),
                'pre_prices': pre_prices.tolist(),
                'post_prices': post_prices.tolist()
            }
        else:
            response = {
                'error': 'Insufficient price data for this event'
            }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_event_impact: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get summary statistics.
    """
    try:
        if price_df.empty:
            return jsonify({'error': 'No price data available'}), 404
        
        stats = {
            'total_records': len(price_df),
            'date_range': {
                'start': price_df.index.min().strftime('%Y-%m-%d'),
                'end': price_df.index.max().strftime('%Y-%m-%d')
            },
            'price': {
                'mean': float(price_df['Price'].mean()),
                'std': float(price_df['Price'].std()),
                'min': float(price_df['Price'].min()),
                'max': float(price_df['Price'].max())
            },
            'returns': {
                'mean': float(price_df['log_return'].mean()) if 'log_return' in price_df.columns else 0.0,
                'std': float(price_df['log_return'].std()) if 'log_return' in price_df.columns else 0.0,
                'skew': float(price_df['log_return'].skew()) if 'log_return' in price_df.columns else 0.0,
                'kurtosis': float(price_df['log_return'].kurtosis()) if 'log_return' in price_df.columns else 0.0
            },
            'events_count': len(events_df),
            'change_points_count': len(cp_df)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({'status': 'healthy', 'timestamp': pd.Timestamp.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)