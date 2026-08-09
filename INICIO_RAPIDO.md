# 🚀 Hotspot Marketing - Guía de Inicio Rápido

**Versión**: 1.0.0 MVP  
**Fecha**: Agosto 2026  
**Stack**: Django + React + PostgreSQL + Railway

---

## 📦 ¿Qué incluye la descarga?

```
hotspot-marketing/
│
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── clients/           # Gestión de clientes
│   │   ├── products/          # Productos y ofertas
│   │   ├── notifications/     # WhatsApp / Email
│   │   ├── mikrotik/          # Integración MikroTik
│   │   └── analytics/         # Estadísticas (vacío, para Fase 2)
│   ├── config/                # Configuración Django
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                   # React + Vite
│   ├── src/
│   │   ├── pages/             # SplashPage, Dashboard
│   │   ├── components/        # OfferCard
│   │   ├── services/          # API service
│   │   ├── context/           # AuthContext
│   │   └── styles/            # CSS
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── .env.example               # Variables de configuración
├── Procfile                   # Para Railway
├── README.md                  # Documentación completa
└── .git/                      # Repositorio git
```

---

## ⚡ Quickstart (5 minutos)

### 1. Extraer Archivo

```bash
tar -xzf hotspot-marketing.tar.gz
cd hotspot-marketing
```

### 2. Backend

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Configurar variables
cp ../.env.example ../.env
# Editar .env: cambiar DB_PASSWORD, FACEBOOK_APP_ID, etc.

# Migraciones (SQLite por defecto)
python manage.py migrate

# Crear admin
python manage.py createsuperuser

# Correr servidor
python manage.py runserver
```

**Backend está en**: `http://localhost:8000/`  
**Admin**: `http://localhost:8000/admin/`  
**API**: `http://localhost:8000/api/`

### 3. Frontend

```bash
cd frontend

# Instalar
npm install

# Configurar
cp .env.example .env

# Correr
npm run dev
```

**Frontend está en**: `http://localhost:5173/`

### 4. Probar Flujo

1. Abrir `http://localhost:5173/`
2. Click en "Conectar con Facebook" (verá error porque falta OAuth config)
3. Ir a `http://localhost:8000/admin/`
4. Crear productos manualmente
5. Crear ofertas
6. Crear cliente de prueba

---

## 🎯 Arquitectura en 60 Segundos

```
Cliente conecta a WiFi MikroTik
    ↓
MikroTik redirige a Portal
    ↓
SplashPage.jsx (login con OAuth)
    ↓
Backend registra Cliente
    ↓
UserDashboard muestra Ofertas
    ↓
Interacciones (view, click, redeem) → Base de datos
    ↓
Celery → WhatsApp notifications
```

---

## 🔧 Configuración Mínima (para empezar)

Editar `.env`:

```env
# Django (leave defaults)
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite local, cambiar a PostgreSQL en producción)
DB_NAME=hotspot_marketing
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432

# OAuth (dejar en blanco por ahora, agregar después)
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
INSTAGRAM_APP_ID=
INSTAGRAM_APP_SECRET=

# Twilio (dejar en blanco, agregar después)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=

# MikroTik (actualizar con tu dispositivo)
MIKROTIK_HOST=192.168.88.1
MIKROTIK_USER=admin
MIKROTIK_PASSWORD=
MIKROTIK_PORT=8728
```

---

## 📊 Estructura de Base de Datos

### Tablas principales:

```
clients
  ├─ id
  ├─ social_id (único por red social)
  ├─ full_name, email, phone
  ├─ total_visits, total_data_consumed
  └─ first_seen, last_seen

sessions
  ├─ id
  ├─ client_id (FK)
  ├─ mac_address, ip_address
  ├─ connected_at, disconnected_at
  └─ data_uploaded, data_downloaded

products
  ├─ id
  ├─ name, description, price
  ├─ category_id (FK)
  └─ image, active

offers
  ├─ id
  ├─ name, offer_type (discount, bogo, combo)
  ├─ discount_value, discount_type
  ├─ banner_image, products[] (M2M)
  ├─ start_date, end_date, status
  ├─ target_all, target_first_time, min_visits
  └─ show_on_splash, send_whatsapp

offer_views
  ├─ id
  ├─ offer_id, client_id, session_id (FKs)
  ├─ viewed_at
  └─ clicked, clicked_at

offer_redemptions
  ├─ id
  ├─ offer_id, client_id (FKs)
  ├─ redeemed_at
  ├─ amount_spent, value_applied
  └─ transaction_id

notifications
  ├─ id
  ├─ client_id, offer_id (FKs)
  ├─ channel (whatsapp, email, sms)
  ├─ title, body
  ├─ status (pending, sent, delivered, failed)
  └─ created_at, sent_at, read_at
```

---

## 🔌 Endpoints de API (Principales)

### Autenticación
```
POST /api/clients/register_from_oauth/
```

### Clientes
```
GET /api/clients/
POST /api/clients/register_from_oauth/
GET /api/clients/{id}/
GET /api/clients/{id}/statistics/
GET /api/clients/{id}/sessions/
```

### Sesiones
```
POST /api/sessions/create_session/
POST /api/sessions/{id}/disconnect/
```

### Ofertas
```
GET /api/offers/
GET /api/offers/{id}/
GET /api/offers/for_client/?client_id=1
POST /api/offers/{id}/track_view/
POST /api/offers/{id}/track_click/
POST /api/offers/{id}/redeem/
```

### Interacciones
```
POST /api/interactions/log_interaction/
```

---

## 🧪 Testing Manual

