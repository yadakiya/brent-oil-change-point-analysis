"""
Event analysis module for associating change points with geopolitical events.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventAnalyzer:
    """
    Analyzes events and their association with oil price changes.
    """
    
    def __init__(self, events_path: str = "data/processed/events.csv"):
        """
        Initialize EventAnalyzer.
        
        Args:
            events_path: Path to events CSV file
        """
        self.events_path = Path(events_path)
        self.events = None
        self._create_default_events()
        
    def _create_default_events(self):
        """
        Create default events dataset if not exists.
        """
        events_data = [
            # 2026 Events
            ("2026-03-01", "Strait of Hormuz Closure - US Military Strikes on Iran", 
             "geopolitical", "US military strikes on Iran tied to Strait of Hormuz closure; Brent surged 60%+ to >$118"),
            
            ("2026-06-15", "US-Iran Preliminary Agreement", 
             "geopolitical", "Preliminary agreement helped crude prices retreat to ~$74; eased inflation fears"),
            
            ("2026-07-08", "US-Iran Ceasefire Breakdown", 
             "geopolitical", "Trump declared ceasefire 'over'; US resumed airstrikes; Brent jumped ~5% to $78"),
            
            ("2026-07-09", "European Energy Price Spike", 
             "geopolitical", "Brent surged ~7% to ~$80; European equities retreated; DAX and CAC 40 dropped >2%"),
            
            ("2026-05-01", "UAE Exits OPEC+", 
             "opec", "UAE withdrawal from OPEC and OPEC+; production increase adjusted to 188,000 bpd"),
            
            ("2026-04-01", "OPEC+ Production Increases Begin", 
             "opec", "7 major OPEC+ producers began gradual output increases; 206,000 bpd in April and May"),
            
            ("2026-08-01", "OPEC+ August Production Increase", 
             "opec", "Production increase of 188,000 bpd continues; fifth consecutive monthly increase"),
            
            ("2026-06-30", "Saudi Aramco Asia Price Cut", 
             "opec", "Saudi Aramco cut Arab Light OSP by $11/bbl for Asia; reflects intensifying market share competition"),
            
            ("2026-03-13", "IMF Stagflation Warning", 
             "economic", "IMF warns Middle East conflict could trigger stagflation; oil >$100/bbl"),
            
            ("2026-07-01", "IEA Demand Downgrade", 
             "economic", "IEA projects 2026 global demand contraction of ~1.1M bpd year-on-year"),
            
            ("2026-06-26", "US Commercial Crude Drawdown", 
             "economic", "US commercial crude inventories dropped by 380,000 bpd to 4.084M barrels; below 5-year average"),
            
            ("2026-07-09", "IEA Monthly Market Report", 
             "economic", "Report highlights global supply-demand balance and inventory trends"),
            
            ("2026-07-09", "Strait of Hormuz Transit Disruption", 
             "geopolitical", "Only 2 oil tankers transited early in day; shipping recovery tentative; insurance costs rising"),
            
            ("2026-07-10", "Oil Price Retreat", 
             "market", "Brent gave back gains, retesting $73.9-76.1 range; market focused on supply fundamentals"),
            
            ("2026-06-01", "Global Supply Recovery", 
             "supply", "Global supply increased 4.1M bpd to 98.8M bpd in June; still 9.4M bpd below pre-conflict"),
        ]
        
        self.events = pd.DataFrame(events_data, columns=['date', 'name', 'category', 'description'])
        self.events['date'] = pd.to_datetime(self.events['date'])
        self.events.sort_values('date', inplace=True)
        
        # Save to CSV
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        self.events.to_csv(self.events_path, index=False)
        logger.info(f"Created default events dataset with {len(self.events)} events")
    
    def load_events(self) -> pd.DataFrame:
        """
        Load events from CSV or create default.
        
        Returns:
            DataFrame of events
        """
        if self.events_path.exists():
            self.events = pd.read_csv(self.events_path)
            self.events['date'] = pd.to_datetime(self.events['date'])
            logger.info(f"Loaded {len(self.events)} events from {self.events_path}")
        else:
            self._create_default_events()
        
        return self.events
    
    def find_events_near_change_point(self, change_point_date: pd.Timestamp, 
                                       window_days: int = 30) -> pd.DataFrame:
        """
        Find events within a window around a change point.
        
        Args:
            change_point_date: Date of change point
            window_days: Number of days before/after to search
            
        Returns:
            DataFrame of nearby events
        """
        if self.events is None:
            self.load_events()
        
        start_date = change_point_date - pd.Timedelta(days=window_days)
        end_date = change_point_date + pd.Timedelta(days=window_days)
        
        nearby = self.events[
            (self.events['date'] >= start_date) & 
            (self.events['date'] <= end_date)
        ].copy()
        
        nearby['days_from_change'] = (nearby['date'] - change_point_date).dt.days
        nearby.sort_values('days_from_change', inplace=True)
        
        return nearby
    
    def quantify_event_impact(self, df: pd.DataFrame, event_date: pd.Timestamp,
                            pre_window: int = 30, post_window: int = 30) -> Dict:
        """
        Quantify the impact of an event on oil prices.
        
        Args:
            df: DataFrame with price data
            event_date: Date of the event
            pre_window: Days before event for baseline
            post_window: Days after event for impact
            
        Returns:
            Dictionary with impact metrics
        """
        # Get pre-event prices
        pre_start = event_date - pd.Timedelta(days=pre_window)
        pre_prices = df.loc[pre_start:event_date, 'Price'].values
        
        # Get post-event prices
        post_end = event_date + pd.Timedelta(days=post_window)
        post_prices = df.loc[event_date:post_end, 'Price'].values
        
        # Calculate metrics
        pre_mean = np.mean(pre_prices)
        post_mean = np.mean(post_prices)
        price_change = post_mean - pre_mean
        percent_change = (price_change / pre_mean) * 100
        
        # Find nearby events
        nearby_events = self.find_events_near_change_point(event_date, window_days=14)
        
        return {
            'event_date': event_date,
            'pre_mean_price': pre_mean,
            'post_mean_price': post_mean,
            'price_change': price_change,
            'percent_change': percent_change,
            'pre_volatility': np.std(pre_prices),
            'post_volatility': np.std(post_prices),
            'volatility_change': np.std(post_prices) - np.std(pre_prices),
            'nearby_events': nearby_events['name'].tolist(),
            'event_count': len(nearby_events)
        }
    
    def generate_event_report(self, df: pd.DataFrame, change_points: List[pd.Timestamp],
                            output_path: str = "results/reports/event_impact_report.md") -> str:
        """
        Generate comprehensive event impact report.
        
        Args:
            df: DataFrame with price data
            change_points: List of change point dates
            output_path: Path to save the report
            
        Returns:
            Report string
        """
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        report = "# Event Impact Analysis Report\n\n"
        report += "## Change Point - Event Associations\n\n"
        
        for cp_date in change_points:
            # Find nearby events
            nearby = self.find_events_near_change_point(cp_date, window_days=14)
            
            if len(nearby) > 0:
                report += f"### Change Point: {cp_date.strftime('%Y-%m-%d')}\n\n"
                
                for _, event in nearby.iterrows():
                    # Quantify impact
                    impact = self.quantify_event_impact(df, event['date'])
                    
                    report += f"**Event**: {event['name']}\n"
                    report += f"- **Date**: {event['date'].strftime('%Y-%m-%d')}\n"
                    report += f"- **Category**: {event['category']}\n"
                    report += f"- **Price Change**: ${impact['price_change']:.2f} ({impact['percent_change']:.1f}%)\n"
                    report += f"- **Pre-Event Price**: ${impact['pre_mean_price']:.2f}\n"
                    report += f"- **Post-Event Price**: ${impact['post_mean_price']:.2f}\n"
                    report += f"- **Volatility Change**: {impact['volatility_change']:.4f}\n"
                    report += f"- **Description**: {event['description']}\n\n"
        
        # Summary statistics
        report += "## Summary Statistics\n\n"
        report += f"**Total Events Analyzed**: {len(self.events)}\n"
        report += f"**Events Associated with Change Points**: {len(change_points)}\n\n"
        
        # Category breakdown
        category_counts = self.events['category'].value_counts()
        report += "### Event Categories\n\n"
        for category, count in category_counts.items():
            report += f"- {category}: {count} events\n"
        
        # Save report
        with open(output_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Event report saved to {output_path}")
        return report

# Example usage
if __name__ == "__main__":
    from data_loader import DataLoader
    
    loader = DataLoader()
    df = loader.load_data()
    
    event_analyzer = EventAnalyzer()
    events = event_analyzer.load_events()
    
    # Example: find events near a specific date
    cp_date = pd.Timestamp('2026-03-01')
    nearby = event_analyzer.find_events_near_change_point(cp_date)
    print(f"Events near {cp_date}:")
    print(nearby[['name', 'date', 'days_from_change']])
    
    # Example: quantify impact
    impact = event_analyzer.quantify_event_impact(df, cp_date)
    print(f"Impact: ${impact['price_change']:.2f} ({impact['percent_change']:.1f}%)")