from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q

from .models import Category, Product, Offer, OfferRedemption, OfferView
from .serializers import (
    CategorySerializer, ProductSerializer, OfferSerializer,
    OfferDetailSerializer, OfferRedemptionSerializer, OfferViewSerializer,
    OfferCreateSerializer
)
from apps.clients.models import Client

class CategoryViewSet(viewsets.ModelViewSet):
    """API para categorías de productos"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    ordering = ['order']


class ProductViewSet(viewsets.ModelViewSet):
    """API para productos"""
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category', 'active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


class OfferViewSet(viewsets.ModelViewSet):
    """
    API para ofertas
    GET /api/offers/ - Listar ofertas activas
    GET /api/offers/{id}/ - Detalle de oferta
    POST /api/offers/for_client/ - Ofertas recomendadas para cliente
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'offer_type', 'target_all']
    search_fields = ['name', 'description']
    ordering = ['-start_date']
    
    def get_queryset(self):
        # Admin ve todas las ofertas
        if self.request.user.is_staff:
            return Offer.objects.all()
        # Usuarios ven solo ofertas activas
        return Offer.objects.filter(status='active', end_date__gte=timezone.now())
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            if self.request.user.is_staff:
                return OfferDetailSerializer
            return OfferSerializer
        elif self.action == 'create':
            return OfferCreateSerializer
        return OfferDetailSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def for_client(self, request):
        """
        Obtener ofertas recomendadas para un cliente
        GET /api/offers/for_client/?client_id=1
        """
        try:
            client_id = request.query_params.get('client_id')
            client = Client.objects.get(id=client_id)
            
            offers = self._get_offers_for_client(client)
            
            serializer = OfferSerializer(offers, many=True)
            return Response(serializer.data)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Cliente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _get_offers_for_client(self, client):
        """Lógica para recomendar ofertas a un cliente"""
        offers = Offer.objects.filter(
            status='active',
            end_date__gte=timezone.now(),
            start_date__lte=timezone.now()
        )
        
        # Filtrar por público objetivo
        if client.total_visits == 1:
            offers = offers.filter(Q(target_all=True) | Q(target_first_time=True))
        else:
            offers = offers.filter(Q(target_all=True) | Q(target_repeat=True))
        
        # Filtrar por número mínimo de visitas
        offers = offers.filter(min_visits__lte=client.total_visits)
        
        return offers.distinct()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def track_view(self, request, pk=None):
        """
        Registrar visualización de oferta
        POST /api/offers/{id}/track_view/
        Params: client_id, session_id
        """
        try:
            offer = self.get_object()
            client = Client.objects.get(id=request.data.get('client_id'))
            
            # Registrar vista
            view = OfferView.objects.create(
                offer=offer,
                client=client,
                session_id=request.data.get('session_id')
            )
            
            return Response(
                OfferViewSerializer(view).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def track_click(self, request, pk=None):
        """
        Registrar click en oferta
        POST /api/offers/{id}/track_click/
        Params: client_id, session_id
        """
        try:
            offer = self.get_object()
            client = Client.objects.get(id=request.data.get('client_id'))
            session_id = request.data.get('session_id')
            
            # Actualizar o crear vista
            view, created = OfferView.objects.update_or_create(
                offer=offer,
                client=client,
                session_id=session_id,
                defaults={
                    'clicked': True,
                    'clicked_at': timezone.now()
                }
            )
            
            return Response(OfferViewSerializer(view).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def redeem(self, request, pk=None):
        """
        Registrar redención de oferta
        POST /api/offers/{id}/redeem/
        Params: client_id, amount_spent, transaction_id
        """
        try:
            offer = self.get_object()
            client = Client.objects.get(id=request.data.get('client_id'))
            
            # Verificar límites
            if offer.max_uses and offer.uses_count >= offer.max_uses:
                return Response(
                    {'error': 'Oferta alcanzó el límite de usos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calcular valor aplicado
            amount_spent = float(request.data.get('amount_spent', 0))
            value_applied = self._calculate_discount(offer, amount_spent)
            
            # Crear redención
            redemption = OfferRedemption.objects.create(
                offer=offer,
                client=client,
                amount_spent=amount_spent,
                value_applied=value_applied,
                transaction_id=request.data.get('transaction_id')
            )
            
            # Incrementar contador
            offer.uses_count += 1
            offer.save()
            
            return Response(
                OfferRedemptionSerializer(redemption).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _calculate_discount(self, offer, amount_spent):
        """Calcular descuento aplicado"""
        if offer.discount_type == 'percent':
            return amount_spent * (offer.discount_value / 100)
        else:  # fixed
            return min(offer.discount_value, amount_spent)


class OfferRedemptionViewSet(viewsets.ModelViewSet):
    """API para redenciones de ofertas"""
    queryset = OfferRedemption.objects.all()
    serializer_class = OfferRedemptionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['offer', 'client']
    ordering = ['-redeemed_at']


class OfferViewViewSet(viewsets.ModelViewSet):
    """API para visualizaciones de ofertas"""
    queryset = OfferView.objects.all()
    serializer_class = OfferViewSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['offer', 'client', 'clicked']
    ordering = ['-viewed_at']
