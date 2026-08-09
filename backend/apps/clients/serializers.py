from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, Session, ClientInteraction

class ClientSerializer(serializers.ModelSerializer):
    """Serializer para Cliente"""
    class Meta:
        model = Client
        fields = [
            'id', 'social_platform', 'email', 'full_name', 
            'phone', 'profile_picture', 'mac_address',
            'status', 'total_visits', 'first_seen', 'last_seen',
            'accepts_marketing'
        ]
        read_only_fields = ['id', 'first_seen', 'last_seen']


class ClientDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Cliente"""
    sessions_count = serializers.SerializerMethodField()
    last_session = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'social_platform', 'email', 'full_name', 
            'phone', 'profile_picture', 'mac_address',
            'status', 'total_visits', 'total_data_consumed',
            'first_seen', 'last_seen', 'accepts_marketing',
            'sessions_count', 'last_session', 'notes'
        ]
        read_only_fields = ['id', 'first_seen', 'last_seen']
    
    def get_sessions_count(self, obj):
        return obj.sessions.count()
    
    def get_last_session(self, obj):
        session = obj.sessions.first()
        if session:
            return SessionSerializer(session).data
        return None


class SessionSerializer(serializers.ModelSerializer):
    """Serializer para Sesión"""
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    total_data_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = [
            'id', 'client', 'client_name', 'mac_address', 'ip_address',
            'connected_at', 'disconnected_at', 'duration_seconds',
            'data_uploaded', 'data_downloaded', 'total_data_mb',
            'saw_offers', 'interacted_with_offer'
        ]
        read_only_fields = ['id', 'connected_at']
    
    def get_duration_seconds(self, obj):
        return int(obj.duration)
    
    def get_total_data_mb(self, obj):
        return round(obj.total_data / (1024 * 1024), 2)


class ClientInteractionSerializer(serializers.ModelSerializer):
    """Serializer para Interacción de Cliente"""
    class Meta:
        model = ClientInteraction
        fields = [
            'id', 'session', 'client', 'interaction_type',
            'offer_id', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer para registro de usuario vía OAuth"""
    social_id = serializers.CharField()
    social_platform = serializers.ChoiceField(choices=['facebook', 'instagram', 'whatsapp'])
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.URLField(required=False, allow_blank=True)
    mac_address = serializers.CharField(max_length=17, required=False, allow_blank=True)
    
    def create(self, validated_data):
        """Crear o actualizar cliente"""
        social_id = validated_data.pop('social_id')
        social_platform = validated_data.get('social_platform')
        
        client, created = Client.objects.update_or_create(
            social_id=social_id,
            defaults=validated_data
        )
        return client
