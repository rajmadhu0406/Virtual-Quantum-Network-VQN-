import React, { useState } from 'react';
import styles from '../styles/GetCountRate.module.css'
import { ApiFetchWithToken } from '../ApiUtility';

function GetCountRate() {
    const [numChannels, setNumChannels] = useState(null);
    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        // alert(`\nSelected Channels: ${selectedChannels.join(', ')}`);

        try {

            const payload = { "numChannels": numChannels};

            console.log(JSON.stringify(payload));

            const res = await ApiFetchWithToken('http://localhost:8000/countrate/get_countrate_data', {
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
            setError(e.message);
        }

    };

    // const handleChannelChange = (e) => {
    //     const value = parseInt(e.target.value, 10);
    //     setSelectedChannels(
    //         e.target.checked
    //             ? [...selectedChannels, value]
    //             : selectedChannels.filter((channel) => channel !== value)
    //     );
    // };

    return (
        <body>

            <div className={styles.heading}>
                <h1> Get CountRate: </h1>
            </div>

            <form className={styles.form_container_channels} onSubmit={handleSubmit}>
                <div>
                    <h2>Enter Number of Channels:</h2>
                    <input
                        type="number"
                        min="1"
                        max="8"
                        value={numChannels}
                        onChange={(e) => setNumChannels(Number(e.target.value))}
                    />
                    <p style={{ color: 'purple', fontSize: '150%' }}>Enter a number between 1 and 8</p>
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
                    <div className={styles.table_container}>
                        <h3>Response from Server:</h3>
                        <br></br>
                        <table border="1" style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    <th>Channel</th>
                                    <th>Data</th>
                                </tr>
                            </thead>
                            <tbody>
                                {response.channels.map((channel, index) => (
                                    <tr key={index}>
                                        <td>{channel}</td>
                                        <td>{response.data[index]}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </body>
    );
}


export default GetCountRate