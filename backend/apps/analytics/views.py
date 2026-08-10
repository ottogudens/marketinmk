"""
Analytics API Views — Dashboard de estadísticas para administradores.
"""
from datetime import timedelta

from django.utils import timezone
from django.db.models import Count, Sum, Avg, F, FloatField, Q
from django.db.models.functions import TruncDate
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.clients.models import Client, Session, ClientInteraction
from apps.products.models import Offer, OfferRedemption
from .models import DailyAnalytics
from .tasks import aggregate_daily_stats


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet de analytics para el panel de administración.
    Todos los endpoints requieren autenticación de admin.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        GET /api/analytics/overview/
        Resumen general del sistema (últimos 7 días vs período anterior).
        """
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)

        # Período actual (últimos 7 días)
        current = {
            'total_clients': Client.objects.count(),
            'new_clients': Client.objects.filter(first_seen__gte=seven_days_ago).count(),
            'active_clients': Client.objects.filter(last_seen__gte=seven_days_ago).count(),
            'total_sessions': Session.objects.filter(connected_at__gte=seven_days_ago).count(),
            'offers_redeemed': ClientInteraction.objects.filter(
                interaction_type='convert',
                created_at__gte=seven_days_ago
            ).count(),
        }

        # Período anterior (7-14 días atrás) para calcular variación
        previous = {
            'new_clients': Client.objects.filter(
                first_seen__gte=fourteen_days_ago, first_seen__lt=seven_days_ago
            ).count(),
            'active_clients': Client.objects.filter(
                last_seen__gte=fourteen_days_ago, last_seen__lt=seven_days_ago
            ).count(),
            'total_sessions': Session.objects.filter(
                connected_at__gte=fourteen_days_ago, connected_at__lt=seven_days_ago
            ).count(),
        }

        def pct_change(curr, prev):
            if prev == 0:
                return 100 if curr > 0 else 0
            return round(((curr - prev) / prev) * 100, 1)

        # Tasa de engagement
        total_views = ClientInteraction.objects.filter(
            interaction_type='view', created_at__gte=seven_days_ago
        ).count()
        total_clicks = ClientInteraction.objects.filter(
            interaction_type='click', created_at__gte=seven_days_ago
        ).count()
        engagement_rate = round((total_clicks / total_views * 100), 1) if total_views > 0 else 0

        # Top ofertas
        top_offers = list(
            Offer.objects.filter(status='active').annotate(
                views_count=Count('views', distinct=True),
                clicks_count=Count(
                    'clientinteraction',
                    filter=Q(clientinteraction__interaction_type='click'),
                    distinct=True
                )
            ).order_by('-views_count').values(
                'id', 'name', 'views_count', 'clicks_count', 'discount_value', 'discount_type'
            )[:5]
        )

        # Top clientes
        top_clients = list(
            Client.objects.annotate(
                session_count=Count('sessions', distinct=True)
            ).order_by('-session_count').values(
                'id', 'full_name', 'email', 'social_platform',
                'total_visits', 'last_seen', 'session_count'
            )[:10]
        )

        return Response({
            'period': '7_days',
            'kpis': {
                'total_clients': current['total_clients'],
                'new_clients': current['new_clients'],
                'new_clients_change': pct_change(current['new_clients'], previous['new_clients']),
                'active_clients': current['active_clients'],
                'active_clients_change': pct_change(current['active_clients'], previous['active_clients']),
                'total_sessions': current['total_sessions'],
                'total_sessions_change': pct_change(current['total_sessions'], previous['total_sessions']),
                'offers_redeemed': current['offers_redeemed'],
                'engagement_rate': engagement_rate,
            },
            'top_offers': top_offers,
            'top_clients': top_clients,
        })

    @action(detail=False, methods=['get'])
    def daily_stats(self, request):
        """
        GET /api/analytics/daily_stats/?days=30
        Estadísticas por día para gráficos.
        """
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)

        daily = (
            Session.objects.filter(connected_at__gte=since)
            .annotate(date=TruncDate('connected_at'))
            .values('date')
            .annotate(
                sessions=Count('id'),
                unique_clients=Count('client', distinct=True),
                total_data_mb=Sum(F('data_uploaded') + F('data_downloaded')) / 1048576,
            )
            .order_by('date')
        )

        # Nuevos clientes por día
        new_clients_by_day = (
            Client.objects.filter(first_seen__gte=since)
            .annotate(date=TruncDate('first_seen'))
            .values('date')
            .annotate(new_clients=Count('id'))
        )
        new_clients_map = {item['date']: item['new_clients'] for item in new_clients_by_day}

        result = []
        for row in daily:
            result.append({
                'date': row['date'],
                'sessions': row['sessions'],
                'unique_clients': row['unique_clients'],
                'total_data_mb': round(float(row['total_data_mb'] or 0), 2),
                'new_clients': new_clients_map.get(row['date'], 0),
            })

        return Response(result)

    @action(detail=False, methods=['get'])
    def clients_by_platform(self, request):
        """
        GET /api/analytics/clients_by_platform/
        Distribución de clientes por plataforma social.
        """
        data = (
            Client.objects.values('social_platform')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return Response(list(data))

    @action(detail=False, methods=['post'])
    def trigger_aggregation(self, request):
        """
        POST /api/analytics/trigger_aggregation/
        Fuerza la agregación manual (solo superadmin).
        """
        if not request.user.is_superuser:
            return Response({'error': 'Solo superadmin'}, status=403)
        date_str = request.data.get('date')
        result = aggregate_daily_stats.delay(date_str)
        return Response({'task_id': result.id, 'status': 'queued'})
