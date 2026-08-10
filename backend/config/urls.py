from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from apps.clients.views import ClientViewSet, SessionViewSet, ClientInteractionViewSet
from apps.products.views import (
    CategoryViewSet, ProductViewSet, OfferViewSet,
    OfferRedemptionViewSet, OfferViewViewSet
)
from apps.analytics.views import AnalyticsViewSet

# REST Framework Router
router = DefaultRouter()

# Clientes
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'interactions', ClientInteractionViewSet, basename='interaction')

# Productos y Ofertas
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'redemptions', OfferRedemptionViewSet, basename='redemption')
router.register(r'offer-views', OfferViewViewSet, basename='offer-view')

# Analytics
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token-auth/', obtain_auth_token, name='api_token_auth'),
    
    # OAuth Social Auth
    path('auth/', include('social_django.urls', namespace='social')),
    
    # Static & Media
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
