from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from apps.clients.views import ClientViewSet, SessionViewSet, ClientInteractionViewSet, LoyaltyProgramViewSet, pos_webhook
from apps.products.views import (
    CategoryViewSet, ProductViewSet, OfferViewSet,
    OfferRedemptionViewSet, OfferViewViewSet, CouponViewSet,
    validate_coupon, create_payment, payment_webhook
)
from apps.analytics.views import AnalyticsViewSet
from apps.mikrotik.views import MikroTikDeviceViewSet
from apps.mikrotik.wireguard_views import get_wireguard_server_status, generate_mikrotik_script

# REST Framework Router
router = DefaultRouter()

# Clientes
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'interactions', ClientInteractionViewSet, basename='interaction')
router.register(r'loyalty', LoyaltyProgramViewSet, basename='loyalty')

# Productos y Ofertas
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'redemptions', OfferRedemptionViewSet, basename='redemption')
router.register(r'offer-views', OfferViewViewSet, basename='offer-view')

# Analytics y MikroTik
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'mikrotik/devices', MikroTikDeviceViewSet, basename='mikrotik-device')

from apps.clients.oauth_views import oauth_callback, logout_user, get_current_user

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/callback/<str:provider>/', oauth_callback, name='oauth_callback'),
    path('api/auth/logout/', logout_user, name='logout'),
    path('api/auth/me/', get_current_user, name='current_user'),
    path('api/coupons/validate/', validate_coupon, name='validate_coupon'),
    path('api/payments/create/', create_payment, name='create_payment'),
    path('api/payments/webhook/', payment_webhook, name='payment_webhook'),
    path('api/pos/webhook/', pos_webhook, name='pos_webhook'),
    path('api/mikrotik/wireguard/server_status/', get_wireguard_server_status, name='wireguard_server_status'),
    path('api/mikrotik/wireguard/generate_script/<int:device_id>/', generate_mikrotik_script, name='generate_mikrotik_script'),
    
    # OAuth Social Auth
    path('auth/', include('social_django.urls', namespace='social')),
    
    # Static & Media
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
