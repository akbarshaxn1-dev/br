import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

let API_URL = process.env.REACT_APP_BACKEND_URL;

// Ensure API_URL uses HTTPS if window is HTTPS
if (typeof window !== 'undefined' && window.location.protocol === 'https:' && API_URL && API_URL.startsWith('http:')) {
  API_URL = API_URL.replace('http:', 'https:');
}

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'));

  useEffect(() => {
    if (accessToken) {
      verifyToken();
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setUser(response.data);
    } catch (error) {
      if (error.response?.status === 401 && refreshToken) {
        await refreshAccessToken();
      } else {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  const refreshAccessToken = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/auth/refresh`, null, {
        params: { refresh_token: refreshToken }
      });
      const newAccessToken = response.data.access_token;
      setAccessToken(newAccessToken);
      localStorage.setItem('access_token', newAccessToken);
      await verifyToken();
    } catch (error) {
      logout();
    }
  };

  const login = async (email, password, otpCode = null) => {
    const response = await axios.post(`${API_URL}/api/auth/login`, {
      email,
      password,
      otp_code: otpCode
    });
    
    const { access_token, refresh_token, user: userData } = response.data;
    
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    setAccessToken(access_token);
    setRefreshToken(refresh_token);
    setUser(userData);
    
    return userData;
  };

  const register = async (userData) => {
    const response = await axios.post(`${API_URL}/api/auth/register`, userData);
    return response.data;
  };

  const logout = async () => {
    try {
      if (refreshToken) {
        await axios.post(`${API_URL}/api/auth/logout`, null, {
          params: { refresh_token: refreshToken },
          headers: { Authorization: `Bearer ${accessToken}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setAccessToken(null);
      setRefreshToken(null);
      setUser(null);
    }
  };

  const getAuthHeader = () => ({
    Authorization: `Bearer ${accessToken}`
  });

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    getAuthHeader,
    accessToken,
    isAuthenticated: !!user
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
