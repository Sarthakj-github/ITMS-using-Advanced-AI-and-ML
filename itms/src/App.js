import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import ControlPanel from './components/ControlPanel/ControlPanel';
import LanesContainer from './components/LanesContainer/LanesContainer';
import DebugSection from './components/DebugSection/DebugSection';
import LoadingSpinner from './components/LoadingSpinner/LoadingSpinner';
import './App.css';

function App() {
  const [systemStatus, setSystemStatus] = useState('stopped');
  const [lanes, setLanes] = useState([]);
  const [updateInterval, setUpdateInterval] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(null);

  // Initialize lanes with loading state
  useEffect(() => {
    const initialLanes = Array.from({ length: 4 }, (_, i) => ({
      id: i + 1,
      status: 'loading',
      timer: '--',
      vehicleCount: 0
    }));
    setLanes(initialLanes);
    fetchInitialStatus();
  }, []);

  // Fetch initial system status
  const fetchInitialStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/status');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      console.log("Initial status data:", data); // Debug log
      
      if (!data.lane_status) {
        throw new Error("No lane_status in response");
      }
      
      setSystemStatus(data.system_status || 'stopped');
      updateLanesData(data);
      setConnectionError(null);
    } catch (error) {
      console.error('Initial connection failed:', error);
      setConnectionError('Failed to connect to server. Please check your connection.');
      setSystemStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  // Update system status
  const updateSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/status');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      console.log("Update status data:", data); // Debug log
      
      setSystemStatus(data.system_status || 'stopped');
      updateLanesData(data);
      setConnectionError(null);
    } catch (error) {
      console.error('Error fetching status:', error);
      setConnectionError('Connection lost. Attempting to reconnect...');
      setSystemStatus('error');
    }
  };

  // Update lanes data with proper error handling
  const updateLanesData = (data) => {
    try {
      // Create a fresh lanes array instead of mapping existing state
      const newLanes = Array.from({ length: 4 }, (_, i) => {
        const laneId = i + 1;
        return {
          id: laneId,
          status: data.lane_status?.[laneId] || 'off',
          timer: (data.lane_status?.[laneId] === 'green' || data.lane_status?.[laneId] === 'yellow') 
            ? `${data.time_remain}s` 
            : '--',
          vehicleCount: data.vehicle_counts?.[i]?.toFixed(1) || 0
        };
      });
      
      console.log("Updating lanes with:", newLanes); // Debug log
      setLanes(newLanes);
    } catch (error) {
      console.error('Error updating lane data:', error);
      setLanes(Array.from({ length: 4 }, (_, i) => ({
        id: i + 1,
        status: 'error',
        timer: '--',
        vehicleCount: 0
      })));
    }
  };

  // Start the system
  const startSystem = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5000/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      console.log("Start response:", data); // Debug log
      
      if (data.status === 'started') {
        setUpdateInterval(setInterval(updateSystemStatus, 1000));
        updateSystemStatus();
      }
    } catch (error) {
      console.error('Error starting system:', error);
      setConnectionError('Failed to start system. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Stop the system
  const stopSystem = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5000/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      console.log("Stop response:", data); // Debug log
      
      if (data.status === 'stopped') {
        clearInterval(updateInterval);
        setUpdateInterval(null);
        updateSystemStatus();
      }
    } catch (error) {
      console.error('Error stopping system:', error);
      setConnectionError('Failed to stop system properly.');
    } finally {
      setIsLoading(false);
    }
  };

  // Render loading screen
  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-content">
          <LoadingSpinner size="large" color="blue" />
          <h2>Initializing Traffic Management System</h2>
          <p>Connecting to server...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <h1>Traffic Management System</h1>
      
      {connectionError && (
        <div className="connection-error">
          <p>{connectionError}</p>
          <button onClick={fetchInitialStatus}>Retry Connection</button>
        </div>
      )}
      
      <ControlPanel 
        systemStatus={systemStatus}
        onStart={startSystem}
        onStop={stopSystem}
        isSystemRunning={systemStatus === 'running'}
        isLoading={isLoading}
      />

      {/* Debug lane data display */}
      {/* <div style={{ margin: '20px', padding: '10px', background: '#f5f5f5' }}>
        <h3>Debug Info (remove in production):</h3>
        <pre>{JSON.stringify(lanes, null, 2)}</pre>
      </div> */}
      
      <LanesContainer lanes={lanes} />
      
      <DebugSection />
    </div>
  );
}

// Create root and render
const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

export default App;