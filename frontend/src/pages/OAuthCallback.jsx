import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/oauth-callback.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const OAuthCallback = () => {
  const { provider } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState('loading'); // 'loading', 'success', 'error'
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');

    if (error) {
      setStatus('error');
      setErrorMessage(searchParams.get('error_description') || 'El usuario canceló o denegó la autenticación.');
      return;
    }

    if (!code) {
      setStatus('error');
      setErrorMessage('No se recibió código de autorización desde el proveedor.');
      return;
    }

    const processOAuth = async () => {
      try {
        const redirectUri = `${window.location.origin}/callback/${provider}`;
        const macAddress = localStorage.getItem('mac_address') || '';

        const response = await axios.post(`${API_URL}/auth/callback/${provider}/`, {
          code,
          redirect_uri: redirectUri,
          mac_address: macAddress,
        });

        const { token, client } = response.data;

        localStorage.setItem('authToken', token);
        localStorage.setItem('client', JSON.stringify(client));

        setStatus('success');

        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } catch (err) {
        setStatus('error');
        setErrorMessage(err.response?.data?.error || 'Error al autenticar con el servidor backend.');
      }
    };

    processOAuth();
  }, [provider, searchParams, navigate]);

  return (
    <div className="oauth-callback-container">
      {status === 'loading' && (
        <div className="callback-loading">
          <div className="spinner"></div>
          <h2>Autenticando con {provider?.toUpperCase()}</h2>
          <p>Por favor espera mientras validamos tu sesión...</p>
        </div>
      )}

      {status === 'success' && (
        <div className="callback-success">
          <div className="success-icon">✅</div>
          <h2>¡Autenticación Exitosa!</h2>
          <p>Redirigiendo a tu panel de ofertas...</p>
        </div>
      )}

      {status === 'error' && (
        <div className="callback-error">
          <div className="error-icon">❌</div>
          <h2>Error de Autenticación</h2>
          <p>{errorMessage}</p>
          <button className="btn-retry" onClick={() => navigate('/')}>
            Volver a intentar
          </button>
        </div>
      )}
    </div>
  );
};

export default OAuthCallback;
