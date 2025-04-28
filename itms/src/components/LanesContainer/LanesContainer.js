import React from 'react';
import Lane from '../Lane/Lane';
import './LanesContainer.css';

const LanesContainer = ({ lanes = [] }) => {
  console.log("Rendering lanes:", lanes); // Debug log
  
  if (!lanes || lanes.length === 0) {
    return (
      <div className="lanes-container">
        <div className="no-lanes-warning">
          ⚠️ No lane data received. Check these possible issues:
          <ul>
            <li>Backend API returning empty lane_status</li>
            <li>Incorrect data structure in response</li>
            <li>Network request failing</li>
          </ul>
        </div>
      </div>
    );
  }

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

export default React.memo(LanesContainer);