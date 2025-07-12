import React, { useState, useEffect } from 'react';
import styles from '../styles/TimeTaggerStatus.module.css'
import {ApiFetchWithToken} from '../ApiUtility';


function TimeTaggerStatus() {
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch data from API when the component is mounted
    const fetchData = async () => {
      try {
        const res = await ApiFetchWithToken('http://localhost:8000/timetagger/status', {
          method: 'GET',
          credentials: "include", // Include JWT cookie in the request
        });

        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }

        const data = await res.json();
        setResponse(data);
      } catch (err) {
        console.error("Failed to fetch data:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []); // Empty dependency array means this effect runs once when the component mounts


  return (
    <body>
      <h2 className={styles.heading}>TimeTagger Status</h2>
      <div>
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
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

export default TimeTaggerStatus