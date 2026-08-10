"""
Celery tasks para el envío de notificaciones (WhatsApp, Email).
"""
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


@shared_task(name='apps.notifications.tasks.send_whatsapp_offers')
def send_whatsapp_offers():
    """
    Envía ofertas activas por WhatsApp a clientes que aceptan marketing.
    Se ejecuta cada 2 horas vía Celery Beat.
    """
    from apps.clients.models import Client
    from apps.products.models import Offer
    from .models import Notification

    # Solo clientes activos que aceptan marketing y tienen teléfono
    clients = Client.objects.filter(
        accepts_marketing=True,
        phone__isnull=False,
        status='active'
    )

    # Ofertas activas
    active_offers = Offer.objects.filter(status='active')[:3]

    if not active_offers:
        return "No hay ofertas activas"

    sent = 0
    for client in clients:
        # Evitar spam: no enviar si ya recibió notificación en las últimas 24h
        recent = Notification.objects.filter(
            client=client,
            channel='whatsapp',
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()

        if recent:
            continue

        for offer in active_offers:
            _send_whatsapp_message(client, offer)
            sent += 1
            break  # Solo 1 oferta por cliente por ciclo

    return f"WhatsApp enviados: {sent}"


def _send_whatsapp_message(client, offer):
    """Envía un mensaje WhatsApp via Twilio"""
    from .models import Notification

    # Crear registro de notificación
    notification = Notification.objects.create(
        client=client,
        offer=offer,
        channel='whatsapp',
        title=f"¡Oferta especial para ti!",
        body=f"Hola {client.full_name}, tenemos una oferta especial: {offer.name}. ¡No te la pierdas!",
        status='pending'
    )

    try:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            notification.status = 'failed'
            notification.save()
            return

        from twilio.rest import Client as TwilioClient
        twilio_client = TwilioClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        message = twilio_client.messages.create(
            from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{client.phone}",
            body=notification.body
        )

        notification.status = 'sent'
        notification.external_id = message.sid
        notification.save()

    except Exception as e:
        notification.status = 'failed'
        notification.error_message = str(e)
        notification.save()


@shared_task(name='apps.notifications.tasks.send_notification')
def send_notification(notification_id):
    """Envía una notificación específica por ID"""
    from .models import Notification

    try:
        notification = Notification.objects.get(id=notification_id)
        if notification.channel == 'whatsapp':
            _send_whatsapp_message(notification.client, notification.offer)
    except Notification.DoesNotExist:
        pass
