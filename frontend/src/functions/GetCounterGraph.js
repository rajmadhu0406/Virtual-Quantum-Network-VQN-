import React, { useState } from 'react';
import styles from '../styles/GetCounterGraph.module.css';
import { ApiFetchWithToken } from '../ApiUtility';
import GraphPage from './GraphPage';

function GetCounterGraph() {
    // State to store input values
    const [numChannels, setNumChannels] = useState('');
    const [binWidth, setBinWidth] = useState('');
    const [nValues, setNValues] = useState('');

    const [graphType, setGraphType] = useState('bar'); // Default to line graph
    const [graphData, setGraphData] = useState(null);

    const [error, setError] = useState(null);

    const [showForm, setShowForm] = useState(true); // Toggle for form visibility
    const [showGraph, setShowGraph] = useState(false); // Toggle for graph visibility

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Basic validation
        if (numChannels < 1 || numChannels > 8 || binWidth <= 0 || nValues <= 0) {
            alert('Please provide valid values');
            return;
        }

        try {

            const payload = { "numChannels": numChannels, "bin_width": binWidth, "n_values": nValues };

            const result = await ApiFetchWithToken('http://localhost:8000/counter/graph', {
                method: 'POST',
                credentials: "include",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });


            console.log("get_counter_graph_ : ", result);

            if (result == null || !result) {
                alert("no response from server :(");
            }
            else if ('error' in result) {
                setError(result["error"])
            }
            else {
                setGraphData(result);
                setShowForm(false); // Hide form
                setShowGraph(true); // Show graph
            }


        } catch (error) {
            console.error('Error fetching data:', error);
            setError(error.message);
        }
    }

    const handleRetry = () => {
        setShowForm(true);  // Show form again
        setShowGraph(false); // Hide graph
        setGraphData(null); // Clear the graph data
    };


    return (
        <div className={styles.container}>
            <h1 className={styles.heading}>Get Counter Graph </h1>

            <div className={`${styles.form_container} ${showForm ? styles['form-container-visible'] : styles['form-container-hidden']}`}>
                
                <form className={styles.form_style} onSubmit={handleSubmit}>
                    {/* <div className={styles.input_container}> */}
                        <label>
                            Number of Channels:
                            </label>
                            <input
                                className={styles.input_style}
                                type="number"
                                value={numChannels}
                                onChange={(e) => setNumChannels(e.target.value)}
                                min="1"
                                max="8"
                                required
                            />
                        
                    {/* </div> */}
                    {/* <div className={styles.input_container}> */}
                        <label>
                            Bin Width (in picoseconds):
                            </label>
                            <input
                                className={styles.input_style}
                                type="number"
                                value={binWidth}
                                onChange={(e) => setBinWidth(e.target.value)}
                                min="1"
                                required
                            />
                        
                    {/* </div> */}
                    {/* <div className={styles.input_container}> */}
                        <label>
                            Number of Bins:
                            </label>
                            <input
                                className={styles.input_style}
                                type="number"
                                value={nValues}
                                onChange={(e) => setNValues(e.target.value)}
                                min="1"
                                required
                            />
                        
                    {/* </div> */}
                    {/* <div> */}
                        <button className={styles['button-style']} type="submit">Submit</button>
                    {/* </div> */}
                </form>

                {error && <p style={{ color: 'red' }}>Error: {error}</p>}

            </div>

            <div className={`${styles.graph_container} ${showGraph ? styles['graph-container-visible'] : styles['graph-container-hidden']}`}>
                {graphData && <GraphPage graphType={graphType} data={graphData} />}
                <button className={styles['button-style']} onClick={handleRetry}>Retry</button>
                <div className={styles.graph_info}>
                    <p>Number of Channels: {numChannels}</p>
                    <p>Bin Width: {binWidth}</p>
                    <p>Number of Bins: {nValues}</p>
                </div>
            </div>

        </div>
    );
}


export default GetCounterGraph