import React from 'react';
import '../styles/ResultDisplay.css';

const ResultDisplay = ({ result, loading, error }) => {
  if (loading) {
    return (
      <div className="result-container loading">
        <div className="loading-spinner">
          <div className="spinner-large"></div>
          <p>Processing your research query...</p>
          <p className="loading-steps">
            Gathering data from social media, news sources, and web content...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="result-container error">
        <div className="error-message">
          <h3>❌ Research Error</h3>
          <p>{error}</p>
          <p>Please try again with a different query or check your connection.</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="result-container empty">
        <div className="empty-state">
          <h3>🚀 Ready to Research</h3>
          <p>Enter your research query above to get started with AI-powered deep research.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="result-container">
      <div className="result-header">
        <h2>📊 Research Summary</h2>
      </div>
      <div className="result-content">
        <div className="summary-text">
          {result.split('\n').map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultDisplay;
