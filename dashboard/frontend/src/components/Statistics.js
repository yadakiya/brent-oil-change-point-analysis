
const Statistics = ({ stats }) => {
  if (!stats) {
    return (
      <div className="stats-grid">
        <div className="stat-item">
          <div className="label">Loading...</div>
          <div className="value">-</div>
        </div>
      </div>
    );
  }

  const formatNumber = (num) => {
    if (num === undefined || num === null) return '-';
    if (typeof num === 'number') {
      return num.toFixed(2);
    }
    return num;
  };

  return (
    <div className="stats-grid">
      <div className="stat-item">
        <div className="label">📅 Total Records</div>
        <div className="value">{stats.total_records || '-'}</div>
      </div>
      
      <div className="stat-item">
        <div className="label">💰 Mean Price</div>
        <div className="value">${formatNumber(stats.price?.mean)}</div>
      </div>
      
      <div className="stat-item">
        <div className="label">📈 Max Price</div>
        <div className="value green">${formatNumber(stats.price?.max)}</div>
      </div>
      
      <div className="stat-item">
        <div className="label">📉 Min Price</div>
        <div className="value red">${formatNumber(stats.price?.min)}</div>
      </div>
      
      <div className="stat-item">
        <div className="label">📊 Volatility (Std)</div>
        <div className="value orange">${formatNumber(stats.price?.std)}</div>
      </div>
      
      <div className="stat-item">
        <div className="label">📌 Events</div>
        <div className="value">{stats.events_count || 0}</div>
      </div>
      
      <div className="stat-item">
        <div className="label">🔴 Change Points</div>
        <div className="value">{stats.change_points_count || 0}</div>
      </div>
      
      <div className="stat-item">
        <div className="label">📅 Date Range</div>
        <div className="value" style={{ fontSize: '12px' }}>
          {stats.date_range?.start || '-'}<br/>
          to {stats.date_range?.end || '-'}
        </div>
      </div>
    </div>
  );
};

export default Statistics;