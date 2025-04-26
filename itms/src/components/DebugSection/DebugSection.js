import React, { useState } from 'react';
import './DebugSection.css';

const DebugSection = () => {
  const [debugOutput, setDebugOutput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const processImage = async () => {
    if (!selectedFile) {
      alert('Please select an image first');
      return;
    }
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    try {
      const response = await fetch('http://localhost:5000/debug', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        setDebugOutput(
          <div>
            <p>Processed image:</p>
            <img 
              src={`${data.debug_path}?${Date.now()}`} 
              alt="Debug output" 
              style={{ maxWidth: '100%' }} 
            />
          </div>
        );
      } else {
        setDebugOutput('Error processing image');
      }
    } catch (error) {
      console.error('Error processing debug image:', error);
      setDebugOutput('Error processing image');
    }
  };

  return (
    <div className="debug-section">
      <h2>Debug Vehicle Detection</h2>
      <input 
        type="file" 
        id="debugInput" 
        accept="image/*" 
        onChange={handleFileChange}
      />
      <button id="debugBtn" onClick={processImage}>
        Process Image
      </button>
      <div id="debugOutput">{debugOutput}</div>
    </div>
  );
};

export default DebugSection;