import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from 'config/apiConfig';
import { useNavigate } from 'react-router-dom'

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  const checkAuthStatus = async () => {
    try {
      const response = await apiClient.get('/user/profile', {
        withCredentials: true
      });

      if (response.data) {
        setUser({
          ...response.data,
          plan: response.data.plan || 'free'
        });
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Auth check error:', error);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Debug state changes
  useEffect(() => {
  }, [loading, isAuthenticated, user]);

  const login = async (credentials) => {
    try {
      const response = await apiClient.post('/user/login', credentials, {
        withCredentials: true
      });

      const userData = response.data;

      // First set the user data
      setUser({
        ...userData,
        plan: userData.plan || 'free'
      });

      // Then set authenticated status
      setIsAuthenticated(true);

      // Check auth status to ensure everything is synced
      await checkAuthStatus();

      return {
        success: true,
        user: userData
      };
    } catch (error) {
      console.error('Login failed:', error);
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed'
      };
    }
  };

  const logout = async () => {
    try {
      await apiClient.get('/user/logout', {
        withCredentials: true
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
