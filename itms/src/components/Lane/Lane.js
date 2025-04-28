import React from 'react';
import './Lane.css';

const Lane = ({ id, status, timer, vehicleCount }) => {
  const statusText = {
    green: 'Active',
    yellow: 'Changing',
    red: 'Waiting',
    off: 'Offline',
    loading: 'Loading...'
  };

  return (
    <div className={`lane ${status}`}>
      <h3>Lane {id}</h3>
      <div className="status-badge">{statusText[status]}</div>
      <div className="timer">
        {status === 'green' || status === 'yellow' ? `${timer}` : '--'}
      </div>
      <div className="vehicle-count">
        {vehicleCount !== undefined ? `${vehicleCount} vehicles` : 'N/A'}
      </div>
    </div>
  );
};

export default React.memo(Lane);  // Optimize rendering