# 📖 Guía de Configuración: MikroTik + OAuth + Twilio

Este documento contiene los pasos específicos para configurar tu hotspot con MikroTik, OAuth social y notificaciones por WhatsApp.

---

## 1️⃣ Configuración de MikroTik (Portal Cautivo)

### 1.1 Acceso a MikroTik

**Opción A: Vía WinBox (Windows)**
- Descargar WinBox desde `https://mikrotik.com/download`
- Conectar a `192.168.88.1`
- Usuario: `admin` (sin contraseña por defecto)

**Opción B: Vía SSH**
```bash
ssh admin@192.168.88.1
```

**Opción C: Interfaz Web**
```
http://192.168.88.1:8291/
```

### 1.2 Crear Perfil de Hotspot

En **WinBox → IP → Hotspot → Hotspot Profiles**:

1. Click `+` (New)
2. Configurar:
   - **Name**: `default` o tu nombre
   - **Login By**: `HTTP CHAP`
   - **HTTP Proxy**: Check
   - **HTML**: Check

3. En la pestaña **DNS**:
   - Static DNS: Check
   - DNS Servers: `8.8.8.8 8.8.4.4`

4. **Aceptar**

### 1.3 Configurar URL de Portal Cautivo

En el mismo perfil, pestaña **Login**:

```
Login Page URL: https://tu-dominio.com/
```

**Ejemplo:**
```
https://hotspot.mirestaurante.cl/
```

⚠️ **IMPORTANTE**: 
- Debe ser HTTPS (SSL/TLS válido)
- El certificado debe ser válido (no auto-firmado en producción)
- MikroTik debe poder alcanzar la URL

### 1.4 Crear Interfaz de Hotspot

En **IP → Hotspot → Hotspot**:

1. Click `+` (New)
2. Configurar:
   - **Name**: `hotspot1`
   - **Interface**: `ether2` (o tu interfaz WiFi)
   - **Address Pool**: `192.168.100.2-192.168.100.254`
   - **Profile**: `default`
   - **Certificate**: Seleccionar certificado SSL válido

3. **Aceptar**

### 1.5 Configurar IP de la Interfaz

En **IP → Addresses**:

1. Click `+` (New)
2. Configurar:
   - **Address**: `192.168.100.1/24`
   - **Interface**: `ether2`

3. **Aceptar**

### 1.6 Crear Usuario de Hotspot

En **IP → Hotspot → Users**:

1. Click `+` (New)
2. Configurar:
   - **Name**: `hotspot_user`
   - **Password**: `hotspot_password` (cambiar en producción)
   - **Profile**: `default`
   - **Disabled**: `No`

3. **Aceptar**

### 1.7 Activar API REST (para integración)

En **System → API**:

1. Click `+` (New service)
2. Configurar:
   - **Name**: `api`
   - **Port**: `8728`
   - **Certificate**: `none`
   - **Require Certificate**: `No`

3. **Aceptar**

**O vía SSH:**
```bash
/ip service
set api disabled=no port=8728
```

### 1.8 Parámetros que envía MikroTik

Cuando un cliente se conecta, MikroTik redirige con parámetros:

```
https://tu-dominio.com/?mac=XX:XX:XX:XX:XX:XX
                       &ip=192.168.100.50
                       &username=hotspot_user
```

Tu aplicación (`SplashPage.jsx`) debe **capturar estos parámetros** al cargar.

---

## 2️⃣ Configuración de OAuth (Facebook, Instagram, WhatsApp)

### 2.1 Crear Aplicación en Facebook Developers

**Link**: `https://developers.facebook.com/`

#### Pasos:

1. **Login** con tu cuenta de Facebook
2. **My Apps → Create App**
3. Seleccionar tipo: **Consumer**
4. Llenar:
   - **App Name**: `Hotspot Marketing`
   - **App Contact Email**: tu-email@example.com
   - **App Purpose**: Seleccionar "Business"

5. **Create App**

#### Configurar Settings

En **Settings → Basic**:
- Copiar y guardar:
  - **App ID** → `FACEBOOK_APP_ID`
  - **App Secret** → `FACEBOOK_APP_SECRET`

#### Agregar Producto: Facebook Login

1. En el dashboard, click **+ Add Product**
2. Buscar **Facebook Login**
3. Click **Set Up**
4. Seleccionar **Web**

#### Configurar URLs de Redireccionamiento

En **Facebook Login → Settings**:

```
Authorized JavaScript Origins:
- http://localhost:5173
- http://localhost:3000
- https://tu-dominio.com

Valid OAuth Redirect URIs:
- http://localhost:5173/callback/facebook
- http://localhost:3000/callback/facebook
- https://tu-dominio.com/callback/facebook
```

#### Agregar Testers/Administradores

