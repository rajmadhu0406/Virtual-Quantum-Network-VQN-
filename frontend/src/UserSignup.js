import React, { useState } from 'react';
import './UserSignup.css';
import { Link, useNavigate } from 'react-router-dom';


const UserSignup = () => {

    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [age, setAge] = useState('');
    const [password, setPassword] = useState('');
    const [institution, setInstitution] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    let navigate = useNavigate();


    const handleSignup = async (event) => {
        event.preventDefault();

        // Check if any required field is empty
        if (!firstName || !lastName || !email || !age || !password || !institution) {
            setErrorMessage('All fields are required.');
            return;
        }

        // Check if age is a number
        if (isNaN(age) || age === '') {
            setErrorMessage('Age must be a number.');
            return;
        }

        const allowedDomains = ['ncsu.edu', 'umich.edu'];
        const emailDomain = email.split('@')[1];
        if (!allowedDomains.includes(emailDomain)) {
            setErrorMessage('Email address domain not allowed.');
            return;
        }

        // Basic email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setErrorMessage('Invalid email address.');
            return;
        }

        // Password validation
        const passwordRegex = /^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$/;
        if (!passwordRegex.test(password)) {
            setErrorMessage('Password must contain at least 8 characters with one uppercase letter, one special character, and one digit.');
            return;
        }

        // Implement signup logic here
        console.log('First Name:', firstName);
        console.log('Last Name:', lastName);
        console.log('Email:', email);
        console.log('Age:', age);
        console.log('Institution:', institution);


        //send request to backend
        try {
            const response = await fetch('http://localhost:8000/api/user/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    firstName: firstName,
                    lastName: lastName,
                    username: username,
                    email: email,
                    institution: institution,
                    age: age,
                    password: password
                })
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            console.log("data : ", data);

            if ("error" in data || data.hasOwnProperty('error')) {
                throw new Error(data['error']);
            }

            // Clear form fields after signup
            setFirstName('');
            setLastName('');
            setEmail('');
            setAge('');
            setPassword('');
            setInstitution('');
            setErrorMessage('');
            setUsername('');
            
            setSuccessMessage('Signup Successful');
            navigate('/login');

        } catch (error) {
            console.error('Login error:', error);
            setErrorMessage(error.toString());
        }

    };

    //  id = Column(Integer, primary_key=True, unique=True)
    // firstName = Column(String(250))
    // lastName = Column(String(250))
    // username = Column(String(250), nullable=False)
    // age = Column(Integer)
    // institution = Column(String(250))
    // email = Column(String(250), nullable=False)  # Make email field required
    // hash_password = Column(String(250), nullable=False)  # Make password field required
    // disabled = bool = False

    return (
        <div className="signup-container">
            <div className="signup-box">
                <h2>Sign Up</h2>
                <input
                    type="text"
                    placeholder="First Name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="Last Name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="Age"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="Institution"
                    value={institution}
                    onChange={(e) => setInstitution(e.target.value)}
                />
                <button onClick={handleSignup}>Sign Up</button>
                <p>Already have an account? <Link to="/login">Login here</Link></p> {/* Link to the signup page */}

                {errorMessage && <p className="error-message">{errorMessage}</p>}
                {successMessage && <p className="success-message">{successMessage}</p>}

            </div>
        </div>
    );

};

export default UserSignup;
