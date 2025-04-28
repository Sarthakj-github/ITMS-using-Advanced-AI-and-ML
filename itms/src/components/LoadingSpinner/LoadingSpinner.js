import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ size = 'medium', color = 'blue' }) => {
  const sizeClass = {
    small: '20px',
    medium: '40px',
    large: '60px'
  };

  const colorClass = {
    blue: 'var(--blue)',
    green: 'var(--green)',
    red: 'var(--red)',
    yellow: 'var(--yellow)'
  };

  return (
    <div 
      className="loading-spinner"
      style={{
        width: sizeClass[size] || sizeClass.medium,
        height: sizeClass[size] || sizeClass.medium,
        borderTopColor: colorClass[color] || colorClass.blue
      }}
    ></div>
  );
};

export default LoadingSpinner;