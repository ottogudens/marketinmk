"""
Celery tasks para la sincronización con dispositivos MikroTik via RouterOS API.
"""
from celery import shared_task
from django.utils import timezone
from librouteros import connect
from librouteros.exceptions import RouterOsError

from .models import MikroTikDevice, MikroTikLog, MikroTikUser
from apps.clients.models import Client, Session


@shared_task(name='apps.mikrotik.tasks.sync_mikrotik_users')
def sync_mikrotik_users():
    """
    Sincroniza usuarios activos de Hotspot en todos los dispositivos MikroTik registrados.
    Ejecutado periódicamente por Celery Beat (cada 5 minutos).
    """
    devices = MikroTikDevice.objects.filter(is_active=True)
    if not devices.exists():
        return "No hay dispositivos MikroTik activos"

    total_processed = 0

    for device in devices:
        target_host = device.wireguard_ip if (device.use_wireguard and device.wireguard_ip) else device.host
        try:
            api = connect(
                username=device.username,
                password=device.password,
                host=target_host,
                port=device.port,
                timeout=10
            )

            # Consultar usuarios activos en el Hotspot (/ip/hotspot/active)
            active_users = api(cmd='/ip/hotspot/active/print')

            processed = 0
            created = 0
            updated = 0

            for user_data in active_users:
                username = user_data.get('user', '')
                mac_address = user_data.get('mac-address', '')
                ip_address = user_data.get('address', '')
                bytes_in = int(user_data.get('bytes-in', 0))
                bytes_out = int(user_data.get('bytes-out', 0))

                if not mac_address:
                    continue

                processed += 1

                # Buscar o asociar cliente por MAC
                client = Client.objects.filter(mac_address=mac_address).first()

                mk_user, is_new = MikroTikUser.objects.update_or_create(
                    mac_address=mac_address,
                    defaults={
                        'mikrotik': device,
                        'username': username,
                        'client': client,
                        'is_active': True,
                    }
                )

                if is_new:
                    created += 1
                else:
                    updated += 1

                # Actualizar o registrar sesión activa
                if client:
                    session = Session.objects.filter(
                        client=client,
                        mac_address=mac_address,
                        disconnected_at__isnull=True
                    ).first()

                    if session:
                        session.data_uploaded = bytes_in
                        session.data_downloaded = bytes_out
                        session.save()
                    else:
                        Session.objects.create(
                            client=client,
                            mac_address=mac_address,
                            ip_address=ip_address,
                            data_uploaded=bytes_in,
                            data_downloaded=bytes_out
                        )

            device.last_sync = timezone.now()
            device.last_error = ""
            device.save()

            MikroTikLog.objects.create(
                mikrotik=device,
                log_type='sync_users',
                message=f"Sincronizados {processed} usuarios ({created} creados, {updated} actualizados).",
                status='success',
                users_processed=processed,
                users_created=created,
                users_updated=updated
            )

            total_processed += processed

        except (RouterOsError, Exception) as e:
            device.last_error = str(e)
            device.save()

            MikroTikLog.objects.create(
                mikrotik=device,
                log_type='error',
                message=f"Error al conectar con MikroTik: {str(e)}",
                status='error'
            )

    return f"Sincronización MikroTik completada. Usuarios procesados: {total_processed}"
