import React, { useState, useEffect } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import axios from "axios";

const ProtectedRoute = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);
  const location = useLocation();
  // Helper function to decode the JWT token and check if it's expired


  useEffect(() => {
    const checkToken = async () => {

      try {

        const response = await fetch("http://localhost:8000/auth/verify_token", {
          method: 'POST',
          credentials: 'include',
        });


        if (response.status === 200) {

          const data = await response.json();
          
          console.debug(data);

          if(data.refresh === true) {
            console.debug("refreshing token...");
            const refresh_response = await fetch("http://localhost:8000/auth/refresh_token", {
              method: 'POST',
              credentials: 'include',
            });

            setIsLoading(false);
            setIsAuthorized(true);
          }
          else if(data.authenticated === true) {
            setIsLoading(false);
            setIsAuthorized(true);
          }
          else{
            setIsLoading(false);
            setIsAuthorized(false);
          }
        
        }
        else {
          // If status is not 200 OK (e.g., 401 Unauthorized), handle as unauthorized
          setIsLoading(false);
          setIsAuthorized(false);
        }

      } catch (err) {
        console.error("Failed to verify token:", err);
        setIsLoading(false);
        setIsAuthorized(false);
        return;
      }

    };

    checkToken();

  }, []);


  if (isLoading) {
    // Optionally, show a loading spinner or placeholder here
    return <div>Loading...</div>;
  }

  if (!isAuthorized) {
    return <Navigate to="/login" state={{ message: 'Please log in to continue.', from: location }} />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
