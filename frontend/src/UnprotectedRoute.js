import React from 'react'
import { Navigate, Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import axios from 'axios';


function UnprotectedRoute() {

    const [isTokenPresent, setIsTokenPresent] = useState(null);

    useEffect(() => {
        const checkToken = async () => {
            try {
                
                const response = await fetch("http://localhost:8000/auth/verify_token", {
                    method: 'POST',
                    credentials: 'include', 
                });

                const data = await response.json();

                if (response.status === 200 && data.authenticated === true) {
                    setIsTokenPresent(true);
                }
                else{
                    setIsTokenPresent(false);
                }

            } catch (err) {
                if (err.response) {
                    // Handle specific errors
                    const { detail } = err.response.data;
                    console.error("Token verification failed:", detail);
                } else {
                    console.error("Server error or network issue:", err.message);
                }
                setIsTokenPresent(false);
            }
        };

        checkToken();
    }, []);

    if (isTokenPresent) {
        return <Navigate to="/menu" />;
    }

    return <Outlet />;

}

export default UnprotectedRoute