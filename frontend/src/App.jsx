import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import SplashPage from './pages/SplashPage';
import UserDashboard from './pages/UserDashboard';
import './styles/index.css';

const ProtectedRoute = ({ element }) => {
  const token = localStorage.getItem('authToken');
  return token ? element : <Navigate to="/" />;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<SplashPage />} />
          <Route
            path="/dashboard"
            element={<ProtectedRoute element={<UserDashboard />} />}
          />
          {/* OAuth Callback Routes (to be implemented) */}
          {/* <Route path="/callback/facebook" element={<OAuthCallback />} />
          <Route path="/callback/instagram" element={<OAuthCallback />} /> */}
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
