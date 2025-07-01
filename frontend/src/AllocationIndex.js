import React, { useState } from 'react';
import AuthUser from './AuthUser';
import { useEffect } from 'react';

const AllocationIndex = () => {

  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);


  useEffect(() => {
    const fetchData =  async() => {
      try {
        const data = await AuthUser();
        setIsAuthenticated(true);
        setData(data);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchData();
  }, []);

  if (error) {
    return <p>{error} <a href="/login">Click Here</a> </p>;
  }
  

  if(isAuthenticated){
    return (
      <div style={styles.buttonContainer}>
        <h1> Request Service  </h1>
  
        <a href="add-switch" style={styles.button}>Add Switch</a>
        <a href="form" style={styles.button}>Request Resource</a>
        <a href="view-user-resource" style={styles.button}>View User Resources</a>
        <a href="view-all-resource" style={styles.button}>View All Resources</a>
  
      </div>
    )
  }

 
}

const styles = {
  buttonContainer: {
    display: 'flex',
    'flex-direction': 'column',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh', // Full height of viewport
  },
  button: {
    display: 'inline-block',
    padding: '20px 40px',
    margin: '10px',
    fontSize: '24px',
    textDecoration: 'none',
    color: '#fff',
    backgroundColor: '#4CAF50', // Green
    border: 'none',
    borderRadius: '8px',
    transition: 'background-color 0.3s',
    width: '15%'
  },
};


export default AllocationIndex