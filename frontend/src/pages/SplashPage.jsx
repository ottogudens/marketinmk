import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { clientService, sessionService, oauthService } from '../services/api';
import '../styles/splash.css';

const SplashPage = () => {
  const navigate = useNavigate();
  const { login, startSession } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Detectar datos de conexión desde URL params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const macAddress = params.get('mac');
    const ipAddress = params.get('ip');

    if (macAddress && ipAddress) {
      sessionStorage.setItem('macAddress', macAddress);
      sessionStorage.setItem('ipAddress', ipAddress);
    }
  }, []);

  const handleOAuthLogin = async (provider) => {
    setIsLoading(true);
    setError(null);

    try {
      // Redirigir a OAuth
      if (provider === 'facebook') {
        window.location.href = oauthService.getFacebookAuthUrl();
      } else if (provider === 'instagram') {
        window.location.href = oauthService.getInstagramAuthUrl();
      }
    } catch (err) {
      setError('Error al iniciar sesión. Intenta de nuevo.');
      console.error(err);
      setIsLoading(false);
    }
  };

  return (
    <div className="splash-container">
      {/* Header con branding */}
      <header className="splash-header">
        <div className="logo">
          <h1>🏪 Mi Negocio</h1>
          <p>Conecta y disfruta ofertas exclusivas</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="splash-main">
        <div className="welcome-section">
          <h2>¡Bienvenido!</h2>
          <p>Conéctate a través de tu red social y obtén acceso a ofertas especiales</p>
        </div>

        {error && <div className="error-banner">{error}</div>}

        {/* OAuth Buttons */}
        <div className="oauth-section">
          <button
            className="oauth-btn facebook-btn"
            onClick={() => handleOAuthLogin('facebook')}
            disabled={isLoading}
          >
            <span className="icon">f</span>
            <span>Conectar con Facebook</span>
          </button>

          <button
            className="oauth-btn instagram-btn"
            onClick={() => handleOAuthLogin('instagram')}
            disabled={isLoading}
          >
            <span className="icon">📷</span>
            <span>Conectar con Instagram</span>
          </button>

          <button
            className="oauth-btn whatsapp-btn"
            onClick={() => handleOAuthLogin('whatsapp')}
            disabled={isLoading}
          >
            <span className="icon">💬</span>
            <span>Conectar con WhatsApp</span>
          </button>
        </div>

        {isLoading && <div className="loading">Cargando...</div>}

        {/* Demo / Admin Quick Login Link */}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <button
            style={{
              background: 'rgba(255,255,255,0.08)',
              border: '1px solid rgba(255,255,255,0.2)',
              color: '#94a3b8',
              fontSize: '0.8rem',
              padding: '6px 14px',
              borderRadius: '20px',
              cursor: 'pointer'
            }}
            onClick={() => {
              const username = prompt('Usuario Administrador:', 'admin');
              const password = prompt('Contraseña Administrador:', 'Admin1234!');
              if (username && password) {
                // Autenticar contra token API de Django
                fetch(`${import.meta.env.VITE_API_URL || '/api'}/token-auth/`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ username, password })
                })
                .then(res => res.json())
                .then(data => {
                  if (data.token) {
                    localStorage.setItem('authToken', data.token);
                    navigate('/admin/dashboard');
                  } else {
                    alert('Credenciales incorrectas');
                  }
                })
                .catch(() => alert('Error de conexión al servidor de autenticación'));
              }
            }}
          >
            🔐 Acceso Administrador (Panel Control)
          </button>
        </div>
      </main>

      {/* Footer con info */}
      <footer className="splash-footer">
        <p>Tus datos están protegidos. <a href="#privacy">Política de privacidad</a></p>
      </footer>
    </div>
  );
};

export default SplashPage;