### Test 1: Crear cliente (sin OAuth)

```bash
curl -X POST http://localhost:8000/api/clients/register_from_oauth/ \
  -H "Content-Type: application/json" \
  -d '{
    "social_id": "12345678",
    "social_platform": "facebook",
    "email": "test@example.com",
    "full_name": "Juan Pérez",
    "phone": "+56912345678",
    "mac_address": "AA:BB:CC:DD:EE:FF"
  }'
```

Respuesta:
```json
{
  "id": 1,
  "social_platform": "facebook",
  "email": "test@example.com",
  "full_name": "Juan Pérez",
  "total_visits": 0,
  ...
}
```

### Test 2: Crear sesión

```bash
curl -X POST http://localhost:8000/api/sessions/create_session/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "ip_address": "192.168.1.100"
  }'
```

### Test 3: Ver ofertas

```bash
curl http://localhost:8000/api/offers/
```

---

## 🚀 Deployment en Railway (10 minutos)

### 1. Crear cuenta
- Ir a `https://railway.app`
- Sign up con GitHub

### 2. Conectar repo

```bash
git remote add origin https://github.com/tu-usuario/hotspot-marketing.git
git push -u origin main
```

### 3. En Railway Dashboard

- **New Project**
- **Import from GitHub**
- Seleccionar repo
- **Deploy**

Railway automáticamente:
1. Detecta `Procfile`
2. Crea PostgreSQL plugin
3. Ejecuta migraciones
4. Inicia servidor

**URL final**: `https://hotspot-marketing-xxxx.railway.app/`

---

## 📋 Configuración OAuth (después)

Cuando estés listo (Fase 2):

1. **Facebook Developers**: Crear app, copiar ID y Secret
2. **Instagram**: Usar mismo app que Facebook
3. **Twilio**: Crear cuenta, obtener credenciales de WhatsApp
4. **Actualizar `.env`** en Railway dashboard

---

## 🐛 Troubleshooting

### Error: "Module not found: apps.clients"
```bash
# Asegúrate que estás en backend/
cd backend
python manage.py runserver
```

### Error: "PostgreSQL connection refused"
```bash
# Usar SQLite por ahora (cambiar DB_NAME a algo.db)
DB_NAME=db.sqlite3
```

### Error: "Migrations pending"
```bash
python manage.py migrate
```

### Frontend no conecta a backend
```javascript
// Verificar en frontend/.env:
VITE_API_URL=http://localhost:8000/api
```

---

## 📁 Próximos Pasos

### Corto plazo (esta semana):
1. ✅ Setup local (Django + React)
2. ✅ Crear admin user
3. ✅ Agregar productos en admin
4. ✅ Crear 2-3 ofertas de prueba
5. ✅ Probar registro manual de cliente

### Mediano plazo (próximas 2 semanas):
1. Configurar OAuth (Facebook + Instagram)
2. Configurar Twilio para WhatsApp
3. Configurar MikroTik con portal
4. Testing de flujo completo
5. Deploy en Railway

### Largo plazo (mes 1-2):
1. Agregar dashboard de admin (Phase 2)
2. Sistema de cupones (Phase 3)
3. Integraciones con TPV/POS
4. App móvil (React Native)

---

## 📚 Documentación Completa

En los archivos descargados encontrarás:

- **`README.md`**: Documentación técnica completa
- **`CONFIGURACION_MIKROTIK_OAUTH.md`**: Setup detallado
- **`PROXIMAS_ITERACIONES.md`**: Fases futuras con código

---

## 💬 Preguntas Frecuentes

**P: ¿Puedo usar SQLite en producción?**  
R: No. Cambiar a PostgreSQL en Railway para escalar.

**P: ¿Cuánto cuesta hostearlo?**  
R: Railway: ~$5-20/mes. Twilio: por mensaje (~$0.01 cada uno).

**P: ¿Cómo conecto mi TPV actual?**  
R: Webhook en `/api/pos-webhook/` que recibe datos de venta.

**P: ¿Se puede usar WhatsApp Business sin Twilio?**  
R: Sí, directamente con WhatsApp API (Phase 6).

**P: ¿Qué pasa con los datos del cliente?**  
R: Almacenados en PostgreSQL. GDPR compliant si agregas opción de borrado.

---

## 🎓 Recursos Útiles

- **Django Docs**: `https://docs.djangoproject.com/`
- **Django REST**: `https://www.django-rest-framework.org/`
- **React Docs**: `https://react.dev/`
- **Vite**: `https://vitejs.dev/`
- **Railway**: `https://docs.railway.app/`
- **MikroTik API**: `https://help.mikrotik.com/docs/display/ROS/API`

---

## ✨ Diferenciadores de esta Solución

1. **OAuth Social Integrado**: Facebook, Instagram, WhatsApp en un portal
2. **WhatsApp Automático**: Notificaciones via Twilio sin SMS
3. **MikroTik Ready**: Arquitectura pensada para hotspots existentes
4. **Full Stack Modular**: Cada componente es independiente
5. **Analytics Listos**: Métricas de engagement, conversión, ROI
6. **Fácil de Extender**: Código limpio, comentado, reutilizable

---

**¡Listo para empezar?**

```bash
tar -xzf hotspot-marketing.tar.gz
cd hotspot-marketing
python -m venv venv
source venv/bin/activate
cd backend && pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Y en otra terminal:

```bash
cd frontend
npm install
npm run dev
```

**¡Abierto en http://localhost:5173/ 🚀**

---

Creado con ❤️ para retail y restaurantes  
Preguntas: Ver archivos de documentación
