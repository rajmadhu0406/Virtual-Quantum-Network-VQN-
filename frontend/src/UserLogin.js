import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './UserLogin.css';
import axios from 'axios';


const UserLogin = () => {

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (event) => {
    event.preventDefault();

    // Implement your login logic here
    console.log('Username:', username);
    console.log('Password:', password);

    try {

      const response = await fetch('http://localhost:8000/api/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: username,
          password: password
        })
      });

      
      const data = await response.json();
      console.log(data);

      if(data.detail){
        throw new Error(data.detail);
      }

      const access_token = data.access_token;
      
      // Save the token to local storage or state
      localStorage.setItem('token', access_token);

      // Redirect to another page or update UI accordingly
      window.location.href = "/allocateindex";

    } catch (error) {
      console.error(error)
      setError(error.toString());
    }

  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p>{error}</p>}
        <button onClick={handleLogin}>Login</button>
        <p>Don't have an account? <Link to="/signup">Sign Up</Link></p> {/* Link to the signup page */}

      </div>
    </div>
  );
};

export default UserLogin