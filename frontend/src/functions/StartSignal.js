import React, { useState } from 'react';
import styles from '../styles/StartSignal.module.css';
import {ApiFetchWithToken} from '../ApiUtility';

function StartSignal() {
  const [selectedChannels, setSelectedChannels] = useState([]);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // alert(`\nSelected Channels: ${typeof(selectedChannels)}`);

    try {

      console.debug("channels : " + selectedChannels)

      const payload = { "channels": selectedChannels };

      console.log(JSON.stringify(payload));

      const res = await ApiFetchWithToken('http://localhost:8000/timetagger/start_test_signal', {
        method: 'POST',
        credentials: "include", // Include JWT cookie in the request
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        console.error("Server responded with an error:", res.status, res.statusText);
        const errorText = await res.text(); // To get the actual error message from the server
        throw new Error(`HTTP error! Status: ${res.status}, Message: ${errorText}`);
      }


      const result = await res.json();


      if (result == null || !result) {
        alert("no response from server :(");
      }
      else if ('error' in result) {
        setError(result["error"])
      }
      else {
        setResponse(result);
      }

    } catch (e) {
      console.log(e);
    }

  };

  const handleChannelChange = (e) => {
    const value = parseInt(e.target.value, 10);
    setSelectedChannels(
      e.target.checked
        ? [...selectedChannels, value]
        : selectedChannels.filter((channel) => channel !== value)
    );
  };

  return (
    <body>

      <div className={styles.heading}>
        <h1> Start Signal Form: </h1>
      </div>

      <form className={styles.start_signal_form_container} onSubmit={handleSubmit}>
        <div>
          <h2>Select Channels :</h2>
          {[...Array(8).keys()].map((i) => (
            <div key={i}>
              <input
                type="checkbox"
                value={i + 1}
                onChange={handleChannelChange}
                checked={selectedChannels.includes(i + 1)}
              />
              Channel {i + 1}
            </div>
          ))}
        </div>
        <br></br>
        <button type="submit">Submit</button>
      </form>

      <div>
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      </div>

      <div>
        {/* Display the response if it exists */}
        {response && (
          <div>
            <h3>Response from Server:</h3>
            <pre>{JSON.stringify(response, null, 2)}</pre> {/* Prettify JSON */}
          </div>
        )}
      </div>


    </body>
  );
}



export default StartSignal