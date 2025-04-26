import React from 'react';
import './Lane.css';

const Lane = ({ id, status, timer, vehicleCount }) => {
  return (
    <div className={`lane ${status}`}>
      <h3>Lane {id}</h3>
      <div className="timer">{timer}</div>
      <div className="vehicle-count">
        {vehicleCount} vehicle{vehicleCount !== 1 ? 's' : ''}
      </div>
    </div>
  );
};

export default Lane;