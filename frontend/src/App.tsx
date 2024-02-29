import React from 'react';
import logo from './logo.svg';
import './App.css';

function App() {

  async function getBackendData() {
    const result = await fetch(`${process.env.REACT_APP_ENDPOINT_URL}/search/test`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        "field": "test"
      })
    });
    
    const data = await result.json();
    console.log(data);
  }

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
        <button onClick={getBackendData}>Get Backend Data</button>
      </header>
    </div>
  );
}

export default App;