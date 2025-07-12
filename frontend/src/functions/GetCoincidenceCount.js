import React, { useState } from 'react';
import styles from '../styles/GetCoincidenceCount.module.css';
import { ApiFetchWithToken } from '../ApiUtility';


function GetCoincidenceCount() {

  const [data, setData] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [formInputs, setFormInputs] = useState({ binwidth: 0, n_bins: 0 });

  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [ws, setWs] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormInputs((prev) => ({ ...prev, [name]: parseInt(value, 10) }));
  };

  const handleDisconnect = () => {
    ws.close();
    setResponse("Disconnected by user");
  };

  const handleRestart = () => {
    setResponse(null);
    setError(null);
    setWs(null);
    setIsConnected(false);
    setData([]);
    setFormInputs({ binwidth: 0, n_bins: 0 });
  }

  const handleSubmit = (e) => {
    e.preventDefault();

    setError(null);
    setResponse(null);

    // Validate inputs
    const binwidth = parseInt(formInputs.binwidth, 10);
    const n_bins = parseInt(formInputs.n_bins, 10);

    if (isNaN(binwidth) || isNaN(n_bins) || binwidth <= 0 || n_bins <= 0) {
      alert("Please enter valid positive numbers for binwidth and n_bins.");
      return;
    }

    // Start WebSocket connection
    const websocket = new WebSocket("ws://localhost:8000/coincidence/ws/coincidence_count");
    setWs(websocket);

    websocket.onopen = () => {
      console.log("WebSocket connected");

      // Send inputs to server
      websocket.send(JSON.stringify({
        binwidth: formInputs.binwidth,
        n_bins: formInputs.n_bins
      }));


      setIsConnected(true); // Show table once WebSocket is connected
    };

    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        console.log("Received message from server ws:", message);

        if (message.error) {
          setError(message.error)
          ws.close();
        }
        else if (message.success) {
          setResponse(message.success)
          ws.close();
        }
        else {
          // Add new data to the table
          setData((prevData) => [...prevData, message]);
        }

      } catch (error) {
        console.error("Error parsing WebSocket message:", event.data);
        setError("Error parsing WebSocket message");
      }
    };

    websocket.onclose = () => {
      console.log("WebSocket closed");
      setResponse("Websocket Connection Disconnected!");
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setError(error);
    };
  };



  return (
    <div>

      <div className={styles.heading}>
        <h1>Get Coincidence Count:</h1>
      </div>




      {!isConnected && (
        // <form onSubmit={handleSubmit}>
        <form className={styles.form_container} onSubmit={handleSubmit}>
          <label htmlFor="binwidth">Binwidth (seconds): </label>
          <input
            type="number"
            step="1"
            name="binwidth"
            value={formInputs.binwidth}
            onChange={handleInputChange}
            required
          />
          <label htmlFor="n_bins">Number of Bins: </label>
          <input
            type="number"
            name="n_bins"
            step="1"
            value={formInputs.n_bins}
            onChange={handleInputChange}
            required
          />
          <button type="submit">Start</button>
        </form>
      )}

      {isConnected && (
        <div>
          <button onClick={handleDisconnect}> Disconnect </button>
          <button onClick={handleRestart}> Reset </button>
          <table border="1" style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>Elapsed Time</th>
                <th>CH1 Count</th>
                <th>CH2 Count</th>
                <th>Coincidence Count</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index}>
                  <td>{row.elapsed_time}</td>
                  <td>{row.ch1_count}</td>
                  <td>{row.ch2_count}</td>
                  <td>{row.coincidence_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}


      <div>
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      </div>

      <div>
        {response && <p style={{ color: 'green' }}>Response: {response}</p>}
      </div>


    </div>


  );


};

export default GetCoincidenceCount