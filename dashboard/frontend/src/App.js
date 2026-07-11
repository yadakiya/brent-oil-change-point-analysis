import axios from 'axios';
import { useEffect, useState } from 'react';
import './App.css';

// Import components
import DateRangePicker from './components/DateRangePicker';
import EventList from './components/EventList';
import PriceChart from './components/PriceChart';
import Statistics from './components/Statistics';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [priceData, setPriceData] = useState({ dates: [], prices: [], returns: [] });
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [changePoints, setChangePoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState({ start: null, end: null });
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [activeTab, setActiveTab] = useState('chart');

  // Load data on component mount
  useEffect(() => {
    fetchAllData();
  }, []);

  // Fetch data when date range changes
  useEffect(() => {
    if (dateRange.start || dateRange.end) {
      fetchPriceData();
    }
  }, [dateRange]);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([
        fetchPriceData(),
        fetchEvents(),
        fetchStats(),
        fetchChangePoints()
      ]);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load data. Please check if the backend is running.');
    }
    setLoading(false);
  };

  const fetchPriceData = async () => {
    try {
      const params = {};
      if (dateRange.start) params.start = dateRange.start;
      if (dateRange.end) params.end = dateRange.end;
      
      const response = await axios.get(`${API_URL}/prices`, { params });
      setPriceData(response.data);
    } catch (error) {
      console.error('Error fetching price data:', error);
      setError('Failed to load price data');
    }
  };

  const fetchEvents = async () => {
    try {
      const response = await axios.get(`${API_URL}/events`);
      setEvents(response.data.events || []);
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchChangePoints = async () => {
    try {
      const response = await axios.get(`${API_URL}/change_points`);
      setChangePoints(response.data.change_points || []);
    } catch (error) {
      console.error('Error fetching change points:', error);
    }
  };

  const handleEventClick = (event) => {
    setSelectedEvent(event);
    setActiveTab('chart');
  };

  const handleDateRangeChange = (start, end) => {
    setDateRange({ start, end });
  };

  const handleRefresh = () => {
    fetchAllData();
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loader">
          <div className="spinner"></div>
          <p>Loading Brent Oil Data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>⚠️ Error</h2>
        <p>{error}</p>
        <button onClick={handleRefresh}>Retry</button>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>🛢️ Brent Oil Price Analysis</h1>
          <p>Change Point Detection & Event Association</p>
          <button className="refresh-btn" onClick={handleRefresh}>🔄 Refresh</button>
        </div>
      </header>

      <main className="App-main">
        {/* Statistics Section */}
        <section className="stats-section">
          <Statistics stats={stats} />
        </section>

        {/* Tabs */}
        <div className="tabs">
          <button 
            className={activeTab === 'chart' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('chart')}
          >
            📊 Chart
          </button>
          <button 
            className={activeTab === 'events' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('events')}
          >
            📋 Events
          </button>
          <button 
            className={activeTab === 'analysis' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('analysis')}
          >
            📈 Analysis
          </button>
        </div>

        {/* Controls */}
        <section className="controls-section">
          <DateRangePicker 
            onRangeChange={handleDateRangeChange}
          />
        </section>

        {/* Content based on active tab */}
        {activeTab === 'chart' && (
          <section className="chart-section">
            <PriceChart 
              data={priceData}
              events={events}
              changePoints={changePoints}
              selectedEvent={selectedEvent}
              onEventClick={handleEventClick}
            />
          </section>
        )}

        {activeTab === 'events' && (
          <section className="events-section">
            <EventList 
              events={events}
              onEventClick={handleEventClick}
            />
          </section>
        )}

        {activeTab === 'analysis' && (
          <section className="analysis-section">
            <div className="analysis-card">
              <h3>📊 Key Findings</h3>
              {changePoints.length > 0 ? (
                <div>
                  <p><strong>Change Points Detected:</strong> {changePoints.length}</p>
                  <ul>
                    {changePoints.map((cp, idx) => (
                      <li key={idx}>
                        📅 {cp.date}: ${cp.price.toFixed(2)}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p>No significant change points detected.</p>
              )}
              
              {stats && (
                <div className="stats-detail">
                  <h4>📈 Price Statistics</h4>
                  <p>Mean: ${stats.price?.mean?.toFixed(2) || 'N/A'}</p>
                  <p>Std Dev: ${stats.price?.std?.toFixed(2) || 'N/A'}</p>
                  <p>Min: ${stats.price?.min?.toFixed(2) || 'N/A'}</p>
                  <p>Max: ${stats.price?.max?.toFixed(2) || 'N/A'}</p>
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      <footer className="App-footer">
        <p>© 2026 Birhan Energies - Data Science Team | Brent Oil Analysis Dashboard</p>
      </footer>
    </div>
  );
}

export default App;