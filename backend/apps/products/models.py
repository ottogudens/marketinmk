from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    """Categoría de productos"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.URLField(null=True, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Producto o servicio que ofrece el negocio"""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Marketing
    image = models.URLField()
    short_description = models.CharField(max_length=255)
    
    # Estado
    active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class Offer(models.Model):
    """Oferta especial vinculada a producto(s)"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('paused', 'Pausada'),
        ('expired', 'Expirada'),
    ]
    
    OFFER_TYPES = [
        ('discount', 'Descuento %'),
        ('fixed', 'Precio fijo'),
        ('bogo', 'Compra 1 Lleva 2'),
        ('combo', 'Combo'),
        ('loyalty', 'Programa de puntos'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    products = models.ManyToManyField(Product, related_name='offers')
    
    # Tipo de oferta
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES)
    discount_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=10, choices=[('percent', '%'), ('fixed', '$')], default='percent')
    
    # Imagen y promoción
    banner_image = models.URLField()
    cta_text = models.CharField(max_length=100, default='Ver oferta')
    
    # Validez
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Reglas
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_uses = models.IntegerField(null=True, blank=True)
    uses_count = models.IntegerField(default=0)
    
    # Público objetivo
    target_all = models.BooleanField(default=True)
    target_first_time = models.BooleanField(default=False)
    target_repeat = models.BooleanField(default=False)
    min_visits = models.IntegerField(default=1)
    
    # Distribución
    show_on_splash = models.BooleanField(default=True)
    send_whatsapp = models.BooleanField(default=True)
    whatsapp_delay_minutes = models.IntegerField(default=5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offers'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.get_offer_type_display()})"
    
    @property
    def is_active(self):
        now = timezone.now()
        return (self.status == 'active' and 
                self.start_date <= now <= self.end_date and
                (self.max_uses is None or self.uses_count < self.max_uses))
    
    @property
    def days_remaining(self):
        delta = self.end_date - timezone.now()
        return delta.days


class OfferRedemption(models.Model):
    """Registro de uso de ofertas"""
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='redemptions')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='redeemed_offers')
    
    # Detalles de la redención
    redeemed_at = models.DateTimeField(auto_now_add=True)
    value_applied = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Referencia
    transaction_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'offer_redemptions'
        ordering = ['-redeemed_at']
    
    def __str__(self):
        return f"{self.client} - {self.offer}"


class OfferView(models.Model):
    """Registro de visualizaciones de ofertas"""
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='views')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='seen_offers')
    session = models.ForeignKey('clients.Session', on_delete=models.SET_NULL, null=True, blank=True)
    
    viewed_at = models.DateTimeField(auto_now_add=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'offer_views'
        ordering = ['-viewed_at']


class Coupon(models.Model):
    """Cupones de descuento asignados a ofertas"""
    code = models.CharField(max_length=50, unique=True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='coupons')
    
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(max_length=10, choices=[('percent', '%'), ('fixed', '$')], default='fixed')
    max_uses = models.IntegerField(default=100)
    uses_count = models.IntegerField(default=0)
    
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupons'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.offer.name}"

    @property
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_until and
                self.uses_count < self.max_uses)


class CouponRedemption(models.Model):
    """Redenciones de cupones por clientes"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='redemptions')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='coupon_redemptions')
    
    redeemed_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'coupon_redemptions'
        ordering = ['-redeemed_at']

    def __str__(self):
        return f"{self.client} - {self.coupon.code}"


class Payment(models.Model):
    """Registro de pagos (ej. Flow)"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]

    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='payments')
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    flow_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pago #{self.id} ({self.client}) - {self.status}"
