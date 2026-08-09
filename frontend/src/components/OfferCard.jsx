import React from 'react';
import '../styles/offer-card.css';

const OfferCard = ({ offer, onClickOffer }) => {
  const getDiscountLabel = () => {
    if (offer.offer_type === 'discount') {
      return `${offer.discount_value}${offer.discount_type === 'percent' ? '%' : '$'} OFF`;
    } else if (offer.offer_type === 'bogo') {
      return 'COMPRA 1\nLLEVA 2';
    } else if (offer.offer_type === 'combo') {
      return 'COMBO';
    } else if (offer.offer_type === 'loyalty') {
      return 'PUNTOS';
    }
    return 'OFERTA';
  };

  const handleClick = () => {
    onClickOffer();
  };

  return (
    <div className="offer-card">
      {/* Banner Image */}
      <div
        className="offer-banner"
        style={{
          backgroundImage: `url('${offer.banner_image}')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Discount Badge */}
        <div className="discount-badge">
          {getDiscountLabel()}
        </div>

        {/* Days Remaining */}
        {offer.days_remaining !== undefined && (
          <div className="expiration-badge">
            Vence en {offer.days_remaining} días
          </div>
        )}
      </div>

      {/* Card Content */}
      <div className="offer-content">
        <h3 className="offer-name">{offer.name}</h3>
        <p className="offer-description">{offer.description}</p>

        {/* Products (if any) */}
        {offer.products && offer.products.length > 0 && (
          <div className="offer-products">
            {offer.products.map((product) => (
              <span key={product.id} className="product-tag">
                {product.name}
              </span>
            ))}
          </div>
        )}

        {/* Min Purchase */}
        {offer.min_purchase && (
          <p className="min-purchase">
            Compra mínima: ${offer.min_purchase}
          </p>
        )}

        {/* CTA Button */}
        <button className="cta-button" onClick={handleClick}>
          {offer.cta_text || 'Ver Oferta'}
        </button>
      </div>
    </div>
  );
};

export default OfferCard;
