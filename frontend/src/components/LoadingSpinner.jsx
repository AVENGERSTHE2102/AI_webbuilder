import React from 'react';
import './LoadingSpinner.css';

function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="loading-spinner">
      <div className="spinner-circle"></div>
      <p className="spinner-message">{message}</p>
    </div>
  );
}

export default LoadingSpinner;
