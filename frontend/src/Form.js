import React, { useState } from 'react';
import './Form.css';

const MyForm = () => {
  const [username, setUsername] = useState('');
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

    if (!username.trim()) {
      setError('Username cannot be empty');
      return;
    }

    if (channels <= 0) {
      setError('Channels must be greater than zero');
      return;
    }

    // Open the dialog box
    setShowDialog(true);

    const timestamp = new Date().toISOString();

    try {

      const response = await fetch('http://localhost:8000/api/channel/allocate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Timestamp': timestamp,
        },
        body: JSON.stringify({ "username": username, "channels_needed": channels }),
      });

      const data = await response.json();
      console.log(data)
      
      if ("error" in data || data.hasOwnProperty('error')) {
        console.log(data.error)
        setError('Failed to allocate channels due to : '+ data.error);
        setDialogResponse('Failed to allocate channels due to : '+ data.error);
        setDialogState('error');
        return;
      }
      else{
        console.log("data.display : ", data.display);
        const displayArray = data.display;
        setDialogResponse(displayArray);
      }
      

      if (data.hasOwnProperty('error')) {
        setDialogState('error');
      } else {
        setDialogState('success');
      }


    } catch (error) {
      console.log("\n\nError has occured\n\n")
      console.error('Error:', error);
      setError('Failed to allocate channels due to : ', error);
      setDialogState('error');
    } finally {

    }
  };


  const handleDialogCancel = () => {
    setUsername('');
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
      <h1> Request Service Form </h1>
      <form id='resource-form' name='resource-form' onSubmit={handleSubmit}>
        <label>
          Username:
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </label>
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
};

export default MyForm;