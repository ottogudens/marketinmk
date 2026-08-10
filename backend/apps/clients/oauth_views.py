import requests
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Client, Session
from .serializers import ClientSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def oauth_callback(request, provider):
    """
    Procesa el código de retorno de OAuth de Facebook o Instagram.
    POST /api/auth/callback/<provider>/
    Body: { "code": "...", "redirect_uri": "...", "mac_address": "..." }
    """
    code = request.data.get('code')
    redirect_uri = request.data.get('redirect_uri')
    mac_address = request.data.get('mac_address', '')
    
    if not code or not redirect_uri:
        return Response(
            {'error': 'Faltan parámetros requeridos (code, redirect_uri)'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if provider == 'facebook':
        app_id = getattr(settings, 'FACEBOOK_APP_ID', '')
        app_secret = getattr(settings, 'FACEBOOK_APP_SECRET', '')
        token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
        profile_url = 'https://graph.facebook.com/me?fields=id,name,email,picture'
    elif provider == 'instagram':
        app_id = getattr(settings, 'INSTAGRAM_APP_ID', '')
        app_secret = getattr(settings, 'INSTAGRAM_APP_SECRET', '')
        token_url = 'https://api.instagram.com/oauth/access_token'
        profile_url = 'https://graph.instagram.com/me?fields=id,username'
    else:
        return Response({'error': 'Proveedor de OAuth no soportado'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 1. Intercambiar código por Access Token
        token_resp = requests.post(token_url, data={
            'client_id': app_id,
            'client_secret': app_secret,
            'redirect_uri': redirect_uri,
            'code': code,
            'grant_type': 'authorization_code'
        }, timeout=10)
        
        token_json = token_resp.json()
        if 'error' in token_json:
            return Response({'error': token_json['error'].get('message', 'Error de OAuth')}, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_json.get('access_token')

        # 2. Obtener información del perfil
        if provider == 'facebook':
            profile_resp = requests.get(profile_url, params={'access_token': access_token}, timeout=10)
        else:
            profile_resp = requests.get(profile_url, params={'access_token': access_token}, timeout=10)

        profile_json = profile_resp.json()
        social_id = profile_json.get('id')
        full_name = profile_json.get('name') or profile_json.get('username') or f"Usuario {provider.capitalize()}"
        email = profile_json.get('email') or f"{social_id}@{provider}.com"
        picture = profile_json.get('picture', {}).get('data', {}).get('url') if provider == 'facebook' else None

        if not social_id:
            return Response({'error': 'No se pudo obtener el ID social'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Buscar o crear Django User y Client
        username = f"{provider}_{social_id}"
        user, _ = User.objects.get_or_create(username=username, defaults={'email': email, 'first_name': full_name})
        
        client, created = Client.objects.get_or_create(
            social_id=social_id,
            defaults={
                'user': user,
                'social_platform': provider,
                'email': email,
                'full_name': full_name,
                'profile_picture': picture,
                'mac_address': mac_address or None,
            }
        )

        if not created:
            client.total_visits += 1
            if mac_address and not client.mac_address:
                client.mac_address = mac_address
            client.save()

        # 4. Registrar Sesión si viene mac_address e ip
        ip_address = request.META.get('REMOTE_ADDR', '')
        if mac_address and ip_address:
            Session.objects.create(client=client, mac_address=mac_address, ip_address=ip_address)

        # 5. Generar o recuperar Token DRF
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'client': ClientSerializer(client).data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error en procesamiento OAuth: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Invalida el token del usuario actual.
    """
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Sesión cerrada exitosamente'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Devuelve la información del cliente autenticado actual.
    """
    try:
        client = request.user.client
        return Response(ClientSerializer(client).data)
    except Exception:
        return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
