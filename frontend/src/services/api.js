import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

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
  registerFromOAuth: (data) => api.post('/clients/register_from_oauth/', data),
  getCurrent: () => api.get('/clients/me/'),
  get: (id) => api.get(`/clients/${id}/`),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.patch(`/clients/${id}/`, data),
  delete: (id) => api.delete(`/clients/${id}/`),
  getStatistics: (clientId) => api.get(`/clients/${clientId}/statistics/`),
  getSessions: (clientId) => api.get(`/clients/${clientId}/sessions/`),
  list: (params) => api.get('/clients/', { params }),
};

// ============ Sesiones ============
export const sessionService = {
  list: () => api.get('/sessions/'),
  create: (data) => api.post('/sessions/create_session/', data),
  disconnect: (sessionId, data) => api.post(`/sessions/${sessionId}/disconnect/`, data),
  get: (id) => api.get(`/sessions/${id}/`),
};

// ============ Interacciones ============
export const interactionService = {
  log: (data) => api.post('/interactions/log_interaction/', data),
};

// ============ Productos ============
export const productService = {
  list: () => api.get('/products/'),
  get: (id) => api.get(`/products/${id}/`),
  getCategories: () => api.get('/categories/'),
};

// ============ Ofertas ============
export const offerService = {
  list: () => api.get('/offers/'),
  get: (id) => api.get(`/offers/${id}/`),
  create: (data) => api.post('/offers/', data),
  update: (id, data) => api.patch(`/offers/${id}/`, data),
  delete: (id) => api.delete(`/offers/${id}/`),
  getForClient: (clientId) => api.get('/offers/for_client/', { params: { client_id: clientId } }),
  trackView: (offerId, data) => api.post(`/offers/${offerId}/track_view/`, data),
  trackClick: (offerId, data) => api.post(`/offers/${offerId}/track_click/`, data),
  redeem: (offerId, data) => api.post(`/offers/${offerId}/redeem/`, data),
};

// ============ Analytics ============
export const analyticsService = {
  getOverview: () => api.get('/analytics/overview/'),
  getDailyStats: (days = 30) => api.get('/analytics/daily_stats/', { params: { days } }),
  getClientsByPlatform: () => api.get('/analytics/clients_by_platform/'),
  triggerAggregation: (date) => api.post('/analytics/trigger_aggregation/', { date }),
  getMyAISuggestions: () => api.get('/analytics/my_ai_suggestions/'),
  requestAISuggestion: (clientId) => api.post('/analytics/generate_ai_suggestion/', { client_id: clientId }),
};

// ============ OAuth ============
export const oauthService = {
  getFacebookAuthUrl: () => {
    const appId = import.meta.env.VITE_FACEBOOK_APP_ID;
    const redirectUri = `${window.location.origin}/callback/facebook`;
    return `https://www.facebook.com/v18.0/dialog/oauth?client_id=${appId}&redirect_uri=${redirectUri}&scope=email,public_profile`;
  },
  getInstagramAuthUrl: () => {
    const appId = import.meta.env.VITE_INSTAGRAM_APP_ID;
    const redirectUri = `${window.location.origin}/callback/instagram`;
    return `https://api.instagram.com/oauth/authorize?client_id=${appId}&redirect_uri=${redirectUri}&scope=user_profile,user_media&response_type=code`;
  },
  exchangeCode: (provider, code) => api.post('/auth/exchange-code/', { provider, code }),
};

// ============ Cupones ============
export const couponService = {
  validate: (code, purchaseAmount) => api.post('/coupons/validate/', { code, purchase_amount: purchaseAmount }),
  list: () => api.get('/coupons/'),
};

// ============ Pagos ============
export const paymentService = {
  create: (data) => api.post('/payments/create/', data),
};

// ============ Programa de Lealtad ============
export const loyaltyService = {
  getMyStatus: () => api.get('/loyalty/my_status/'),
};

// ============ MikroTik & Wireguard ============
export const mikrotikService = {
  listDevices: () => api.get('/mikrotik/devices/'),
  createDevice: (data) => api.post('/mikrotik/devices/', data),
  updateDevice: (id, data) => api.patch(`/mikrotik/devices/${id}/`, data),
  deleteDevice: (id) => api.delete(`/mikrotik/devices/${id}/`),
  getWireguardStatus: () => api.get('/mikrotik/wireguard/server_status/'),
  generateScript: (deviceId, data) => api.post(`/mikrotik/wireguard/generate_script/${deviceId}/`, data),
};

export default api;
