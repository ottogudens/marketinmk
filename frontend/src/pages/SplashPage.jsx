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
  const [activeLoginTab, setActiveLoginTab] = useState('oauth'); // 'oauth' | 'password'

  // User/Password Form State
  const [credentials, setCredentials] = useState({ username: '', password: '' });

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
      if (provider === 'facebook') {
        window.location.href = oauthService.getFacebookAuthUrl();
      } else if (provider === 'instagram') {
        window.location.href = oauthService.getInstagramAuthUrl();
      } else if (provider === 'google') {
        // Redirección OAuth Google
        const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || 'dummy_google_id';
        const redirectUri = `${window.location.origin}/callback/google`;
        window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${redirectUri}&response_type=code&scope=email%20profile`;
      } else if (provider === 'whatsapp') {
        const phone = prompt('Ingresa tu número de WhatsApp con código de país (ej: +56912345678):');
        if (phone) {
          const mac = sessionStorage.getItem('macAddress') || 'AA:BB:CC:DD:EE:FF';
          const res = await clientService.registerFromOAuth({
            social_platform: 'whatsapp',
            social_id: phone,
            email: `${phone.replace('+', '')}@whatsapp.local`,
            full_name: `Usuario WhatsApp ${phone}`,
            phone: phone,
            mac_address: mac
          });
          login(res.data, 'dummy_token');
          navigate('/dashboard');
        }
        setIsLoading(false);
      }
    } catch (err) {
      setError('Error al iniciar sesión. Intenta de nuevo.');
      console.error(err);
      setIsLoading(false);
    }
  };

  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const mac = sessionStorage.getItem('macAddress') || '';
      const res = await clientService.loginWithPassword({
        username: credentials.username,
        password: credentials.password,
        mac_address: mac
      });

      login(res.data.client, res.data.token);
      navigate('/dashboard');
    } catch (err) {
      setError('Usuario o contraseña incorrectos. Revisa los datos ingresados.');
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
          <p>Elige tu método de acceso para conectarte al Wi-Fi gratis</p>
        </div>

        {error && <div className="error-banner">{error}</div>}

        {/* Tab Switcher */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', justifyContent: 'center' }}>
          <button
            style={{
              padding: '8px 16px',
              borderRadius: '20px',
              border: 'none',
              cursor: 'pointer',
              background: activeLoginTab === 'oauth' ? '#6366f1' : '#334155',
              color: '#fff',
              fontWeight: '600'
            }}
            onClick={() => setActiveLoginTab('oauth')}
          >
            🌐 Redes Sociales / Google
          </button>
          <button
            style={{
              padding: '8px 16px',
              borderRadius: '20px',
              border: 'none',
              cursor: 'pointer',
              background: activeLoginTab === 'password' ? '#6366f1' : '#334155',
              color: '#fff',
              fontWeight: '600'
            }}
            onClick={() => setActiveLoginTab('password')}
          >
            🔑 Usuario y Contraseña
          </button>
        </div>

        {/* TAB 1: OAuth & Google */}
        {activeLoginTab === 'oauth' && (
          <div className="oauth-section">
            <button
              className="oauth-btn google-btn"
              style={{ background: '#ea4335' }}
              onClick={() => handleOAuthLogin('google')}
              disabled={isLoading}
            >
              <span className="icon">🔴</span>
              <span>Conectar con Google</span>
            </button>

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
        )}

        {/* TAB 2: Usuario y Contraseña */}
        {activeLoginTab === 'password' && (
          <form onSubmit={handlePasswordLogin} style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '320px', margin: '0 auto' }}>
            <div style={{ textAlign: 'left' }}>
              <label style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '4px', display: 'block' }}>Email / Usuario:</label>
              <input
                type="text"
                required
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #475569', background: '#0f172a', color: '#fff' }}
                value={credentials.username}
                onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                placeholder="usuario@ejemplo.com"
              />
            </div>
            <div style={{ textAlign: 'left' }}>
              <label style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '4px', display: 'block' }}>Contraseña:</label>
              <input
                type="password"
                required
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #475569', background: '#0f172a', color: '#fff' }}
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              style={{ padding: '12px', borderRadius: '8px', border: 'none', background: '#10b981', color: '#fff', fontWeight: 'bold', fontSize: '1rem', cursor: 'pointer', marginTop: '8px' }}
            >
              Ingresar y Conectar Wi-Fi
            </button>
          </form>
        )}

        {isLoading && <div className="loading">Cargando...</div>}

        {/* Demo / Admin Quick Login Link */}
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
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
