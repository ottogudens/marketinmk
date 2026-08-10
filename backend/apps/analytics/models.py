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
