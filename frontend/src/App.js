import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {

  const [text, setText] = useState("");
  const [result, setResult] = useState("");
  const [history, setHistory] = useState([]);

  const scanInput = async () => {
    const res = await axios.post("http://localhost:5000/scan", {
      text
    });

    setResult(res.data.result);
    loadHistory();
  };

  const loadHistory = async () => {
    const res = await axios.get("http://localhost:5000/history");
    setHistory(res.data);
  };

  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <div className="container">

      <h1>🔐 Smart Cybersecurity Scanner</h1>

      <textarea
        rows="5"
        placeholder="Enter URL / Script / Query"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button onClick={scanInput}>
        Scan Now
      </button>

      <h2>{result}</h2>

      <hr />

      <h3>📜 Scan History</h3>

      {history.map((item, index) => (
        <div className="card" key={index}>
          <p><b>Input:</b> {item.text}</p>
          <p><b>Result:</b> {item.result}</p>
        </div>
      ))}

    </div>
  );
}

export default App;