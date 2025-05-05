import React, { useState } from 'react';
import LoadingSpinner from '../LoadingSpinner/LoadingSpinner';
import './DebugSection.css';

const DebugSection = () => {
  const [debugOutput, setDebugOutput] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setDebugOutput(null);
    setError(null);
  };

  const processImage = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }
    
    setIsProcessing(true);
    setError(null);
    setDebugOutput(null);
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    //console.log(formData);
    
    try {
      const response = await fetch('http://localhost:5000/debug', {
        method: 'POST',
        body: formData
      });

      // First check if the response is OK (status 200-299)
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      // Then try to parse as JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`Expected JSON but got: ${text.substring(0, 100)}...`);
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        setDebugOutput(
          <div className="result">
            <p>Processed image:</p>
            <img 
              src={`http://localhost:5000${data.processed_url}`}
              alt="Debug output"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = '/image-error-placeholder.png';
              }}
            />
          </div>
        );
      } else {
        throw new Error(data.message || 'Unknown error from server');
      }
    } catch (error) {
      console.error('Error processing debug image:', error);
      setError(error.message);
      
      // If this is a common error, you could add specific handling:
      if (error.message.includes('Unexpected token') && error.message.includes('<html>')) {
        setError('Server returned an HTML error page. Is the backend running?');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="debug-section">
      <h2>Debug Vehicle Detection</h2>
      
      <div className="debug-controls">
        <label htmlFor="debugInput" className="file-upload-label">
          {selectedFile ? selectedFile.name : 'Choose Image'}
        </label>
        <input 
          type="file" 
          id="debugInput" 
          accept="image/*" 
          onChange={handleFileChange}
          disabled={isProcessing}
        />
        <button 
          id="debugBtn" 
          onClick={processImage}
          disabled={isProcessing || !selectedFile}
        >
          {isProcessing ? (
            <>
              <LoadingSpinner size="small" color="white" />
              <span>Processing...</span>
            </>
          ) : (
            'Process Image'
          )}
        </button>
      </div>
      
      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
          <p>Please ensure:</p>
          <ul>
            <li>The backend server is running at http://localhost:5000</li>
            <li>The endpoint /debug is properly configured</li>
            <li>You're sending a valid image file</li>
          </ul>
        </div>
      )}
      
      <div id="debugOutput" className={debugOutput || isProcessing ? 'show' : ''}>
        {isProcessing ? (
          <div className="processing-message">
            <LoadingSpinner size="medium" color="blue" />
            <p>Processing image...</p>
          </div>
        ) : (
          debugOutput
        )}
      </div>
    </div>
  );
};

export default DebugSection;