import { useState } from 'react';

const DateRangePicker = ({ onRangeChange }) => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleApply = () => {
    onRangeChange(startDate || null, endDate || null);
  };

  const handleReset = () => {
    setStartDate('');
    setEndDate('');
    onRangeChange(null, null);
  };

  return (
    <div className="date-range-picker">
      <label>📅 Date Range:</label>
      <input
        type="date"
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
        placeholder="Start Date"
      />
      <span style={{ color: '#888' }}>to</span>
      <input
        type="date"
        value={endDate}
        onChange={(e) => setEndDate(e.target.value)}
        placeholder="End Date"
      />
      <button
        onClick={handleApply}
        style={{
          padding: '8px 20px',
          background: '#2d6a9f',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '14px'
        }}
      >
        Apply
      </button>
      <button
        onClick={handleReset}
        style={{
          padding: '8px 16px',
          background: '#eee',
          color: '#555',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '14px'
        }}
      >
        Reset
      </button>
    </div>
  );
};

export default DateRangePicker;