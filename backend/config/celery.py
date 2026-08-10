"""
Celery application configuration for MarketinMK.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('marketinmk')

# Leer configuración desde Django settings con prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas en todas las apps instaladas
app.autodiscover_tasks()

# Beat Schedule — tareas periódicas
app.conf.beat_schedule = {
    'aggregate-daily-stats': {
        'task': 'apps.analytics.tasks.aggregate_daily_stats',
        'schedule': crontab(hour=0, minute=5),  # Cada medianoche +5min
    },
    'send-whatsapp-offers': {
        'task': 'apps.notifications.tasks.send_whatsapp_offers',
        'schedule': crontab(hour='*/2'),  # Cada 2 horas
    },
    'sync-mikrotik-users': {
        'task': 'apps.mikrotik.tasks.sync_mikrotik_users',
        'schedule': crontab(minute='*/5'),  # Cada 5 minutos
    },
}

app.conf.timezone = 'America/Santiago'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
