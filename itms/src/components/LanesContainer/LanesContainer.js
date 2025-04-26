import React from 'react';
import Lane from '../Lane/Lane';
import './LanesContainer.css';

const LanesContainer = ({ lanes }) => {
  return (
    <div className="lanes-container">
      {lanes.map(lane => (
        <Lane 
          key={lane.id}
          id={lane.id}
          status={lane.status}
          timer={lane.timer}
          vehicleCount={lane.vehicleCount}
        />
      ))}
    </div>
  );
};

export default LanesContainer;