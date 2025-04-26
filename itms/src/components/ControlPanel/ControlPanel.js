import React from 'react';
import './ControlPanel.css';

const ControlPanel = ({ systemStatus, onStart, onStop, isSystemRunning }) => {
  return (
    <div className="control-panel">
      <button 
        id="startBtn" 
        onClick={onStart}
        disabled={isSystemRunning}
      >
        Start System
      </button>
      <button 
        id="stopBtn" 
        onClick={onStop}
        disabled={!isSystemRunning}
      >
        Stop System
      </button>
      <div className="status-display">
        Status: {systemStatus.charAt(0).toUpperCase() + systemStatus.slice(1)}
      </div>
    </div>
  );
};

export default ControlPanel;