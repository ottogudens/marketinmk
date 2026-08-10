"""
Celery tasks para agregación diaria de analytics.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Avg, F, FloatField
from django.db.models.functions import Cast

from apps.clients.models import Client, Session, ClientInteraction
from .models import DailyAnalytics


@shared_task(name='apps.analytics.tasks.aggregate_daily_stats')
def aggregate_daily_stats(date_str=None):
    """
    Agrega estadísticas del día anterior y las guarda en DailyAnalytics.
    Se ejecuta cada medianoche vía Celery Beat.
    """
    if date_str:
        from datetime import date
        target_date = date.fromisoformat(date_str)
    else:
        target_date = (timezone.now() - timedelta(days=1)).date()

    # Clientes
    new_clients = Client.objects.filter(
        first_seen__date=target_date
    ).count()

    active_clients = Client.objects.filter(
        last_seen__date=target_date
    ).count()

    # Sesiones del día
    sessions_qs = Session.objects.filter(connected_at__date=target_date)

    total_sessions = sessions_qs.count()

    data_agg = sessions_qs.aggregate(
        total_bytes=Sum(F('data_uploaded') + F('data_downloaded'))
    )
    total_bytes = data_agg['total_bytes'] or 0
    total_data_gb = round(total_bytes / (1024 ** 3), 4)

    duration_agg = sessions_qs.filter(
        disconnected_at__isnull=False
    ).annotate(
        duration_sec=Cast(
            F('disconnected_at') - F('connected_at'),
            FloatField()
        )
    ).aggregate(avg_dur=Avg('duration_sec'))

    avg_sec = duration_agg['avg_dur'] or 0
    avg_session_duration_min = round(avg_sec / 60, 2)

    # Interacciones
    interactions_qs = ClientInteraction.objects.filter(
        created_at__date=target_date
    )
    offers_shown = interactions_qs.filter(interaction_type='view').count()
    offers_clicked = interactions_qs.filter(interaction_type='click').count()
    offers_redeemed = interactions_qs.filter(interaction_type='convert').count()

    DailyAnalytics.objects.update_or_create(
        date=target_date,
        defaults={
            'new_clients': new_clients,
            'active_clients': active_clients,
            'total_sessions': total_sessions,
            'total_data_gb': total_data_gb,
            'avg_session_duration_min': avg_session_duration_min,
            'offers_shown': offers_shown,
            'offers_clicked': offers_clicked,
            'offers_redeemed': offers_redeemed,
        }
    )

    return f"Analytics agregados para {target_date}"
