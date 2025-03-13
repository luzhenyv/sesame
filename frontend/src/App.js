import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': "*"
  },
});

function App() {
  const [message, setMessage] = useState('Loading...');
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await api.get('/api/hello');
        setMessage(response.data.message);
        setError(null);
      } catch (err) {
        console.error('Error fetching message:', err);
        setMessage('Error loading message');
        setError(err.message);
      }
    };

    fetchMessage();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>{message}</h1>
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      </header>
    </div>
  );
}

export default App; 