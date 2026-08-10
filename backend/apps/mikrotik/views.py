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


class MikroTikDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet para la gestión de dispositivos RouterOS"""
    queryset = MikroTikDevice.objects.all()
    serializer_class = MikroTikDeviceSerializer
    permission_classes = [IsAdminUser]
