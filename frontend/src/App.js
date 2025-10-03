import React, { useState } from 'react';
import './styles/App.css';
import QueryInput from './components/QueryInput';
import ResultDisplay from './components/ResultDisplay';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleQuerySubmit = async (searchQuery, startDate, endDate) => {
    setLoading(true);
    setError('');
    setResult('');

    try {
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          start_date: startDate,
          end_date: endDate
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch research data');
      }

      const data = await response.json();
      setResult(data.final_summary || 'No summary available');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔬 Deep Research Agent</h1>
        <p>AI-powered research with social media and web data aggregation</p>
      </header>

      <main className="App-main">
        <QueryInput onSubmit={handleQuerySubmit} loading={loading} />
        <ResultDisplay result={result} loading={loading} error={error} />
      </main>
    </div>
  );
}

export default App;
