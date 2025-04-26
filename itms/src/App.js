import React, { useState, useEffect } from 'react';
import ControlPanel from '../src/components/ControlPanel/ControlPanel';
import LanesContainer from '../src/components/LanesContainer/LanesContainer';
import DebugSection from '../src/components/DebugSection/DebugSection';
import './App.css';

function App() {
  const [systemStatus, setSystemStatus] = useState('stopped');
  const [lanes, setLanes] = useState([]);
  const [updateInterval, setUpdateInterval] = useState(null);

  // Initialize lanes
  useEffect(() => {
    const initialLanes = Array.from({ length: 4 }, (_, i) => ({
      id: i + 1,
      status: 'off',
      timer: '--',
      vehicleCount: 0
    }));
    setLanes(initialLanes);
  }, []);

  // Update system status
  const updateSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/status');
      const data = await response.json();
      
      setSystemStatus(data.system_status);
      
      const updatedLanes = lanes.map((lane, index) => {
        const laneData = data.lane_status?.[lane.id] || 'off';
        return {
          ...lane,
          status: laneData,
          timer: (laneData === 'green' || laneData === 'yellow') 
            ? `${data.time_remain}s` 
            : '--',
          vehicleCount: data.vehicle_counts?.[index]?.toFixed(1) || 0
        };
      });
      
      setLanes(updatedLanes);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  // Start the system
  const startSystem = async () => {
    try {
      const response = await fetch('http://localhost:5000/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      
      if (data.status === 'started') {
        setUpdateInterval(setInterval(updateSystemStatus, 1000));
        updateSystemStatus();
      }
    } catch (error) {
      console.error('Error starting system:', error);
      alert('Failed to start system');
    }
  };

  // Stop the system
  const stopSystem = async () => {
    try {
      const response = await fetch('http://localhost:5000/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      
      if (data.status === 'stopped') {
        clearInterval(updateInterval);
        setUpdateInterval(null);
        updateSystemStatus();
      }
    } catch (error) {
      console.error('Error stopping system:', error);
      alert('Failed to stop system');
    }
  };

  return (
    <div className="app">
      <h1>Traffic Management System</h1>
      
      <ControlPanel 
        systemStatus={systemStatus}
        onStart={startSystem}
        onStop={stopSystem}
        isSystemRunning={systemStatus === 'running'}
      />
      
      <LanesContainer lanes={lanes} />
      
      <DebugSection />
    </div>
  );
}

export default App;