En **Roles → Test Users**:
- Click `+` (Add Test User)
- Crear usuario de prueba para testing

### 2.2 Configuración para Instagram (mediante Facebook)

En la misma aplicación de Facebook:

1. **Add Product → Instagram Graph API**
2. El acceso a Instagram se hace a través de Facebook Login
3. Usar `FACEBOOK_APP_ID` como `INSTAGRAM_APP_ID`

### 2.3 Configuración de WhatsApp Business

**Link**: `https://www.whatsapp.com/business/`

1. **Crear Business Account** en Meta Business Manager
2. Ir a **Apps and Assets → Apps**
3. Crear/Seleccionar app que ya tenga Facebook Login

#### Agregar WhatsApp en la App

1. En el dashboard de la app: **+ Add Product**
2. Seleccionar **WhatsApp**
3. Click **Set Up**

#### Obtener Access Token

1. En **WhatsApp → Getting Started**
2. Copiar **Phone Number ID** y **Business Account ID**

Para testing, usar números verificados en Twilio.

### 2.4 Variables de Entorno

En tu `.env` del backend:

```env
# Facebook OAuth
FACEBOOK_APP_ID=123456789012345
FACEBOOK_APP_SECRET=abcdef1234567890abcdef1234567890

# Instagram (igual que Facebook por ahora)
INSTAGRAM_APP_ID=123456789012345
INSTAGRAM_APP_SECRET=abcdef1234567890abcdef1234567890

# WhatsApp (lo configuraremos en Twilio)
```

En tu `.env.local` del frontend:

```env
VITE_API_URL=https://tu-dominio.com/api
VITE_FACEBOOK_APP_ID=123456789012345
VITE_INSTAGRAM_APP_ID=123456789012345
```

---

## 3️⃣ Configuración de Twilio (WhatsApp Notifications)

### 3.1 Crear Cuenta en Twilio

**Link**: `https://www.twilio.com/`

1. **Sign Up**
2. Verificar email y teléfono
3. Seleccionar producto: **WhatsApp**

### 3.2 Obtener Credenciales

En el dashboard de Twilio:

1. **Account → Account SID**
2. **Account → Auth Token** (copiar y guardar en `.env`)

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxx
```

### 3.3 Configurar WhatsApp Sandbox

En **Messaging → Try it out → Send a WhatsApp message**:

1. Seguir instrucciones para verificar tu número
2. Copiar número de Twilio asignado:

```env
TWILIO_WHATSAPP_NUMBER=+1234567890  # Será algo como +14155552671
```

### 3.4 Activar WhatsApp Business Integration

Para producción (después de testing):

1. Registrar **WhatsApp Business Account** en Meta
2. Conectar a Twilio mediante webhook
3. Usar templates de mensajes pre-aprobados

**Comando Python para enviar prueba:**

```python
from twilio.rest import Client

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

message = client.messages.create(
    body="¡Hola! Aquí está tu oferta especial 🎁",
    from_="whatsapp:+1234567890",  # Tu número Twilio
    to="whatsapp:+56912345678"  # Número del cliente
)

print(message.sid)
```

### 3.5 Flujo de Notificaciones en la App

El sistema automáticamente:

1. **Cuando cliente se conecta** → Crea registro
2. **Después de 5 minutos** → Celery task envía oferta por WhatsApp
3. **Twilio envía mensaje** → "¡Hola Juan! Tenemos 20% descuento en X. Válido hasta mañana"
4. **App registra estado** → Entregado, leído, etc.

**En** `apps/notifications/tasks.py` (crear este archivo):

```python
from celery import shared_task
from apps.notifications.models import Notification
from apps.products.models import Offer
from apps.clients.models import Client
from twilio.rest import Client as TwilioClient
from django.conf import settings

@shared_task
def send_whatsapp_offers():
    """Enviar ofertas a clientes nuevos por WhatsApp"""
    
    # Obtener clientes que se conectaron hace 5 min
    clients = Client.objects.filter(
        last_seen__gte=timezone.now() - timedelta(minutes=5),
        accepts_marketing=True,
        phone__isnull=False
    )
    
    for client in clients:
        # Obtener ofertas elegibles
        offers = Offer.objects.filter(
            status='active',
            send_whatsapp=True,
            end_date__gte=timezone.now()
        )[:1]  # Solo la mejor oferta
        
        for offer in offers:
            # Crear notificación
            notification = Notification.objects.create(
                client=client,
                offer=offer,
                channel='whatsapp',
                title=offer.name,
                body=f"¡{client.full_name}! {offer.description}\n{offer.discount_value}% OFF\nVálido hasta {offer.end_date.strftime('%d/%m')}"
            )
            
            # Enviar por Twilio
            try:
                twilio_client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                
                message = twilio_client.messages.create(
                    body=notification.body,
                    from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                    to=f"whatsapp:{client.phone}"
                )
                
                notification.status = 'sent'
                notification.external_id = message.sid
                notification.sent_at = timezone.now()
                notification.save()
                
            except Exception as e:
                notification.status = 'failed'
                notification.error_message = str(e)
                notification.save()
