import React, { useState } from 'react';
import styles from '../styles/GetCounterData.module.css';
import {ApiFetchWithToken} from '../ApiUtility';


function GetCounterData() {
    const [numChannels, setNumChannels] = useState('');
    const [binWidth, setBinWidth] = useState('');
    const [nValues, setNValues] = useState('');

    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        // alert(`\nSelected Channels: ${selectedChannels.join(', ')}`);
        try {


            const payload = { "numChannels": numChannels, "bin_width": binWidth, "n_values": nValues };

            console.log(JSON.stringify(payload));

            const res = await ApiFetchWithToken('http://localhost:8000/counter/get_counter_data', {
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
            console.log("get_counter_result_ : ", result);

            if (result == null || !result) {
                alert("no response from server :(");
            }
            else if('error' in result){
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
                <h1> Get Counter Data: </h1>
            </div>

            
            <form className={styles.form_container_channels} onSubmit={handleSubmit}>
                
                    <label htmlFor="numChannels">Number of Channels:</label> 
                    <input
                        id="numChannels"
                        type="number"
                        value={numChannels}
                        onChange={(e) => setNumChannels(e.target.value)}
                        min="1"
                        max="8"
                        required
                    />

                    <label htmlFor="binWidth">Bin Width:</label> 
                    <input
                        id="binWidth"
                        type="number"
                        value={binWidth}
                        onChange={(e) => setBinWidth(e.target.value)}
                        min="1"
                        required
                    />

                    <label htmlFor="nValues">Number of Bins:</label> 
                    <input
                        id="nValues"
                        type="number"
                        value={nValues}
                        onChange={(e) => setNValues(e.target.value)}
                        min="1"
                        required
                    />

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
                        <table border="1" style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    <th>Channels</th>
                                    <th>[{response.channels.join(", ")}]</th>
                                </tr>
                            </thead>
                            <tbody>
                                {response.data.map((bin, binIndex) => (
                                    <tr key={binIndex}>
                                        <td>{`Bin ${binIndex+1}`}</td>
                                        <td>[{bin.join(", ")}]</td>
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


export default GetCounterData