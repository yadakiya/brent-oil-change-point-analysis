import { useState } from 'react';
import {
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';

const PriceChart = ({ data, events, changePoints, selectedEvent, onEventClick }) => {
  const [tooltipData, setTooltipData] = useState(null);

  // Format data for Recharts
  const formatChartData = () => {
    if (!data.dates || !data.prices) return [];
    
    return data.dates.map((date, index) => ({
      date: date,
      price: data.prices[index],
      return: data.returns && data.returns[index] ? data.returns[index] : 0,
      isEvent: false,
      eventName: null
    }));
  };

  const chartData = formatChartData();

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      
      // Check if this is an event point
      const event = events.find(e => e.date === dataPoint.date);
      
      return (
        <div style={{
          background: 'white',
          padding: '12px 16px',
          border: '1px solid #ddd',
          borderRadius: '6px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          maxWidth: '250px'
        }}>
          <p style={{ margin: 0, fontWeight: 600, fontSize: '14px' }}>
            {dataPoint.date}
          </p>
          <p style={{ margin: '4px 0', color: '#2d6a9f' }}>
            Price: ${dataPoint.price.toFixed(2)}
          </p>
          {event && (
            <div style={{ marginTop: '8px', borderTop: '1px solid #eee', paddingTop: '8px' }}>
              <p style={{ margin: 0, fontWeight: 600, color: '#e67e22' }}>
                {event.name}
              </p>
              <p style={{ margin: '2px 0', fontSize: '12px', color: '#888' }}>
                Category: {event.category}
              </p>
              <p style={{ margin: '2px 0', fontSize: '11px', color: '#666' }}>
                {event.description.substring(0, 60)}...
              </p>
            </div>
          )}
          {dataPoint.isChangePoint && (
            <p style={{ margin: '4px 0', color: '#e74c3c', fontWeight: 600 }}>
              🔴 Change Point
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // Get min and max for domain
  const allPrices = chartData.map(d => d.price);
  const minPrice = Math.min(...allPrices) * 0.95;
  const maxPrice = Math.max(...allPrices) * 1.05;

  // Event markers for scatter
  const eventScatterData = events.map(event => {
    const point = chartData.find(d => d.date === event.date);
    return {
      x: event.date,
      y: point ? point.price : 0,
      event: event
    };
  });

  // Change point markers
  const cpScatterData = changePoints.map(cp => ({
    x: cp.date,
    y: cp.price,
    cp: cp
  }));

  return (
    <div className="price-chart-container">
      <h3>Brent Oil Price History with Change Points</h3>
      <ResponsiveContainer width="100%" height={500}>
        <ComposedChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 60,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            angle={-45}
            textAnchor="end"
            height={80}
            interval={Math.floor(chartData.length / 20)}
            tick={{ fontSize: 10 }}
          />
          <YAxis 
            domain={[minPrice, maxPrice]}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Price line */}
          <Line
            type="monotone"
            dataKey="price"
            stroke="#2d6a9f"
            strokeWidth={2}
            dot={false}
            name="Brent Oil Price (USD)"
          />
          
          {/* Event markers as ReferenceLines */}
          {events.map((event, index) => (
            <ReferenceLine
              key={`event-${index}`}
              x={event.date}
              stroke="#e67e22"
              strokeDasharray="3 3"
              strokeWidth={1.5}
              label={{
                value: event.name.length > 15 ? event.name.substring(0, 15) + '...' : event.name,
                position: 'top',
                fill: '#e67e22',
                fontSize: 8,
                angle: -45,
                textAnchor: 'end'
              }}
            />
          ))}
          
          {/* Change point markers */}
          {changePoints.map((cp, index) => (
            <ReferenceLine
              key={`cp-${index}`}
              x={cp.date}
              stroke="#e74c3c"
              strokeWidth={2.5}
              label={{
                value: '🔴 CP',
                position: 'bottom',
                fill: '#e74c3c',
                fontSize: 11,
                fontWeight: 'bold'
              }}
            />
          ))}
          
          {/* Event scatter points */}
          <Scatter
            data={eventScatterData}
            fill="#e67e22"
            shape="diamond"
            name="Events"
          />
          
          {/* Change point scatter points */}
          <Scatter
            data={cpScatterData}
            fill="#e74c3c"
            shape="circle"
            name="Change Points"
          />
        </ComposedChart>
      </ResponsiveContainer>
      
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#2d6a9f' }}></span>
          Price Series
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#e67e22' }}></span>
          Events (Click for details)
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#e74c3c' }}></span>
          Change Points
        </div>
      </div>
    </div>
  );
};

export default PriceChart;