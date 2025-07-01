import React, { useState, useEffect } from 'react'
import './CreateSwitch.css'

const CreateSwitch = () => {

    useEffect(() => {
        const meta = document.createElement('meta');
        meta.httpEquiv = 'Content-Security-Policy';
        meta.content = 'upgrade-insecure-requests';
        document.head.appendChild(meta);
        return () => {
          document.head.removeChild(meta);
        };
      }, []);
    
    const [active, setActive] = useState(true);
    const [channels, setChannels] = useState(0);
    const [apiResponse, setApiResponse] = useState('');
    const [error, setError] = useState('');

    const [showDialog, setShowDialog] = useState(false);
    const [dialogResponse, setDialogResponse] = useState('');
    const [dialogState, setDialogState] = useState('');


    const handleSubmit = async (event) => {
        event.preventDefault();

        setError('');
        setApiResponse('');

        setDialogResponse('');
        setDialogState('');

        if (channels <= 0) {
            setError('Channels must be greater than zero');
            return;
        }

        setShowDialog(true);

        const timestamp = new Date().toISOString();

        try {
            const response = await fetch('http://localhost:8000/api/switch/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Timestamp': timestamp,
                },
                body: JSON.stringify({ "channels_count": channels, "active": active }),
            });

            const data = await response.json();

            setApiResponse(data);

            console.debug(apiResponse);


            if (data.hasOwnProperty('error')) {
                setDialogResponse(data.error);
                setDialogState('error');
            } else {
                setDialogResponse('Switch Creation Successful!');
                setDialogState('success');
            }


        } catch (error) {
            console.error('Error:', error);
            setError('Failed to allocate channels');
        } finally {

        }
    };

    const handleDialogCancel = () => {
        setChannels(0);
        setShowDialog(false);
    };

    const handleDialogNavigate = () => {
        setShowDialog(false);
        // Navigate to another URL
        window.location.href = 'allocateindex'; // Replace 'url' with your desired URL
    };

    return (
        <div className="container">
            <h1> Create Switch Form </h1>
            <form id='resource-form' name='resource-form' onSubmit={handleSubmit}>
              
                <br />
                <label>
                    Channels:
                    <input
                        type="number"
                        value={channels}
                        onChange={(e) => setChannels(parseInt(e.target.value))}
                    />
                </label>
                <br />
                <div style={{ flexDirection: 'row' }}>
                    <button type="submit" style={{ marginRight: '15px' }}>Submit</button>
                    <button type="button" style={{ marginRight: '15px' }} onClick={() => window.location.href = "allocateindex"} > Home </button>
                </div>
            </form>
            {error && <div className="error">{error}</div>}

            {/* Dialog Box */}
            {showDialog && (
                <div className="dialog-background">
                    <div className="dialog-content">
                        <div className="dialog-header">

                            {dialogState === '' ? (

                                <div className='loading-container'>
                                    <div className="loading-icon">  </div>
                                    <br />
                                    <div> Loading... </div>
                                </div>

                            ) : dialogState === 'success' ? (
                                <div className='success-container'>
                                    <div className="success-icon">&#10004;</div>
                                    <div className="dialog-body">{dialogResponse}</div>
                                    <div className="dialog-footer">
                                        <button className="cancel-button" onClick={handleDialogCancel}>Cancel</button>
                                        <button className="navigate-button" onClick={handleDialogNavigate}>Home</button>
                                    </div>
                                </div>
                            ) : (
                                <div className='error-container'>
                                    <div className="error-icon">&#10006;</div>
                                    <div className="dialog-body">{dialogResponse}</div>
                                    <div className="dialog-footer">
                                        <button className="cancel-button" onClick={handleDialogCancel}>Cancel</button>
                                        <button className="navigate-button" onClick={handleDialogNavigate}>Home</button>
                                    </div>
                                </div>
                            )}

                        </div>

                    </div>
                </div>
            )}

        </div>
    );

}

export default CreateSwitch