import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { offerService, interactionService, clientService } from '../services/api';
import OfferCard from '../components/OfferCard';
import '../styles/dashboard.css';

const UserDashboard = () => {
  const navigate = useNavigate();
  const { client, currentSession, logout } = useAuth();
  const [offers, setOffers] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!client) {
      navigate('/');
      return;
    }

    loadOffers();
    loadStatistics();
  }, [client]);

  const loadOffers = async () => {
    try {
      const response = await offerService.getForClient(client.id);
      
      // Registrar que vio las ofertas
      if (currentSession) {
        await interactionService.log({
          session_id: currentSession.id,
          client_id: client.id,
          interaction_type: 'view',
          metadata: { offers_count: response.data.length }
        });
      }

      setOffers(response.data);
    } catch (err) {
      console.error('Error loading offers:', err);
      setError('Error al cargar las ofertas');
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await clientService.getStatistics(client.id);
      setStatistics(response.data);
    } catch (err) {
      console.error('Error loading statistics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOfferClick = async (offerId) => {
    try {
      // Registrar click
      await offerService.trackClick(offerId, {
        client_id: client.id,
        session_id: currentSession?.id,
      });

      // Registrar interacción
      await interactionService.log({
        session_id: currentSession?.id,
        client_id: client.id,
        interaction_type: 'click',
        offer_id: offerId,
      });
    } catch (err) {
      console.error('Error tracking click:', err);
    }
  };

  if (isLoading) {
    return <div className="loading-container">Cargando ofertas...</div>;
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>¡Hola {client?.full_name}!</h1>
          <button className="logout-btn" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </header>

      {/* Statistics */}
      {statistics && (
        <section className="statistics-section">
          <div className="stat-card">
            <h4>Puntuación</h4>
            <p className="stat-value">{statistics.engagement_score}%</p>
          </div>
          <div className="stat-card">
            <h4>Visitas</h4>
            <p className="stat-value">{statistics.total_sessions}</p>
          </div>
          <div className="stat-card">
            <h4>Tiempo total</h4>
            <p className="stat-value">{statistics.total_time_minutes} min</p>
          </div>
          <div className="stat-card">
            <h4>Datos usados</h4>
            <p className="stat-value">{statistics.total_data_gb} GB</p>
          </div>
        </section>
      )}

      {/* Offers Section */}
      <section className="offers-section">
        <h2>Ofertas Exclusivas Para Ti</h2>

        {error && <div className="error-banner">{error}</div>}

        {offers.length > 0 ? (
          <div className="offers-grid">
            {offers.map((offer) => (
              <OfferCard
                key={offer.id}
                offer={offer}
                onClickOffer={() => handleOfferClick(offer.id)}
              />
            ))}
          </div>
        ) : (
          <div className="no-offers">
            <p>No hay ofertas disponibles en este momento</p>
            <p>Sigue conectado para las próximas sorpresas</p>
          </div>
        )}
      </section>

      {/* My Offers Section */}
      <section className="my-offers-section">
        <h3>Mis Ofertas Guardadas</h3>
        <div className="my-offers">
          <p>Aquí aparecerán las ofertas que hayas guardado</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>Oferta especial: Te estamos rastreando para ofrecer lo mejor 🎁</p>
      </footer>
    </div>
  );
};

export default UserDashboard;
