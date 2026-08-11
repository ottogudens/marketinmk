from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAdminUser
from .models import MikroTikDevice, MikroTikLog


class MikroTikDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MikroTikDevice
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        if validated_data.get('use_wireguard') and not validated_data.get('wireguard_ip'):
            host = validated_data.get('host', '')
            if host.startswith('10.8.'):
                validated_data['wireguard_ip'] = host
        return super().create(validated_data)


class MikroTikDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet para la gestión de dispositivos RouterOS"""
    queryset = MikroTikDevice.objects.all()
    serializer_class = MikroTikDeviceSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
