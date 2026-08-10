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


@shared_task(name='apps.analytics.tasks.generate_personalized_offers')
def generate_personalized_offers(client_id):
    """
    Genera una oferta o sugerencia personalizada mediante IA (Gemini / Anthropic)
    basada en el historial de visitas, consumo e interacciones del cliente.
    """
    import json
    from django.conf import settings
    from apps.clients.models import Client
    from apps.products.models import Offer
    from .models import AISuggestion

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return f"Cliente con id {client_id} no encontrado"

    active_offers = Offer.objects.filter(status='active')
    offers_data = [{'id': o.id, 'name': o.name, 'discount': str(o.discount_value)} for o in active_offers]

    views_count = client.interactions.filter(interaction_type='view').count()
    clicks_count = client.interactions.filter(interaction_type='click').count()

    prompt = f"""
    Analiza la información de este cliente de hotspot WiFi:
    - Nombre: {client.full_name}
    - Total de Visitas: {client.total_visits}
    - Consumo total de datos: {round(client.total_data_consumed / (1024*1024), 2)} MB
    - Ofertas Vistas: {views_count}
    - Ofertas Clicadas: {clicks_count}

    Ofertas activas disponibles en el negocio:
    {json.dumps(offers_data)}

    Genera una sugerencia de oferta recomendada.
    Devuelve estrictamente un JSON con las siguientes claves:
    {{
       "title": "<Título atractivo y personalizado>",
       "reasoning": "<Explicación de 1 frase del por qué es ideal para este cliente>",
       "suggested_offer_id": <id de una de las ofertas disponibles o null>,
       "discount_percent": <un número entero de descuento recomendado entre 5 y 25>
    }}
    """

    # Intentar usar la API disponible o un motor inteligente interno
    title = f"¡Especial para ti, {client.full_name.split()[0]}!"
    reasoning = f"Detectamos que has visitado nuestro hotspot {client.total_visits} veces. ¡Premio a tu lealtad!"
    suggested_offer_id = active_offers.first().id if active_offers.exists() else None
    discount_percent = 15

    try:
        # Si la API KEY de Gemini está configurada
        api_key = getattr(settings, 'GEMINI_API_KEY', '') or getattr(settings, 'ANTHROPIC_API_KEY', '')
        if api_key:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                res_json = res.json()
                text_response = res_json['candidates'][0]['content']['parts'][0]['text']
                # Extraer JSON si viene en bloque markdown
                if "```json" in text_response:
                    text_response = text_response.split("```json")[1].split("```")[0].strip()
                data = json.loads(text_response)
                title = data.get('title', title)
                reasoning = data.get('reasoning', reasoning)
                suggested_offer_id = data.get('suggested_offer_id', suggested_offer_id)
                discount_percent = data.get('discount_percent', discount_percent)
    except Exception as err:
        pass

    offer_obj = Offer.objects.filter(id=suggested_offer_id).first() if suggested_offer_id else None

    suggestion = AISuggestion.objects.create(
        client=client,
        suggested_offer=offer_obj,
        title=title,
        reasoning=reasoning,
        suggested_discount_percent=discount_percent
    )

    return f"Sugerencia IA generada para cliente {client.id}: {suggestion.title}"
