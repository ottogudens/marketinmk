from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Client(models.Model):
    """Cliente capturado a través del hotspot"""
    SOCIAL_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('blocked', 'Bloqueado'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    social_platform = models.CharField(max_length=20, choices=SOCIAL_CHOICES)
    social_id = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    profile_picture = models.URLField(null=True, blank=True)
    
    # Información geográfica
    mac_address = models.CharField(max_length=17, unique=True, null=True, blank=True)
    first_location = models.CharField(max_length=255, null=True, blank=True)
    
    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Engagement
    total_visits = models.IntegerField(default=0)
    total_time_connected = models.DurationField(default=timezone.timedelta(0))
    total_data_consumed = models.BigIntegerField(default=0)  # en bytes
    
    # Preferencias
    accepts_marketing = models.BooleanField(default=True)
    
    # Metadatos
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'clients'
        indexes = [
            models.Index(fields=['social_id']),
            models.Index(fields=['phone']),
            models.Index(fields=['mac_address']),
            models.Index(fields=['last_seen']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.social_platform})"


class Session(models.Model):
    """Sesión de conexión al hotspot"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sessions')
    
    # Conexión
    mac_address = models.CharField(max_length=17)
    ip_address = models.GenericIPAddressField()
    
    # Tiempo
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    
    # Estadísticas
    data_uploaded = models.BigIntegerField(default=0)  # bytes
    data_downloaded = models.BigIntegerField(default=0)  # bytes
    
    # Interacciones
    saw_offers = models.BooleanField(default=False)
    interacted_with_offer = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sessions'
        ordering = ['-connected_at']
        indexes = [
            models.Index(fields=['client', 'connected_at']),
            models.Index(fields=['mac_address']),
        ]
    
    @property
    def duration(self):
        """Duración de la sesión en segundos"""
        if self.disconnected_at:
            return (self.disconnected_at - self.connected_at).total_seconds()
        return (timezone.now() - self.connected_at).total_seconds()
    
    @property
    def total_data(self):
        """Total de datos transferidos en bytes"""
        return self.data_uploaded + self.data_downloaded
    
    def __str__(self):
        return f"Sesión {self.client} - {self.connected_at}"


class ClientInteraction(models.Model):
    """Registro de interacciones del cliente con ofertas"""
    INTERACTION_TYPES = [
        ('view', 'Visualización'),
        ('click', 'Click'),
        ('dismiss', 'Descartado'),
        ('convert', 'Conversión'),
    ]
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='interactions')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interactions')
    
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    offer_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'client_interactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client} - {self.interaction_type}"


class LoyaltyProgram(models.Model):
    """Programa de lealtad por cliente"""
    TIER_CHOICES = [
        ('bronze', 'Bronce'),
        ('silver', 'Plata'),
        ('gold', 'Oro'),
        ('platinum', 'Platino'),
    ]

    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='loyalty_program')
    total_points = models.IntegerField(default=0)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loyalty_programs'

    def update_tier(self):
        if self.total_points >= 3000:
            self.tier = 'platinum'
        elif self.total_points >= 1500:
            self.tier = 'gold'
        elif self.total_points >= 500:
            self.tier = 'silver'
        else:
            self.tier = 'bronze'
        self.save()

    def __str__(self):
        return f"Programa de Lealtad - {self.client.full_name} ({self.tier.capitalize()}: {self.total_points} pts)"


class LoyaltyTransaction(models.Model):
    """Transacciones de puntos del programa de lealtad"""
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='transactions')
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loyalty_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.program.client.full_name}: {self.points} pts - {self.description}"


class Purchase(models.Model):
    """Registro de compras fisicas / TPV POS"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='purchases')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pos_terminal_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'purchases'
        ordering = ['-created_at']

    def __str__(self):
        return f"Compra {self.client.full_name}: ${self.amount}"
