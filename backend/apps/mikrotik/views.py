from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAdminUser
from .models import MikroTikDevice, MikroTikLog


class MikroTikDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MikroTikDevice
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False, 'allow_blank': True}
        }

    def create(self, validated_data):
        if validated_data.get('use_wireguard') and not validated_data.get('wireguard_ip'):
            host = validated_data.get('host', '')
            if host.startswith('10.8.'):
                validated_data['wireguard_ip'] = host
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data and not validated_data['password']:
            validated_data.pop('password')
        return super().update(instance, validated_data)


class MikroTikDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet para la gestión de dispositivos RouterOS"""
    queryset = MikroTikDevice.objects.all()
    serializer_class = MikroTikDeviceSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.clients.models import Client, Session

@api_view(['POST'])
@permission_classes([AllowAny])
def push_sessions(request):
    """
    POST /api/mikrotik/push_sessions/
    Sincroniza sesiones activas enviadas mediante HTTP Push desde RouterOS (/tool fetch).
    """
    mac = request.data.get('mac') or request.POST.get('mac')
    user_name = request.data.get('user') or request.POST.get('user')
    try:
        bytes_in = int(request.data.get('bytes_in', 0) or request.POST.get('bytes_in', 0))
        bytes_out = int(request.data.get('bytes_out', 0) or request.POST.get('bytes_out', 0))
    except (ValueError, TypeError):
        bytes_in = 0
        bytes_out = 0

    if not mac:
        return Response({'error': 'MAC requerida'}, status=400)

    client = Client.objects.filter(mac_address=mac).first()
    if not client:
        display_name = user_name if user_name else f"Cliente_{mac.replace(':', '')[-6:]}"
        client = Client.objects.create(
            full_name=display_name,
            email=f"client_{mac.replace(':', '')}@hotspot.local",
            mac_address=mac,
            social_platform='whatsapp',
            social_id=f"mac_{mac}",
            status='active'
        )

    session, created = Session.objects.get_or_create(
        client=client,
        mac_address=mac,
        disconnected_at__isnull=True,
        defaults={'ip_address': request.META.get('REMOTE_ADDR', '0.0.0.0')}
    )
    session.data_uploaded = bytes_in
    session.data_downloaded = bytes_out
    session.save()

    client.total_visits = Session.objects.filter(client=client).count()
    client.save()

    return Response({
        'status': 'ok',
        'session_id': session.id,
        'client': client.full_name,
        'created': created
    })


