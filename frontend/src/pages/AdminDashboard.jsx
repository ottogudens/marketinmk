import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { analyticsService, mikrotikService, clientService, offerService, sessionService } from '../services/api';
import './AdminDashboard.css';

// ─── KPI Card ────────────────────────────────────────────────────────────────
const KPICard = ({ label, value, change, icon, color }) => {
  const isPositive = change >= 0;
  return (
    <div className="kpi-card" style={{ '--accent': color }}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-body">
        <span className="kpi-label">{label}</span>
        <span className="kpi-value">{value}</span>
        {change !== undefined && (
          <span className={`kpi-change ${isPositive ? 'positive' : 'negative'}`}>
            {isPositive ? '▲' : '▼'} {Math.abs(change)}% vs semana anterior
          </span>
        )}
      </div>
    </div>
  );
};

// ─── Custom Tooltip ───────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="tooltip-label">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: <strong>{p.value}</strong>
        </p>
      ))}
    </div>
  );
};

const PLATFORM_COLORS = { facebook: '#1877F2', instagram: '#E1306C', whatsapp: '#25D366' };
const PIE_COLORS = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6'];

export default function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [dailyStats, setDailyStats] = useState([]);
  const [platformData, setPlatformData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDays, setSelectedDays] = useState(30);
  const [activeTab, setActiveTab] = useState('overview');

  // Management States
  const [clientsList, setClientsList] = useState([]);
  const [offersList, setOffersList] = useState([]);
  const [sessionsList, setSessionsList] = useState([]);

  // Modals
  const [showAddClientModal, setShowAddClientModal] = useState(false);
  const [newClient, setNewClient] = useState({ full_name: '', email: '', phone: '', social_platform: 'whatsapp', mac_address: '' });

  const [showAddOfferModal, setShowAddOfferModal] = useState(false);
  const [newOffer, setNewOffer] = useState({
    name: '', description: '', offer_type: 'discount', discount_value: 10, discount_type: 'percent',
    banner_image: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5',
    start_date: new Date().toISOString().slice(0, 16),
    end_date: new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 16),
    status: 'active'
  });

  // MikroTik & Wireguard States
  const [mikrotikDevices, setMikrotikDevices] = useState([]);
  const [wireguardStatus, setWireguardStatus] = useState(null);
  const [showAddDeviceModal, setShowAddDeviceModal] = useState(false);
  const [generatedScript, setGeneratedScript] = useState(null);
  const [newDevice, setNewDevice] = useState({
    name: '', host: '10.8.0.2', port: 8728, username: 'admin', password: '', use_wireguard: true
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ovRes, dailyRes, platRes, mkDevicesRes, wgStatusRes, clientsRes, offersRes, sessionsRes] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getDailyStats(selectedDays),
        analyticsService.getClientsByPlatform(),
        mikrotikService.listDevices().catch(() => ({ data: [] })),
        mikrotikService.getWireguardStatus().catch(() => ({ data: null })),
        clientService.list().catch(() => ({ data: [] })),
        offerService.list().catch(() => ({ data: [] })),
        sessionService.list().catch(() => ({ data: [] })),
      ]);
      setOverview(ovRes.data);
      setDailyStats(Array.isArray(dailyRes.data) ? dailyRes.data : (dailyRes.data?.results || []));
      setPlatformData(Array.isArray(platRes.data) ? platRes.data : (platRes.data?.results || []));
      
      const devicesData = mkDevicesRes.data;
      setMikrotikDevices(Array.isArray(devicesData) ? devicesData : (devicesData?.results || []));
      setWireguardStatus(wgStatusRes.data);

      const cData = clientsRes.data;
      setClientsList(Array.isArray(cData) ? cData : (cData?.results || []));

      const oData = offersRes.data;
      setOffersList(Array.isArray(oData) ? oData : (oData?.results || []));

      const sData = sessionsRes.data;
      setSessionsList(Array.isArray(sData) ? sData : (sData?.results || []));
    } catch (err) {
      setError('Error al cargar datos. Verifica que tienes permisos de admin.');
    } finally {
      setLoading(false);
    }
  }, [selectedDays]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleCreateDevice = async (e) => {
    e.preventDefault();
    try {
      const res = await mikrotikService.createDevice(newDevice);
      const scriptRes = await mikrotikService.generateScript(res.data.id, {});
      setGeneratedScript(scriptRes.data.routeros_script);
      setShowAddDeviceModal(false);
      loadData();
    } catch (err) {
      alert('Error al crear dispositivo MikroTik');
    }
  };

  const handleGetScript = async (deviceId) => {
    try {
      const res = await mikrotikService.generateScript(deviceId, {});
      setGeneratedScript(res.data.routeros_script);
    } catch (err) {
      alert('Error al generar script RouterOS');
    }
  };

  const [editingDevice, setEditingDevice] = useState(null);

  const handleSaveEditDevice = async (e) => {
    e.preventDefault();
    if (!editingDevice) return;
    try {
      const payload = { ...editingDevice };
      if (!payload.password) delete payload.password; // No sobrescribir pass si está vacía
      await mikrotikService.updateDevice(editingDevice.id, payload);
      alert('Dispositivo actualizado correctamente.');
      setEditingDevice(null);
      loadData();
    } catch (err) {
      alert('Error al actualizar el dispositivo.');
    }
  };

  const handleDeleteDevice = async (deviceId, name) => {
    if (window.confirm(`¿Estás seguro de que deseas eliminar el router "${name}"?`)) {
      try {
        await mikrotikService.deleteDevice(deviceId);
        loadData();
      } catch (err) {
        alert('Error al eliminar el dispositivo.');
      }
    }
  };

  const handleCreateClient = async (e) => {
    e.preventDefault();
    try {
      await clientService.create({
        ...newClient,
        social_id: newClient.social_id || `manual_${Date.now()}`
      });
      setShowAddClientModal(false);
      setNewClient({ full_name: '', email: '', phone: '', social_platform: 'whatsapp', mac_address: '' });
      loadData();
    } catch (err) {
      alert('Error al crear el cliente. Revisa que el email o MAC no estén duplicados.');
    }
  };

  const handleDeleteClient = async (clientId, name) => {
    if (window.confirm(`¿Deseas eliminar al cliente "${name}"?`)) {
      try {
        await clientService.delete(clientId);
        loadData();
      } catch (err) {
        alert('Error al eliminar cliente.');
      }
    }
  };

  const handleCreateOffer = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newOffer,
        start_date: newOffer.start_date ? new Date(newOffer.start_date).toISOString() : new Date().toISOString(),
        end_date: newOffer.end_date ? new Date(newOffer.end_date).toISOString() : new Date(Date.now() + 30 * 86400000).toISOString(),
        discount_value: Number(newOffer.discount_value),
        products: []
      };
      await offerService.create(payload);
      setShowAddOfferModal(false);
      loadData();
    } catch (err) {
      alert('Error al crear la oferta: ' + (err.response?.data ? JSON.stringify(err.response.data) : err.message));
    }
  };

  const handleDeleteOffer = async (offerId, name) => {
    if (window.confirm(`¿Deseas eliminar la oferta "${name}"?`)) {
      try {
        await offerService.delete(offerId);
        loadData();
      } catch (err) {
        alert('Error al eliminar la oferta.');
      }
    }
  };

  const handleUpdatePubKey = async (deviceId, currentKey) => {
    const key = prompt('Ingresa la Clave Pública Wireguard (public-key) enviada por tu RouterOS:', currentKey || '');
    if (key !== null) {
      try {
        await mikrotikService.updateDevice(deviceId, { wireguard_public_key: key.trim() });
        alert('Clave pública de Wireguard registrada correctamente.');
        loadData();
      } catch (err) {
        alert('Error al guardar la clave pública.');
      }
    }
  };

  if (loading) return (
    <div className="admin-loading">
      <div className="spinner" />
      <p>Cargando panel de administración…</p>
    </div>
  );

  if (error) return (
    <div className="admin-error">
      <span>⚠️</span>
      <p>{error}</p>
      <button onClick={loadData}>Reintentar</button>
    </div>
  );

  const kpis = overview?.kpis || {};
  const topOffers = overview?.top_offers || [];
  const topClients = overview?.top_clients || [];

  return (
    <div className="admin-dashboard">
      {/* Header */}
      <header className="admin-header">
        <div className="admin-header-left">
          <h1>📊 Admin Control Center</h1>
          <span className="admin-subtitle">MarketinMK · Hotspot & Wireguard VPN Manager</span>
        </div>
        <div className="admin-header-right">
          <select
            value={selectedDays}
            onChange={(e) => setSelectedDays(Number(e.target.value))}
            className="days-selector"
          >
            <option value={7}>Últimos 7 días</option>
            <option value={30}>Últimos 30 días</option>
            <option value={90}>Últimos 90 días</option>
          </select>
          <button className="refresh-btn" onClick={loadData}>↻ Actualizar</button>
        </div>
      </header>

      {/* Tabs */}
      <nav className="admin-tabs">
        {['overview', 'mikrotik', 'docs', 'sessions', 'clients', 'offers'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {{
              overview: '🏠 Resumen General',
              mikrotik: '🌐 Routers MikroTik & Wireguard VPN',
              docs: '📖 Manual Integración Redes Sociales',
              sessions: '📶 Sesiones',
              clients: '👥 Clientes',
              offers: '🎁 Ofertas'
            }[tab]}
          </button>
        ))}
      </nav>

      {/* TAB: MANUAL INTEGRACION REDES SOCIALES */}
      {activeTab === 'docs' && (
        <div className="social-docs-view">
          <div className="docs-header-card">
            <h2>📖 Manual Paso a Paso: Configuración de Redes Sociales (OAuth 2.0)</h2>
            <p>Sigue estas instrucciones precisas para conectar la autenticación de Facebook, Instagram y WhatsApp con tu portal Hotspot.</p>
          </div>

          <div className="docs-grid">
            {/* Facebook Login */}
            <div className="doc-card">
              <div className="doc-card-title">
                <span className="doc-icon fb">📘</span>
                <h3>1. Integración con Facebook Login</h3>
              </div>
              <ol className="doc-steps">
                <li>Ingresa a <a href="https://developers.facebook.com/" target="_blank" rel="noreferrer">Meta for Developers</a> e inicia sesión.</li>
                <li>Ve a <strong>Mis Apps</strong> → <strong>Crear App</strong> → Selecciona el tipo <strong>"Consumidor"</strong> o <strong>"Ninguno"</strong>.</li>
                <li>En el panel lateral, agrega el producto <strong>"Inicio de sesión con Facebook"</strong>.</li>
                <li>Dirígete a <strong>Configuración de la App → Básica</strong> y copia tu <strong>App ID</strong> y <strong>App Secret</strong>.</li>
                <li>En <strong>Inicio de sesión con Facebook → Configuración</strong>, agrega las URLs de redirección permitidas:
                  <pre className="code-box">
                    {`URLs de redirección de OAuth válidas:\nhttps://tu-dominio.railway.app/callback/facebook\nhttp://localhost:5173/callback/facebook`}
                  </pre>
                </li>
                <li>Pega tus credenciales en el archivo <code>.env</code> de Railway:
                  <pre className="code-box">
                    {`FACEBOOK_APP_ID=tu_app_id\nFACEBOOK_APP_SECRET=tu_app_secret`}
                  </pre>
                </li>
              </ol>
            </div>

            {/* Instagram Auth */}
            <div className="doc-card">
              <div className="doc-card-title">
                <span className="doc-icon ig">📸</span>
                <h3>2. Integración con Instagram Basic Display</h3>
              </div>
              <ol className="doc-steps">
                <li>En la misma app de <a href="https://developers.facebook.com/" target="_blank" rel="noreferrer">Meta Developers</a>, ve a <strong>Añadir Producto</strong> → Selecciona <strong>"Instagram Basic Display"</strong>.</li>
                <li>Haz clic en <strong>Crear nueva aplicación de Instagram</strong>.</li>
                <li>En la sección <strong>OAuth Redirect URIs</strong>, registra exactamente la siguiente URL:
                  <pre className="code-box">
                    {`URI de redirección válida de OAuth:\nhttps://tu-dominio.railway.app/callback/instagram`}
                  </pre>
                </li>
                <li>Copia la <strong>Instagram App ID</strong> y el <strong>Instagram App Secret</strong>.</li>
                <li>Configura las variables de entorno en tu panel de Railway:
                  <pre className="code-box">
                    {`INSTAGRAM_APP_ID=tu_instagram_app_id\nINSTAGRAM_APP_SECRET=tu_instagram_app_secret`}
                  </pre>
                </li>
              </ol>
            </div>

            {/* Google OAuth 2.0 */}
            <div className="doc-card">
              <div className="doc-card-title">
                <span className="doc-icon" style={{ color: '#ea4335' }}>🔴</span>
                <h3>3. Integración con Google Identity (OAuth 2.0)</h3>
              </div>
              <ol className="doc-steps">
                <li>Ingresa a <a href="https://console.cloud.google.com/" target="_blank" rel="noreferrer">Google Cloud Console</a>.</li>
                <li>Crea un proyecto → Ve a <strong>APIs y Servicios</strong> → <strong>Pantalla de consentimiento de OAuth</strong> (Usuario Externo).</li>
                <li>Dirígete a <strong>Credenciales → Crear Credenciales → ID de cliente de OAuth</strong> (Tipo: Aplicación Web).</li>
                <li>Registra los orígenes e URIs de redirección autorizados:
                  <pre className="code-box">
                    {`Orígenes de JavaScript autorizados:\nhttps://web-production-4bdaa.up.railway.app\n\nURIs de redirección autorizadas:\nhttps://web-production-4bdaa.up.railway.app/callback/google`}
                  </pre>
                </li>
                <li>Copia tu <strong>Client ID</strong> y <strong>Client Secret</strong> y configúralos en Railway:
                  <pre className="code-box">
                    {`VITE_GOOGLE_CLIENT_ID=tu_google_client_id.apps.googleusercontent.com\nGOOGLE_CLIENT_SECRET=tu_google_client_secret`}
                  </pre>
                </li>
              </ol>
            </div>

            {/* WhatsApp Business / Twilio */}
            <div className="doc-card full">
              <div className="doc-card-title">
                <span className="doc-icon wa">💬</span>
                <h3>4. Configuración de Mensajería WhatsApp (Twilio Sandbox / Prod)</h3>
              </div>
              <ol className="doc-steps">
                <li>Accede a tu consola en <a href="https://console.twilio.com/" target="_blank" rel="noreferrer">Twilio Console</a>.</li>
                <li>Obtén tu <strong>Account SID</strong> y <strong>Auth Token</strong> desde el Dashboard principal.</li>
                <li>Ve a <strong>Messaging → Try it out → Send a WhatsApp message</strong> para obtener tu número Sandbox (ej: <code>+14155238886</code>).</li>
                <li>Configura las credenciales en Railway para que Celery envíe ofertas automáticas cada 2 horas:
                  <pre className="code-box">
                    {`TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nTWILIO_AUTH_TOKEN=your_auth_token_here\nTWILIO_WHATSAPP_NUMBER=+14155238886`}
                  </pre>
                </li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* TAB: MIKROTIK & WIREGUARD VPN */}
      {activeTab === 'mikrotik' && (
        <div className="mikrotik-view">
          {/* Wireguard Server Overview Card */}
          <div className="wg-server-card">
            <div className="wg-server-header">
              <div>
                <h2>🔐 Servidor Wireguard VPN Activo</h2>
                <p className="wg-sub">Permite conexión directa con routers sin IP pública en cada sucursal</p>
              </div>
              <span className="wg-status-badge">ONLINE · {wireguardStatus?.server_ip}</span>
            </div>

            <div className="wg-metrics-grid">
              <div className="wg-metric">
                <span className="wg-metric-label">Puerto de Escucha</span>
                <span className="wg-metric-val">{wireguardStatus?.listen_port} UDP</span>
              </div>
              <div className="wg-metric">
                <span className="wg-metric-label">Endpoint Central</span>
                <span className="wg-metric-val">{wireguardStatus?.endpoint}</span>
              </div>
              <div className="wg-metric">
                <span className="wg-metric-label">Túneles Conectados</span>
                <span className="wg-metric-val">{wireguardStatus?.active_peers?.length || 0} Routers</span>
              </div>
            </div>
          </div>

          {/* Device Action Bar */}
          <div className="device-action-bar">
            <h3>Dispositivos RouterOS Registrados</h3>
            <button className="btn-add-device" onClick={() => setShowAddDeviceModal(true)}>
              + Agregar Router MikroTik
            </button>
          </div>

          {/* Routers Grid */}
          <div className="routers-grid">
            {!Array.isArray(mikrotikDevices) || mikrotikDevices.length === 0 ? (
              <div className="no-routers-card">
                <p>No hay routers MikroTik registrados.</p>
                <p>Agrega un nuevo router para generar su script de autoconfiguración Wireguard.</p>
              </div>
            ) : (
              mikrotikDevices.map((dev) => (
                <div key={dev.id} className="router-card">
                  <div className="router-card-header">
                    <h4>{dev.name}</h4>
                    <span className={`status-pill ${dev.is_active ? 'online' : 'offline'}`}>
                      {dev.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                  <div className="router-card-body">
                    <p><strong>IP VPN:</strong> {dev.wireguard_ip || '10.8.0.X'}</p>
                    <p><strong>IP Host:</strong> {dev.host}</p>
                    <p><strong>Puerto API:</strong> {dev.port}</p>
                    <p><strong>Clave Pública WG:</strong> <code style={{ fontSize: '11px', color: '#60a5fa' }}>{dev.wireguard_public_key || 'Sin registrar'}</code></p>
                    <p><strong>Wireguard:</strong> {dev.use_wireguard ? '✅ Habilitado (Sin IP pública)' : '❌ Deshabilitado'}</p>
                  </div>
                  <div className="router-card-actions">
                    <button className="btn-script" onClick={() => handleGetScript(dev.id)}>
                      📜 Script
                    </button>
                    <button className="btn-script" style={{ background: '#2563eb' }} onClick={() => handleUpdatePubKey(dev.id, dev.wireguard_public_key)}>
                      🔑 Clave WG
                    </button>
                    <button className="btn-script" style={{ background: '#475569' }} onClick={() => setEditingDevice({ ...dev, password: '' })}>
                      ✏️ Editar
                    </button>
                    <button className="btn-script" style={{ background: '#dc2626' }} onClick={() => handleDeleteDevice(dev.id, dev.name)}>
                      🗑️
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Modal / Generated RouterOS Script Box */}
          {generatedScript && (
            <div className="script-modal">
              <div className="script-modal-content">
                <div className="script-modal-header">
                  <h3>📜 Script de Autoconfiguración RouterOS</h3>
                  <button className="close-btn" onClick={() => setGeneratedScript(null)}>✕</button>
                </div>
                <p>Copia y pega este script en la Terminal de WinBox / RouterOS para vincular automáticamente el Router a la VPN Wireguard:</p>
                <pre className="script-code">{generatedScript}</pre>
                <button className="btn-copy" onClick={() => navigator.clipboard.writeText(generatedScript)}>
                  📋 Copiar al Portapapeles
                </button>
              </div>
            </div>
          )}

          {/* Modal Add Device */}
          {showAddDeviceModal && (
            <div className="script-modal">
              <form className="script-modal-content" onSubmit={handleCreateDevice}>
                <div className="script-modal-header">
                  <h3>+ Agregar Nuevo Router MikroTik</h3>
                  <button type="button" className="close-btn" onClick={() => setShowAddDeviceModal(false)}>✕</button>
                </div>
                <div className="form-group">
                  <label>Nombre de la Sucursal / Router:</label>
                  <input type="text" required value={newDevice.name} onChange={(e) => setNewDevice({...newDevice, name: e.target.value})} placeholder="Ej: Sucursal Santiago" />
                </div>
                <div className="form-group">
                  <label>IP Host o Dominio DDNS (mynetname.net):</label>
                  <input type="text" required value={newDevice.host} onChange={(e) => setNewDevice({...newDevice, host: e.target.value})} placeholder="Ej: 123456.sn.mynetname.net o 10.8.0.2" />
                </div>
                <div className="form-group">
                  <label>Puerto API RouterOS:</label>
                  <input type="number" required value={newDevice.port} onChange={(e) => setNewDevice({...newDevice, port: Number(e.target.value)})} placeholder="8728" />
                </div>
                <div className="form-group">
                  <label>Usuario API RouterOS:</label>
                  <input type="text" required value={newDevice.username} onChange={(e) => setNewDevice({...newDevice, username: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Contraseña API RouterOS:</label>
                  <input type="password" required value={newDevice.password} onChange={(e) => setNewDevice({...newDevice, password: e.target.value})} />
                </div>
                <div className="form-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '8px' }}>
                  <input type="checkbox" id="use_wg_add" checked={newDevice.use_wireguard} onChange={(e) => setNewDevice({...newDevice, use_wireguard: e.target.checked})} />
                  <label htmlFor="use_wg_add" style={{ margin: 0 }}>Usar VPN Wireguard</label>
                </div>
                <button type="submit" className="btn-copy">Guardar y Generar Script VPN</button>
              </form>
            </div>
          )}

          {/* Modal Edit Device */}
          {editingDevice && (
            <div className="script-modal">
              <form className="script-modal-content" onSubmit={handleSaveEditDevice}>
                <div className="script-modal-header">
                  <h3>✏️ Editar Router: {editingDevice.name}</h3>
                  <button type="button" className="close-btn" onClick={() => setEditingDevice(null)}>✕</button>
                </div>
                <div className="form-group">
                  <label>Nombre del Router / Sucursal:</label>
                  <input type="text" required value={editingDevice.name || ''} onChange={(e) => setEditingDevice({...editingDevice, name: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>IP Host o Dominio DDNS (mynetname.net / IP pública):</label>
                  <input type="text" required value={editingDevice.host || ''} onChange={(e) => setEditingDevice({...editingDevice, host: e.target.value})} placeholder="Ej: 123456789abc.sn.mynetname.net" />
                </div>
                <div className="form-group">
                  <label>Puerto API RouterOS:</label>
                  <input type="number" required value={editingDevice.port || 8728} onChange={(e) => setEditingDevice({...editingDevice, port: Number(e.target.value)})} />
                </div>
                <div className="form-group">
                  <label>Usuario API RouterOS:</label>
                  <input type="text" required value={editingDevice.username || ''} onChange={(e) => setEditingDevice({...editingDevice, username: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Nueva Contraseña API (dejar en blanco para mantener la actual):</label>
                  <input type="password" value={editingDevice.password || ''} onChange={(e) => setEditingDevice({...editingDevice, password: e.target.value})} placeholder="••••••••" />
                </div>
                <div className="form-group">
                  <label>IP VPN Wireguard asignada (opcional):</label>
                  <input type="text" value={editingDevice.wireguard_ip || ''} onChange={(e) => setEditingDevice({...editingDevice, wireguard_ip: e.target.value})} placeholder="10.8.0.2" />
                </div>
                <div className="form-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '8px' }}>
                  <input type="checkbox" id="use_wg_edit" checked={!!editingDevice.use_wireguard} onChange={(e) => setEditingDevice({...editingDevice, use_wireguard: e.target.checked})} />
                  <label htmlFor="use_wg_edit" style={{ margin: 0 }}>Usar VPN Wireguard</label>
                </div>
                <button type="submit" className="btn-copy">💾 Guardar Cambios</button>
              </form>
            </div>
          )}
        </div>
      )}

      {/* TAB: OVERVIEW */}
      {activeTab === 'overview' && (
        <>
          {/* KPI Cards */}
          <section className="kpi-grid">
            <KPICard label="Clientes Totales" value={kpis.total_clients?.toLocaleString()} icon="👥" color="#6366f1" />
            <KPICard label="Nuevos (7d)" value={kpis.new_clients} change={kpis.new_clients_change} icon="✨" color="#10b981" />
            <KPICard label="Clientes Activos" value={kpis.active_clients} change={kpis.active_clients_change} icon="🔥" color="#f59e0b" />
            <KPICard label="Sesiones (7d)" value={kpis.total_sessions} change={kpis.total_sessions_change} icon="📶" color="#3b82f6" />
            <KPICard label="Canjes (7d)" value={kpis.offers_redeemed} icon="🎁" color="#ec4899" />
            <KPICard label="Engagement Rate" value={`${kpis.engagement_rate}%`} icon="💡" color="#8b5cf6" />
          </section>

          {/* Charts Grid */}
          <section className="charts-grid">
            <div className="chart-card wide">
              <h3>Sesiones diarias</h3>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={dailyStats} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={d => d?.slice(5)} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="sessions" name="Sesiones" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="unique_clients" name="Clientes únicos" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Datos transferidos (MB)</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={d => d?.slice(5)} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="total_data_mb" name="MB" stroke="#3b82f6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Clientes por plataforma</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={platformData}
                    dataKey="count"
                    nameKey="social_platform"
                    cx="50%" cy="50%"
                    outerRadius={80}
                    label={({ social_platform, percent }) => `${social_platform} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {(Array.isArray(platformData) ? platformData : []).map((entry, i) => (
                      <Cell key={i} fill={PLATFORM_COLORS[entry.social_platform] || PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Bottom Grid: Top Offers + Top Clients */}
          <section className="tables-grid">
            <div className="table-card">
              <h3>🎁 Top Ofertas</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Oferta</th>
                    <th>Vistas</th>
                    <th>Clicks</th>
                    <th>CTR</th>
                  </tr>
                </thead>
                <tbody>
                  {topOffers.length === 0 ? (
                    <tr><td colSpan={5} className="empty-row">Sin datos aún</td></tr>
                  ) : topOffers.map((offer, i) => {
                    const ctr = offer.views_count > 0 ? ((offer.clicks_count / offer.views_count) * 100).toFixed(1) : 0;
                    return (
                      <tr key={offer.id}>
                        <td><span className="rank">{i + 1}</span></td>
                        <td className="offer-name">{offer.name}</td>
                        <td>{offer.views_count}</td>
                        <td>{offer.clicks_count}</td>
                        <td><span className={`ctr-badge ${ctr >= 5 ? 'good' : ctr >= 2 ? 'ok' : 'low'}`}>{ctr}%</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="table-card">
              <h3>👥 Top Clientes</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Cliente</th>
                    <th>Red</th>
                    <th>Visitas</th>
                    <th>Última vez</th>
                  </tr>
                </thead>
                <tbody>
                  {topClients.length === 0 ? (
                    <tr><td colSpan={5} className="empty-row">Sin datos aún</td></tr>
                  ) : topClients.map((client, i) => (
                    <tr key={client.id}>
                      <td><span className="rank">{i + 1}</span></td>
                      <td>
                        <div className="client-name">{client.full_name}</div>
                        <div className="client-email">{client.email}</div>
                      </td>
                      <td><span className="platform-badge" data-platform={client.social_platform}>{client.social_platform}</span></td>
                      <td>{client.total_visits}</td>
                      <td className="date-cell">{client.last_seen ? new Date(client.last_seen).toLocaleDateString('es-CL') : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}

      {/* TAB: CLIENTES */}
      {activeTab === 'clients' && (
        <div className="tab-view-container">
          <div className="device-action-bar">
            <h2>👥 Clientes Registrados</h2>
            <button className="btn-add-device" onClick={() => setShowAddClientModal(true)}>
              + Agregar Cliente
            </button>
          </div>

          <div className="table-card">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Cliente</th>
                  <th>MAC Address</th>
                  <th>Red Social</th>
                  <th>Teléfono</th>
                  <th>Visitas</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {clientsList.length === 0 ? (
                  <tr><td colSpan={7} className="empty-row">No hay clientes registrados aún</td></tr>
                ) : clientsList.map((c, i) => (
                  <tr key={c.id}>
                    <td><span className="rank">{i + 1}</span></td>
                    <td>
                      <div className="client-name">{c.full_name}</div>
                      <div className="client-email">{c.email}</div>
                    </td>
                    <td><code style={{ fontSize: '11px', color: '#94a3b8' }}>{c.mac_address || '-'}</code></td>
                    <td><span className="platform-badge" data-platform={c.social_platform}>{c.social_platform}</span></td>
                    <td>{c.phone || '-'}</td>
                    <td>{c.total_visits}</td>
                    <td>
                      <button className="btn-script" style={{ background: '#dc2626', padding: '4px 8px' }} onClick={() => handleDeleteClient(c.id, c.full_name)}>
                        🗑️ Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Modal Add Client */}
          {showAddClientModal && (
            <div className="script-modal">
              <form className="script-modal-content" onSubmit={handleCreateClient}>
                <div className="script-modal-header">
                  <h3>+ Agregar Nuevo Cliente</h3>
                  <button type="button" className="close-btn" onClick={() => setShowAddClientModal(false)}>✕</button>
                </div>
                <div className="form-group">
                  <label>Nombre Completo:</label>
                  <input type="text" required value={newClient.full_name} onChange={(e) => setNewClient({...newClient, full_name: e.target.value})} placeholder="Ej: Juan Pérez" />
                </div>
                <div className="form-group">
                  <label>Email:</label>
                  <input type="email" required value={newClient.email} onChange={(e) => setNewClient({...newClient, email: e.target.value})} placeholder="juan@gmail.com" />
                </div>
                <div className="form-group">
                  <label>Teléfono / WhatsApp:</label>
                  <input type="text" value={newClient.phone} onChange={(e) => setNewClient({...newClient, phone: e.target.value})} placeholder="+56912345678" />
                </div>
                <div className="form-group">
                  <label>Red Social de Captura:</label>
                  <select value={newClient.social_platform} onChange={(e) => setNewClient({...newClient, social_platform: e.target.value})}>
                    <option value="whatsapp">WhatsApp</option>
                    <option value="facebook">Facebook</option>
                    <option value="instagram">Instagram</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Dirección MAC Dispositivo (opcional):</label>
                  <input type="text" value={newClient.mac_address} onChange={(e) => setNewClient({...newClient, mac_address: e.target.value})} placeholder="AA:BB:CC:DD:EE:FF" />
                </div>
                <button type="submit" className="btn-copy">💾 Guardar Cliente</button>
              </form>
            </div>
          )}
        </div>
      )}

      {/* TAB: OFERTAS */}
      {activeTab === 'offers' && (
        <div className="tab-view-container">
          <div className="device-action-bar">
            <h2>🎁 Ofertas & Promociones Hotspot</h2>
            <button className="btn-add-device" onClick={() => setShowAddOfferModal(true)}>
              + Crear Nueva Oferta
            </button>
          </div>

          <div className="table-card">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Nombre Oferta</th>
                  <th>Tipo</th>
                  <th>Descuento</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {offersList.length === 0 ? (
                  <tr><td colSpan={6} className="empty-row">No hay ofertas creadas aún</td></tr>
                ) : offersList.map((o, i) => (
                  <tr key={o.id}>
                    <td><span className="rank">{i + 1}</span></td>
                    <td className="offer-name"><strong>{o.name}</strong><br/><small style={{ color: '#94a3b8' }}>{o.description}</small></td>
                    <td>{o.offer_type}</td>
                    <td>{o.discount_value}{o.discount_type === 'percent' ? '%' : '$'}</td>
                    <td><span className={`status-pill ${o.status === 'active' ? 'online' : 'offline'}`}>{o.status}</span></td>
                    <td>
                      <button className="btn-script" style={{ background: '#dc2626', padding: '4px 8px' }} onClick={() => handleDeleteOffer(o.id, o.name)}>
                        🗑️ Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Modal Add Offer */}
          {showAddOfferModal && (
            <div className="script-modal">
              <form className="script-modal-content" onSubmit={handleCreateOffer}>
                <div className="script-modal-header">
                  <h3>+ Crear Nueva Oferta Promocional</h3>
                  <button type="button" className="close-btn" onClick={() => setShowAddOfferModal(false)}>✕</button>
                </div>
                <div className="form-group">
                  <label>Título de la Oferta:</label>
                  <input type="text" required value={newOffer.name} onChange={(e) => setNewOffer({...newOffer, name: e.target.value})} placeholder="Ej: 20% Dcto en Hamburguesas" />
                </div>
                <div className="form-group">
                  <label>Descripción:</label>
                  <textarea required style={{ background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '6px', padding: '8px' }} value={newOffer.description} onChange={(e) => setNewOffer({...newOffer, description: e.target.value})} placeholder="Muestra esta pantalla en caja para hacer efectivo tu descuento." />
                </div>
                <div className="form-group">
                  <label>Valor del Descuento:</label>
                  <input type="number" required value={newOffer.discount_value} onChange={(e) => setNewOffer({...newOffer, discount_value: Number(e.target.value)})} />
                </div>
                <div className="form-group">
                  <label>Tipo de Descuento:</label>
                  <select value={newOffer.discount_type} onChange={(e) => setNewOffer({...newOffer, discount_type: e.target.value})}>
                    <option value="percent">% Porcentaje</option>
                    <option value="fixed">$ Monto Fijo</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Estado de la Oferta:</label>
                  <select value={newOffer.status} onChange={(e) => setNewOffer({...newOffer, status: e.target.value})}>
                    <option value="active">Activa</option>
                    <option value="draft">Borrador</option>
                    <option value="paused">Pausada</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>URL Imagen Banner:</label>
                  <input type="text" required value={newOffer.banner_image} onChange={(e) => setNewOffer({...newOffer, banner_image: e.target.value})} />
                </div>
                <button type="submit" className="btn-copy">🎁 Publicar Oferta</button>
              </form>
            </div>
          )}
        </div>
      )}

      {/* TAB: SESIONES */}
      {activeTab === 'sessions' && (
        <div className="tab-view-container">
          <div className="device-action-bar">
            <h2>📶 Historial de Sesiones Hotspot</h2>
          </div>

          <div className="table-card">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Cliente</th>
                  <th>MAC Address</th>
                  <th>IP Conexión</th>
                  <th>Fecha Conexión</th>
                  <th>Subida (MB)</th>
                  <th>Bajada (MB)</th>
                </tr>
              </thead>
              <tbody>
                {sessionsList.length === 0 ? (
                  <tr><td colSpan={7} className="empty-row">No hay sesiones registradas aún</td></tr>
                ) : sessionsList.map((s, i) => (
                  <tr key={s.id}>
                    <td><span className="rank">{i + 1}</span></td>
                    <td>{s.client_name || `Cliente #${s.client}`}</td>
                    <td><code style={{ fontSize: '11px', color: '#94a3b8' }}>{s.mac_address}</code></td>
                    <td>{s.ip_address}</td>
                    <td className="date-cell">{new Date(s.connected_at).toLocaleString('es-CL')}</td>
                    <td>{(s.data_uploaded / 1048576).toFixed(2)} MB</td>
                    <td>{(s.data_downloaded / 1048576).toFixed(2)} MB</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
