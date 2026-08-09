import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Manejo de errores global
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('client');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// ============ Clientes ============
export const clientService = {
  // Registrar cliente desde OAuth
  registerFromOAuth: (data) => api.post('/clients/register_from_oauth/', data),
  
  // Obtener cliente actual
  getCurrent: () => api.get('/clients/me/'),
  
  // Obtener cliente por ID
  get: (id) => api.get(`/clients/${id}/`),
  
  // Obtener estadísticas de cliente
  getStatistics: (clientId) => api.get(`/clients/${clientId}/statistics/`),
  
  // Actualizar cliente
  update: (id, data) => api.patch(`/clients/${id}/`, data),
  
  // Obtener sesiones de cliente
  getSessions: (clientId) => api.get(`/clients/${clientId}/sessions/`),
};

// ============ Sesiones ============
export const sessionService = {
  // Crear nueva sesión
  create: (data) => api.post('/sessions/create_session/', data),
  
  // Desconectar sesión
  disconnect: (sessionId, data) => api.post(`/sessions/${sessionId}/disconnect/`, data),
  
  // Obtener sesión
  get: (id) => api.get(`/sessions/${id}/`),
};

// ============ Interacciones ============
export const interactionService = {
  // Registrar interacción (click, view, etc)
  log: (data) => api.post('/interactions/log_interaction/', data),
};

// ============ Productos ============
export const productService = {
  // Obtener todos los productos
  list: () => api.get('/products/'),
  
  // Obtener producto por ID
  get: (id) => api.get(`/products/${id}/`),
  
  // Obtener categorías
  getCategories: () => api.get('/categories/'),
};

// ============ Ofertas ============
export const offerService = {
  // Obtener todas las ofertas activas
  list: () => api.get('/offers/'),
  
  // Obtener detalle de oferta
  get: (id) => api.get(`/offers/${id}/`),
  
  // Obtener ofertas recomendadas para cliente
  getForClient: (clientId) => api.get('/offers/for_client/', {
    params: { client_id: clientId }
  }),
  
  // Registrar visualización
  trackView: (offerId, data) => api.post(`/offers/${offerId}/track_view/`, data),
  
  // Registrar click
  trackClick: (offerId, data) => api.post(`/offers/${offerId}/track_click/`, data),
  
  // Registrar redención
  redeem: (offerId, data) => api.post(`/offers/${offerId}/redeem/`, data),
};

// ============ OAuth ============
export const oauthService = {
  // Obtener URL de autenticación de Facebook
  getFacebookAuthUrl: () => {
    const appId = import.meta.env.VITE_FACEBOOK_APP_ID;
    const redirectUri = `${window.location.origin}/callback/facebook`;
    return `https://www.facebook.com/v18.0/dialog/oauth?client_id=${appId}&redirect_uri=${redirectUri}&scope=email,public_profile`;
  },
  
  // Obtener URL de autenticación de Instagram
  getInstagramAuthUrl: () => {
    const appId = import.meta.env.VITE_INSTAGRAM_APP_ID;
    const redirectUri = `${window.location.origin}/callback/instagram`;
    return `https://api.instagram.com/oauth/authorize?client_id=${appId}&redirect_uri=${redirectUri}&scope=user_profile,user_media&response_type=code`;
  },
  
  // Intercambiar código por token (en el backend)
  exchangeCode: (provider, code) => api.post('/auth/exchange-code/', {
    provider,
    code
  }),
};

export default api;
