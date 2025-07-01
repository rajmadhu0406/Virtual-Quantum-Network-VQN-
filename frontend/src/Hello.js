import React from 'react'
import axios from 'axios';
import { useState, useEffect } from 'react';



const Hello = () => {
    const [result, setResult] = useState(null);

    const handleClick = async () => {
        try {
            // Make the API call using axios.get
            const name = "reactNameButton"

            const response = await axios.get(`http://localhost:8000/api/sayname/${name}`);
            console.log(response.data);
            // Save the result in state
            setResult(response.data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    return (
        <div>
            <button onClick={handleClick}>Send API Request</button>
            {result && (
                <div>
                    <h2>Result:</h2>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );


}

export default Hello