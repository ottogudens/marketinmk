import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { analyticsService } from '../services/api';
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

// ─── Platform colors ─────────────────────────────────────────────────────────
const PLATFORM_COLORS = {
  facebook: '#1877F2',
  instagram: '#E1306C',
  whatsapp: '#25D366',
};
const PIE_COLORS = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6'];

// ─── Main Component ───────────────────────────────────────────────────────────
export default function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [dailyStats, setDailyStats] = useState([]);
  const [platformData, setPlatformData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDays, setSelectedDays] = useState(30);
  const [activeTab, setActiveTab] = useState('overview');

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ovRes, dailyRes, platRes] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getDailyStats(selectedDays),
        analyticsService.getClientsByPlatform(),
      ]);
      setOverview(ovRes.data);
      setDailyStats(dailyRes.data);
      setPlatformData(platRes.data);
    } catch (err) {
      setError('Error al cargar datos. Verifica que tienes permisos de admin.');
    } finally {
      setLoading(false);
    }
  }, [selectedDays]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return (
    <div className="admin-loading">
      <div className="spinner" />
      <p>Cargando analytics…</p>
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
          <h1>📊 Analytics Dashboard</h1>
          <span className="admin-subtitle">MarketinMK · Hotspot Manager</span>
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
        {['overview', 'sessions', 'clients', 'offers'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {{ overview: '🏠 Resumen', sessions: '📶 Sesiones', clients: '👥 Clientes', offers: '🎁 Ofertas' }[tab]}
          </button>
        ))}
      </nav>

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
        {/* Sesiones diarias */}
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

        {/* Datos transferidos */}
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

        {/* Distribución por plataforma */}
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
                label={({ social_platform, percent }) =>
                  `${social_platform} ${(percent * 100).toFixed(0)}%`
                }
                labelLine={false}
              >
                {platformData.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={PLATFORM_COLORS[entry.social_platform] || PIE_COLORS[i % PIE_COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Bottom Grid: Top Offers + Top Clients */}
      <section className="tables-grid">
        {/* Top Ofertas */}
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
                const ctr = offer.views_count > 0
                  ? ((offer.clicks_count / offer.views_count) * 100).toFixed(1)
                  : 0;
                return (
                  <tr key={offer.id}>
                    <td><span className="rank">{i + 1}</span></td>
                    <td className="offer-name">{offer.name}</td>
                    <td>{offer.views_count}</td>
                    <td>{offer.clicks_count}</td>
                    <td>
                      <span className={`ctr-badge ${ctr >= 5 ? 'good' : ctr >= 2 ? 'ok' : 'low'}`}>
                        {ctr}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Top Clientes */}
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
                  <td>
                    <span className="platform-badge" data-platform={client.social_platform}>
                      {client.social_platform}
                    </span>
                  </td>
                  <td>{client.total_visits}</td>
                  <td className="date-cell">
                    {client.last_seen ? new Date(client.last_seen).toLocaleDateString('es-CL') : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
