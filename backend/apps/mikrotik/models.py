from django.db import models
from django.utils import timezone

class MikroTikDevice(models.Model):
    """Dispositivo MikroTik configurado"""
    name = models.CharField(max_length=255)
    host = models.GenericIPAddressField()
    port = models.IntegerField(default=8728)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    
    # Configuración de hotspot
    hotspot_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mikrotik_devices'
    
    def __str__(self):
        return self.name


class MikroTikUser(models.Model):
    """Usuario registrado en MikroTik (para seguimiento)"""
    mikrotik = models.ForeignKey(MikroTikDevice, on_delete=models.CASCADE)
    
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    
    mac_address = models.CharField(max_length=17, unique=True)
    client = models.OneToOneField('clients.Client', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mikrotik_users'
    
    def __str__(self):
        return self.username


class MikroTikLog(models.Model):
    """Log de sincronización con MikroTik"""
    LOG_TYPES = [
        ('sync_users', 'Sincronización de usuarios'),
        ('sync_sessions', 'Sincronización de sesiones'),
        ('get_bandwidth', 'Obtener ancho de banda'),
        ('error', 'Error'),
    ]
    
    mikrotik = models.ForeignKey(MikroTikDevice, on_delete=models.CASCADE, related_name='logs')
    
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('success', 'Éxito'), ('error', 'Error')])
    
    # Datos
    users_processed = models.IntegerField(default=0)
    users_created = models.IntegerField(default=0)
    users_updated = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mikrotik_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_log_type_display()} - {self.created_at}"


class BandwidthUsage(models.Model):
    """Registro de consumo de ancho de banda por cliente"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='bandwidth_usage')
    
    date = models.DateField(auto_now_add=True)
    
    upload_mb = models.FloatField(default=0)
    download_mb = models.FloatField(default=0)
    
    class Meta:
        db_table = 'bandwidth_usage'
        unique_together = ['client', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.client} - {self.date}"
