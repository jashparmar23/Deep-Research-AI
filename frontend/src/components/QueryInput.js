import React, { useState } from 'react';
import '../styles/QueryInput.css';

const QueryInput = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) {
      alert('Please enter a research query');
      return;
    }
    onSubmit(query.trim(), startDate, endDate);
  };

  return (
    <div className="query-input-container">
      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-group">
          <label htmlFor="query">Research Query</label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research question (e.g., 'trending topics about AI in 2024')"
            rows="3"
            required
            disabled={loading}
          />
        </div>

        <div className="date-inputs">
          <div className="input-group">
            <label htmlFor="start-date">Start Date (Optional)</label>
            <input
              type="date"
              id="start-date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="end-date">End Date (Optional)</label>
            <input
              type="date"
              id="end-date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner"></span>
              Researching...
            </>
          ) : (
            'Start Research'
          )}
        </button>
      </form>
    </div>
  );
};

export default QueryInput;
