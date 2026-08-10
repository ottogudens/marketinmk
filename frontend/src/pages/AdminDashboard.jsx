import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { analyticsService, mikrotikService } from '../services/api';
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
      const [ovRes, dailyRes, platRes, mkDevicesRes, wgStatusRes] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getDailyStats(selectedDays),
        analyticsService.getClientsByPlatform(),
        mikrotikService.listDevices().catch(() => ({ data: [] })),
        mikrotikService.getWireguardStatus().catch(() => ({ data: null })),
      ]);
      setOverview(ovRes.data);
      setDailyStats(dailyRes.data);
      setPlatformData(platRes.data);
      setMikrotikDevices(mkDevicesRes.data || []);
      setWireguardStatus(wgStatusRes.data);
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
        {['overview', 'mikrotik', 'sessions', 'clients', 'offers'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {{
              overview: '🏠 Resumen General',
              mikrotik: '🌐 Routers MikroTik & Wireguard VPN',
              sessions: '📶 Sesiones',
              clients: '👥 Clientes',
              offers: '🎁 Ofertas'
            }[tab]}
          </button>
        ))}
      </nav>

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
            {mikrotikDevices.length === 0 ? (
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
                    <p><strong>Wireguard:</strong> {dev.use_wireguard ? '✅ Habilitado (Sin IP pública)' : '❌ Deshabilitado'}</p>
                  </div>
                  <div className="router-card-actions">
                    <button className="btn-script" onClick={() => handleGetScript(dev.id)}>
                      📜 Obtener Script RouterOS
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
                  <input type="text" required value={newDevice.name} onChange={(e) => setNewDevice({...newDevice, name: e.target.value})} placeholder="Ej: Sucursal Santiago Centro" />
                </div>
                <div className="form-group">
                  <label>IP Asignada en VPN Wireguard:</label>
                  <input type="text" required value={newDevice.host} onChange={(e) => setNewDevice({...newDevice, host: e.target.value})} placeholder="10.8.0.2" />
                </div>
                <div className="form-group">
                  <label>Usuario API RouterOS:</label>
                  <input type="text" required value={newDevice.username} onChange={(e) => setNewDevice({...newDevice, username: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Contraseña API RouterOS:</label>
                  <input type="password" required value={newDevice.password} onChange={(e) => setNewDevice({...newDevice, password: e.target.value})} />
                </div>
                <button type="submit" className="btn-copy">Guardar y Generar Script VPN</button>
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
                    {platformData.map((entry, i) => (
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
    </div>
  );
}