```

---

## 4️⃣ Configurar Callback de MikroTik en Django

Crear endpoint para recibir eventos de MikroTik:

**En** `backend/apps/mikrotik/views.py`:

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MikroTikDevice, MikroTikLog

@api_view(['POST'])
def mikrotik_webhook(request):
    """
    Recibe notificaciones de MikroTik cuando:
    - Usuario se conecta
    - Usuario se desconecta
    - Cambios de ancho de banda
    """
    
    data = request.data
    event_type = data.get('event')
    mac_address = data.get('mac')
    
    if event_type == 'login':
        # Nuevo cliente conectado
        from apps.clients.models import Client, Session
        try:
            client = Client.objects.get(mac_address=mac_address)
            Session.objects.create(
                client=client,
                mac_address=mac_address,
                ip_address=data.get('ip')
            )
        except Client.DoesNotExist:
            pass  # Cliente no registrado aún
    
    elif event_type == 'logout':
        # Cliente desconectado
        Session.objects.filter(
            mac_address=mac_address,
            disconnected_at__isnull=True
        ).update(disconnected_at=timezone.now())
    
    return Response({'status': 'ok'})
```

**En** `backend/config/urls.py`:

```python
from apps.mikrotik.views import mikrotik_webhook

urlpatterns = [
    # ... otros patterns
    path('api/mikrotik/webhook/', mikrotik_webhook, name='mikrotik_webhook'),
]
```

**Configurar en MikroTik** (Script):

```bash
/system script
add name="notify_hotspot_app" source="
:local url \"https://tu-dominio.com/api/mikrotik/webhook/\"

/tool fetch url=\$url method=post \
  http-header-field=\"Content-Type: application/json\" \
  http-data=\"{\\\"event\\\":\\\"login\\\", \\\"mac\\\":\\\"[/interface ethernet get [find default-name=ether2] mac-address]\\\"}\";
"

/system scheduler
add name="check_hotspot" interval=1m on-event="/system script run notify_hotspot_app"
```

---

## 5️⃣ Testing Local

### 5.1 Simular conexión a hotspot

En tu máquina local:

```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend  
cd frontend
npm run dev

# Terminal 3: Acceder
# http://localhost:5173/?mac=AA:BB:CC:DD:EE:FF&ip=192.168.1.100
```

### 5.2 Testing OAuth Facebook

1. Ir a `http://localhost:5173/`
2. Click en "Conectar con Facebook"
3. Loguear con test user de Facebook Developers
4. Debe crear cliente en BD

**Verificar en Django Admin:**
```
http://localhost:8000/admin/clients/client/
```

### 5.3 Testing WhatsApp

```bash
# En terminal de Django shell
python manage.py shell

from apps.notifications.tasks import send_whatsapp_offers
send_whatsapp_offers()
```

Revisa tu WhatsApp si recibiste el mensaje.

---

## 6️⃣ Pasos Finales para Producción

### Checklist:

- [ ] Certificado SSL válido en servidor
- [ ] MikroTik configurado con HTTPS
- [ ] Credenciales de OAuth actualizadas
- [ ] Token de Twilio guardado en variables
- [ ] PostgreSQL en producción (Railway)
- [ ] Redis configurado (Railway)
- [ ] Django SECRET_KEY aleatorio
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configurado
- [ ] Variables de entorno sincronizadas en Railway
- [ ] Database migrations ejecutadas
- [ ] Usuarios de test borrados
- [ ] Test del flujo completo de usuario

### Deploy en Railway

```bash
git add .
git commit -m "Production ready"
git push origin main
```

Railway automáticamente:
1. Detecta cambios
2. Construye imagen Docker
3. Ejecuta migraciones
4. Redeploy

---

## 📞 Debugging

### Revisar logs de Twilio

```python
from twilio.rest import Client

client = Client(ACCOUNT_SID, AUTH_TOKEN)
messages = client.messages.list(limit=20)

for message in messages:
    print(f"{message.sid}: {message.status}")
```

### Revisar BD de Django

```bash
python manage.py shell

from apps.clients.models import Client
from apps.notifications.models import Notification

# Clientes registrados
Client.objects.all().values_list('full_name', 'phone', 'last_seen')

# Notificaciones enviadas
Notification.objects.filter(channel='whatsapp').values_list('client', 'status', 'sent_at')
```

### Monitorear MikroTik

```bash
ssh admin@192.168.88.1

/ip hotspot
print

/ip hotspot active
print
```

---

¡Listo! Tu aplicación de hotspot marketing está lista para captar clientes 🎉
