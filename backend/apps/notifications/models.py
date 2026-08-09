from django.db import models
from django.utils import timezone

class Notification(models.Model):
    """Base para todas las notificaciones"""
    CHANNELS = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregado'),
        ('failed', 'Fallido'),
    ]
    
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='notifications')
    offer = models.ForeignKey('products.Offer', on_delete=models.SET_NULL, null=True, blank=True)
    
    channel = models.CharField(max_length=20, choices=CHANNELS)
    
    # Contenido
    title = models.CharField(max_length=255)
    body = models.TextField()
    action_url = models.URLField(null=True, blank=True)
    
    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Respuesta
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    external_id = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['status', 'sent_at']),
        ]
    
    def __str__(self):
        return f"{self.channel.upper()} - {self.client} - {self.title}"


class WhatsAppMessage(models.Model):
    """Mensaje específico de WhatsApp"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='whatsapp')
    
    phone_number = models.CharField(max_length=20)
    template_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Metadata de Twilio
    twilio_message_sid = models.CharField(max_length=255, null=True, blank=True, unique=True)
    twilio_status = models.CharField(max_length=20, null=True, blank=True)
    twilio_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    class Meta:
        db_table = 'whatsapp_messages'
    
    def __str__(self):
        return f"WhatsApp -> {self.phone_number}"


class NotificationTemplate(models.Model):
    """Plantillas de notificaciones predefinidas"""
    TEMPLATE_TYPES = [
        ('welcome', 'Bienvenida'),
        ('offer', 'Oferta'),
        ('reminder', 'Recordatorio'),
        ('win_back', 'Recuperar cliente'),
        ('loyalty', 'Programa de fidelización'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    
    # Contenido
    whatsapp_body = models.TextField()
    whatsapp_footer = models.CharField(max_length=60, blank=True)
    whatsapp_button_text = models.CharField(max_length=20, blank=True)
    
    email_subject = models.CharField(max_length=255, blank=True)
    email_body = models.TextField(blank=True)
    
    sms_body = models.CharField(max_length=160)
    
    # Variables permitidas: {name}, {offer_name}, {discount}, etc
    variables = models.JSONField(default=list, blank=True)
    
    active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
    
    def __str__(self):
        return self.name


class NotificationLog(models.Model):
    """Log detallado de intento de envío"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    
    attempt_number = models.IntegerField(default=1)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=20)
    message = models.TextField()
    
    class Meta:
        db_table = 'notification_logs'
        ordering = ['-attempted_at']
