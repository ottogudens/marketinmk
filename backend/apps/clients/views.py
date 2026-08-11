from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q

from .models import Client, Session, ClientInteraction
from .serializers import (
    ClientSerializer, ClientDetailSerializer, SessionSerializer,
    ClientInteractionSerializer, UserRegistrationSerializer
)

class ClientViewSet(viewsets.ModelViewSet):
    """
    API para gestionar clientes
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'social_platform', 'accepts_marketing']
    search_fields = ['full_name', 'email', 'phone', 'social_id']
    ordering_fields = ['first_seen', 'last_seen', 'total_visits']
    ordering = ['-last_seen']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClientDetailSerializer
        return ClientSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login_with_password(self, request):
        """
        POST /api/clients/login_with_password/
        Autenticación de cliente con email/usuario y contraseña
        """
        from django.contrib.auth import authenticate
        from rest_framework.authtoken.models import Token
        from django.contrib.auth.models import User

        username = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Email/Usuario y contraseña requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            u = User.objects.filter(Q(email=username) | Q(username=username)).first()
            if u:
                user = authenticate(username=u.username, password=password)

        if not user:
            # Si el usuario no existe, crearlo como cliente registrado
            user = User.objects.create_user(username=username, email=username, password=password)

        token, _ = Token.objects.get_or_create(user=user)
        client = getattr(user, 'client', None)

        if not client:
            client = Client.objects.create(
                user=user,
                full_name=user.username.split('@')[0],
                email=user.email if '@' in user.email else f"{user.username}@hotspot.local",
                social_platform='email',
                social_id=f"user_{user.id}",
                status='active'
            )

        mac_address = request.data.get('mac_address', '')
        ip_address = request.META.get('REMOTE_ADDR', '')
        if mac_address:
            Session.objects.create(client=client, mac_address=mac_address, ip_address=ip_address)

        return Response({
            'token': token.key,
            'client': ClientSerializer(client).data
        })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register_from_oauth(self, request):
        """
        Registrar cliente desde OAuth
        POST /api/clients/register_from_oauth/
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            client = serializer.save()
            # Crear sesión
            mac_address = request.data.get('mac_address', '')
            ip_address = request.META.get('REMOTE_ADDR', '')
            
            if mac_address and ip_address:
                Session.objects.create(
                    client=client,
                    mac_address=mac_address,
                    ip_address=ip_address
                )
            
            return Response(
                ClientSerializer(client).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def sessions(self, request, pk=None):
        """Obtener todas las sesiones de un cliente"""
        client = self.get_object()
        sessions = client.sessions.all()
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Obtener estadísticas de un cliente"""
        client = self.get_object()
        sessions = client.sessions.all()
        
        stats = {
            'total_sessions': sessions.count(),
            'total_time_minutes': int(sum(s.duration for s in sessions) / 60),
            'total_data_gb': round(sum(s.total_data for s in sessions) / (1024**3), 2),
            'avg_session_duration_minutes': int(
                sum(s.duration for s in sessions) / sessions.count() / 60
                if sessions.exists() else 0
            ),
            'last_session': SessionSerializer(sessions.first()).data if sessions.exists() else None,
            'engagement_score': self._calculate_engagement_score(client),
        }
        return Response(stats)
    
    def _calculate_engagement_score(self, client):
        """Calcular puntuación de engagement (0-100)"""
        score = 0
        
        # Puntos por visitas
        score += min(client.total_visits * 5, 30)
        
        # Puntos por interacciones con ofertas
        interactions = client.interactions.filter(interaction_type__in=['click', 'convert'])
        score += min(interactions.count() * 10, 30)
        
        # Puntos por recencia (últimos 7 días)
        from datetime import timedelta
        recent = timezone.now() - timedelta(days=7)
        if client.last_seen > recent:
            score += 20
        
        # Puntos por programa de marketing
        if client.accepts_marketing:
            score += 10
        
        # Puntos por tiempo de conexión
        if client.total_time_connected.total_seconds() > 3600:
            score += 10
        
        return min(score, 100)


class SessionViewSet(viewsets.ModelViewSet):
    """
    API para gestionar sesiones de conexión
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['client', 'mac_address', 'saw_offers']
    ordering = ['-connected_at']
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def create_session(self, request):
        """
        Crear nueva sesión
        POST /api/sessions/create_session/
        Params: mac_address, ip_address, client_id
        """
        try:
            mac_address = request.data.get('mac_address')
            ip_address = request.data.get('ip_address')
            client_id = request.data.get('client_id')
            
            client = Client.objects.get(id=client_id)
            
            session = Session.objects.create(
                client=client,
                mac_address=mac_address,
                ip_address=ip_address
            )
            
            # Actualizar estadísticas de cliente
            client.total_visits += 1
            client.save()
            
            return Response(
                SessionSerializer(session).data,
                status=status.HTTP_201_CREATED
            )
        except Client.DoesNotExist:
            return Response(
                {'error': 'Cliente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """
        Desconectar sesión
        POST /api/sessions/{id}/disconnect/
        Params: data_uploaded, data_downloaded
        """
        session = self.get_object()
        
        if session.disconnected_at is None:
            session.data_uploaded = request.data.get('data_uploaded', 0)
            session.data_downloaded = request.data.get('data_downloaded', 0)
            session.disconnected_at = timezone.now()
            session.save()
            
            # Actualizar tiempo total de cliente
            client = session.client
            client.total_time_connected += timezone.timedelta(
                seconds=int(session.duration)
            )
            client.total_data_consumed += session.total_data
            client.save()
        
        return Response(SessionSerializer(session).data)


class ClientInteractionViewSet(viewsets.ModelViewSet):
    """
    API para registrar interacciones de cliente con ofertas
    """
    queryset = ClientInteraction.objects.all()
    serializer_class = ClientInteractionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['client', 'session', 'interaction_type']
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def log_interaction(self, request):
        """
        Registrar interacción
        POST /api/interactions/log_interaction/
        """
        try:
            interaction = ClientInteraction.objects.create(
                session_id=request.data.get('session_id'),
                client_id=request.data.get('client_id'),
                interaction_type=request.data.get('interaction_type'),
                offer_id=request.data.get('offer_id'),
                metadata=request.data.get('metadata', {})
            )
            
            # Marcar sesión como vio ofertas
            session = interaction.session
            if interaction.interaction_type in ['view', 'click', 'convert']:
                session.saw_offers = True
                if interaction.interaction_type in ['click', 'convert']:
                    session.interacted_with_offer = True
                session.save()
            
            return Response(
                ClientInteractionSerializer(interaction).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


from .models import LoyaltyProgram, LoyaltyTransaction, Purchase
from rest_framework.decorators import api_view, permission_classes as perm_dec

@api_view(['POST'])
@perm_dec([AllowAny])
def pos_webhook(request):
    """
    POST /api/pos/webhook/
    Webhook para recibir ventas desde TPV / POS físico
    Body: { "mac_address": "...", "amount": 15000, "pos_terminal_id": "POS-01", "reference": "REF123" }
    """
    mac_address = request.data.get('mac_address')
    amount = float(request.data.get('amount', 0))
    pos_terminal_id = request.data.get('pos_terminal_id', 'POS-GENERAL')
    reference = request.data.get('reference', '')

    if not mac_address or amount <= 0:
        return Response({'error': 'mac_address y amount son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        client = Client.objects.get(mac_address=mac_address)

        # 1. Registrar Compra
        purchase = Purchase.objects.create(
            client=client,
            amount=amount,
            pos_terminal_id=pos_terminal_id,
            transaction_reference=reference
        )

        # 2. Sumar puntos al Programa de Lealtad (100 CLP / $1 = 1 punto)
        points_earned = int(amount / 100) if amount >= 100 else 1
        program, _ = LoyaltyProgram.objects.get_or_create(client=client)
        program.total_points += points_earned
        program.update_tier()

        LoyaltyTransaction.objects.create(
            program=program,
            points=points_earned,
            description=f"Compra TPV {pos_terminal_id} ${amount}"
        )

        return Response({
            'message': 'Venta registrada y puntos acreditados',
            'purchase_id': purchase.id,
            'client': client.full_name,
            'points_earned': points_earned,
            'total_points': program.total_points,
            'tier': program.tier
        }, status=status.HTTP_201_CREATED)

    except Client.DoesNotExist:
        return Response({'error': 'Cliente no encontrado para la MAC provista'}, status=status.HTTP_404_NOT_FOUND)


class LoyaltyProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """API para consultar estado de lealtad"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_status(self, request):
        """GET /api/loyalty/my_status/"""
        try:
            client = request.user.client
            program, _ = LoyaltyProgram.objects.get_or_create(client=client)
            transactions = list(program.transactions.values('points', 'description', 'created_at')[:10])

            return Response({
                'total_points': program.total_points,
                'tier': program.tier,
                'recent_transactions': transactions
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
