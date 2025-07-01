import React, { useState } from 'react';
import './Test.css'

const Test = () => {

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    const [response, setResponse] = useState('');
    const [error, setError] = useState('');
    const [showDialog, setShowDialog] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setError('');
        setResponse('');

        setShowDialog(true);

        await sleep(5000);
        setResponse('success');


        console.log('inside handleSubmit\n')
    }

    const handleDialogCancel = () => {
        
        setShowDialog(false);
    };

    const handleDialogNavigate = () => {
        setShowDialog(false);
        // Navigate to another URL
        window.location.href = 'url'; // Replace 'url' with your desired URL
    };


    return (
        <div className="container">
            <button className='form-button' type="button" onClick={handleSubmit}>Submit</button>

            {error && <div className="error">{error}</div>}
            {/* {loading && <div className="loading">Loading...</div>}
            {response && <div className="response">Response: {response}</div>} */}

            {/* Dialog Box */}
            {showDialog && (
                <div className="dialog-background" >
                    <div className="dialog-content">
                        <div className="dialog-header">

                            {response === '' ? (
                                <div className='loading-container'>
                                    <div className="loading-icon">  </div>
                                    <br />
                                    <div> Loading... </div>
                                </div>
                            ) : response === 'success' ? (
                                <div className="success-icon">&#10004;</div>
                            ) : (
                                <div className="error-icon">&#10006;</div>
                            )}

                        </div>
                        <div className="dialog-body">{response}</div>
                        <div className="dialog-footer">
                            <button className="cancel-button" onClick={handleDialogCancel}>Cancel</button>
                            <button className="navigate-button" onClick={handleDialogNavigate}>Navigate</button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    )
}

export default Test