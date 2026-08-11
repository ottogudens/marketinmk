"""
Wireguard VPN Server Configuration & Management for MarketinMK RouterOS Gateway.
"""
import os
import subprocess
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import MikroTikDevice


def generate_wireguard_keys():
    """Genera un par de claves privada/pública para Wireguard usando wg cli o fallback python"""
    try:
        privkey = subprocess.check_output(['wg', 'genkey']).decode().strip()
        pubkey = subprocess.check_output(['wg', 'pubkey'], input=privkey.encode()).decode().strip()
        return privkey, pubkey
    except Exception:
        # Fallback de desarrollo si no existe wg binario en el container
        import base64
        import secrets
        privkey = base64.b64encode(secrets.token_bytes(32)).decode()
        pubkey = base64.b64encode(secrets.token_bytes(32)).decode()
        return privkey, pubkey


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_wireguard_server_status(request):
    """
    GET /api/mikrotik/wireguard/server_status/
    Devuelve el estado de la interfaz del servidor Wireguard.
    """
    server_public_key = getattr(settings, 'WIREGUARD_SERVER_PUBLIC_KEY', 'WG_SERVER_PUBKEY_EXAMPLE_ABC123=')
    server_listen_port = getattr(settings, 'WIREGUARD_SERVER_PORT', 51820)
    server_endpoint = getattr(settings, 'WIREGUARD_SERVER_ENDPOINT', 'vpn.marketinmk.com')

    devices = MikroTikDevice.objects.filter(is_active=True)
    peers = [{
        'device_id': dev.id,
        'device_name': dev.name,
        'wireguard_ip': dev.wireguard_ip or f"10.8.0.{dev.id + 1}",
        'wireguard_public_key': dev.wireguard_public_key or 'Sin clave registrada',
        'use_wireguard': dev.use_wireguard,
        'status': 'conectado' if dev.last_sync and (dev.last_error == "") else 'desconectado'
    } for dev in devices]

    return Response({
        'server_ip': '10.8.0.1/24',
        'listen_port': server_listen_port,
        'public_key': server_public_key,
        'endpoint': f"{server_endpoint}:{server_listen_port}",
        'active_peers': peers
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def generate_mikrotik_script(request, device_id):
    """
    POST /api/mikrotik/wireguard/generate_script/<device_id>/
    Genera el script ejecutable en RouterOS para autoconfigurar la VPN Wireguard
    sin necesidad de IP pública en el router del cliente.
    """
    try:
        device = MikroTikDevice.objects.get(id=device_id)
    except MikroTikDevice.DoesNotExist:
        return Response({'error': 'Dispositivo MikroTik no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    server_endpoint = request.data.get('server_endpoint', getattr(settings, 'WIREGUARD_SERVER_ENDPOINT', 'vpn.marketinmk.com'))
    server_port = getattr(settings, 'WIREGUARD_SERVER_PORT', 51820)
    server_pubkey = getattr(settings, 'WIREGUARD_SERVER_PUBLIC_KEY', 'SERVER_PUBLIC_KEY_PLACEHOLDER=')

    default_ip = device.host if (device.host and device.host.startswith('10.8.')) else f"10.8.0.{device.id + 1}"
    wg_ip = device.wireguard_ip or request.data.get('assigned_ip', default_ip)
    if not device.wireguard_ip:
        device.wireguard_ip = wg_ip
        device.save()

    # Script autoejecutable para MikroTik RouterOS v7+
    routeros_script = f"""# =========================================================
# Script de Autoconfiguración Wireguard para RouterOS v7
# Mercado: MarketinMK Hotspot Manager
# Dispositivo: {device.name}
# IP VPN Asignada: {wg_ip}/32
# =========================================================

:do {{ /interface wireguard add listen-port=51820 name=wg-marketinmk comment="VPN MarketinMK Cloud" }} on-error={{}}
:do {{ /interface wireguard peers add interface=wg-marketinmk endpoint-address="{server_endpoint}" endpoint-port={server_port} public-key="{server_pubkey}" allowed-address=10.8.0.0/24 persistent-keepalive=25s comment="Central Server" }} on-error={{}}
:do {{ /ip address add address={wg_ip}/24 interface=wg-marketinmk comment="IP VPN MarketinMK" }} on-error={{}}
/ip service set api port={device.port} disabled=no address=10.8.0.0/24
:do {{ /system script add name=marketinmk_keepalive owner=admin source=":ping 10.8.0.1 count=3" }} on-error={{}}

:put "========================================================="
:put "✅ Configuración Wireguard para {device.name} completada!"
:put "Obtén la clave pública del router ejecutando:"
:put "/interface wireguard print"
:put "========================================================="
"""

    return Response({
        'device_id': device.id,
        'device_name': device.name,
        'assigned_wireguard_ip': wg_ip,
        'routeros_script': routeros_script
    })
