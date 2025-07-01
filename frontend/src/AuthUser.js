import React, { useState } from 'react';
import axios from 'axios';

const AuthUser = async (options={}) => {

    const url = "http://localhost:8000/api/auth/current_user"

    const token = localStorage.getItem('token');
    if (!token) {
        throw new Error('No token found. Please login.');
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
    };

    try {
        const response = await axios({
            url,
            ...options,
            headers,
        });
        return response.data;
    } catch (error) {
        if (error.response && error.response.status === 401) {
            // Handle token expiration, logout user, etc.
            localStorage.removeItem('token');
            throw new Error('Session expired. Please login again.');
        }
        throw error;
    }
};

export default AuthUser;