from django.db import models


class DailyAnalytics(models.Model):
    """Estadísticas diarias agregadas del sistema"""
    date = models.DateField(unique=True)

    # Clientes
    new_clients = models.IntegerField(default=0)
    active_clients = models.IntegerField(default=0)

    # Sesiones
    total_sessions = models.IntegerField(default=0)
    total_data_gb = models.FloatField(default=0)
    avg_session_duration_min = models.FloatField(default=0)

    # Ofertas
    offers_shown = models.IntegerField(default=0)
    offers_clicked = models.IntegerField(default=0)
    offers_redeemed = models.IntegerField(default=0)

    # Revenue
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_analytics'
        ordering = ['-date']

    def __str__(self):
        return f"Analytics {self.date}"

    @property
    def conversion_rate(self):
        if self.offers_shown == 0:
            return 0
        return round((self.offers_redeemed / self.offers_shown) * 100, 2)


class AISuggestion(models.Model):
    """Sugerencias y ofertas personalizadas generadas por el Agente de IA para cada cliente"""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='ai_suggestions')
    suggested_offer = models.ForeignKey('products.Offer', on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=255)
    reasoning = models.TextField(blank=True, help_text="Justificación de la IA para esta recomendación")
    suggested_discount_percent = models.IntegerField(default=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_dismissed = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        db_table = 'ai_suggestions'
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Suggestion para {self.client.full_name}: {self.title}"
