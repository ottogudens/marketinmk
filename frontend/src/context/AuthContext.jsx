import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [client, setClient] = useState(null);
  const [currentSession, setCurrentSession] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Cargar datos de sesión al iniciar
  useEffect(() => {
    const savedClient = localStorage.getItem('client');
    const savedSession = localStorage.getItem('currentSession');
    const savedToken = localStorage.getItem('authToken');

    if (savedClient && savedToken) {
      try {
        setClient(JSON.parse(savedClient));
        setIsAuthenticated(true);
      } catch (e) {
        console.error('Error parsing saved client:', e);
        localStorage.removeItem('client');
        localStorage.removeItem('authToken');
      }
    }

    if (savedSession) {
      try {
        setCurrentSession(JSON.parse(savedSession));
      } catch (e) {
        console.error('Error parsing saved session:', e);
      }
    }

    setLoading(false);
  }, []);

  const login = (clientData, token) => {
    localStorage.setItem('authToken', token);
    localStorage.setItem('client', JSON.stringify(clientData));
    setClient(clientData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('client');
    localStorage.removeItem('currentSession');
    setClient(null);
    setCurrentSession(null);
    setIsAuthenticated(false);
  };

  const startSession = (sessionData) => {
    localStorage.setItem('currentSession', JSON.stringify(sessionData));
    setCurrentSession(sessionData);
  };

  const endSession = () => {
    localStorage.removeItem('currentSession');
    setCurrentSession(null);
  };

  const value = {
    user,
    setUser,
    client,
    setClient,
    currentSession,
    setCurrentSession,
    isAuthenticated,
    loading,
    login,
    logout,
    startSession,
    endSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
};
