import { useState } from 'react';

const EventList = ({ events, onEventClick }) => {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  const categories = ['all', ...new Set(events.map(e => e.category))];

  const filteredEvents = events.filter(event => {
    const matchCategory = filter === 'all' || event.category === filter;
    const matchSearch = event.name.toLowerCase().includes(search.toLowerCase()) ||
                        event.description.toLowerCase().includes(search.toLowerCase());
    return matchCategory && matchSearch;
  });

  const getCategoryColor = (category) => {
    const colors = {
      geopolitical: '#fde8e8',
      opec: '#e8f4fd',
      economic: '#fef9e7',
      supply: '#e8f8f5',
      market: '#f0eef8'
    };
    return colors[category] || '#eee';
  };

  return (
    <div className="events-section">
      <h3>📋 Events Database ({events.length} events)</h3>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '15px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="🔍 Search events..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: '8px 12px',
            border: '1px solid #ddd',
            borderRadius: '6px',
            flex: '1',
            minWidth: '200px',
            fontSize: '14px'
          }}
        />
        
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            border: '1px solid #ddd',
            borderRadius: '6px',
            fontSize: '14px',
            background: 'white'
          }}
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: '10px', fontSize: '14px', color: '#888' }}>
        Showing {filteredEvents.length} of {events.length} events
      </div>

      <div className="event-list">
        {filteredEvents.map((event, index) => (
          <div
            key={index}
            className="event-item"
            onClick={() => onEventClick(event)}
            style={{ borderLeft: `4px solid ${getCategoryColor(event.category)}` }}
          >
            <div className="event-date">
              {event.date} • <span className={`event-category ${event.category}`}>
                {event.category}
              </span>
            </div>
            <div className="event-name">{event.name}</div>
            <div style={{ fontSize: '13px', color: '#666', marginTop: '4px' }}>
              {event.description.substring(0, 100)}...
            </div>
          </div>
        ))}
        
        {filteredEvents.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
            No events found matching your filters.
          </div>
        )}
      </div>
    </div>
  );
};

export default EventList;