import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import SplashPage from './pages/SplashPage';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import OAuthCallback from './pages/OAuthCallback';
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
          <Route
            path="/admin/dashboard"
            element={<ProtectedRoute element={<AdminDashboard />} />}
          />
          {/* OAuth Callback Routes */}
          <Route path="/callback/:provider" element={<OAuthCallback />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
