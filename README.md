# 🏪 Hotspot Marketing - Portal de Conexión con Ofertas

Aplicación de marketing digital para captar clientes a través de hotspots WiFi, conectando con redes sociales (Facebook, Instagram, WhatsApp) y enviando ofertas personalizadas.

## 🎯 Características

- **Portal Cautivo**: Página de login integrada con MikroTik
- **OAuth Social**: Autenticación con Facebook, Instagram, WhatsApp
- **Ofertas Personalizadas**: Recomendaciones basadas en perfil del cliente
- **Notificaciones WhatsApp**: Envío automático de ofertas por Twilio
- **Dashboard de Usuario**: Ver ofertas, estadísticas de uso
- **Panel de Admin**: Gestión de productos, ofertas, clientes
- **Integración MikroTik**: Sincronización de usuarios conectados
- **Analytics**: Seguimiento de visualizaciones, clicks, conversiones

## 📋 Stack Tecnológico

### Backend
- Django 4.2 + Django REST Framework
- PostgreSQL
- Celery + Redis (notificaciones)
- Twilio (WhatsApp)
- Python Social Auth (OAuth)

### Frontend
- React 18 + Vite
- Axios (HTTP client)
- React Router

### Infraestructura
- Railway (cloud deployment)
- Docker (containerización)
- GitHub Actions (CI/CD)

## 🚀 Instalación Rápida

### Requisitos Previos
- Python 3.10+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+
- Git

### 1. Clonar y Setup Backend

```bash
# Clonar repo
git clone <repo>
cd hotspot-marketing

# Setup Python
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Configurar variables de entorno
cp ../.env.example ../.env
# Editar .env con tus credenciales

# Migraciones
python manage.py migrate

# Crear superusuario (admin)
python manage.py createsuperuser

# Cargar datos de ejemplo (opcional)
python manage.py loaddata initial_data.json

# Correr servidor de desarrollo
python manage.py runserver
```

### 2. Setup Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Crear archivo .env
cp .env.example .env
# Editar VITE_API_URL si es necesario

# Servidor de desarrollo (puerto 5173)
npm run dev

# Build para producción
npm run build
```

## 🔧 Configuración

### Variables de Entorno Backend (.env)

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DB_NAME=hotspot_marketing
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# OAuth Facebook
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret

# OAuth Instagram
INSTAGRAM_APP_ID=your-app-id
INSTAGRAM_APP_SECRET=your-app-secret

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_WHATSAPP_NUMBER=+1234567890

# MikroTik
MIKROTIK_HOST=192.168.88.1
MIKROTIK_USER=admin
MIKROTIK_PASSWORD=your-password
MIKROTIK_PORT=8728

# Redis
REDIS_URL=redis://localhost:6379/0
```

## 📱 Flujo de Usuario

### 1. Cliente se conecta al WiFi
```
Cliente → MikroTik (Portal Cautivo)
       ↓
  Redirige a portal
       ↓
  SplashPage.jsx
```

### 2. Login OAuth
```
Cliente → Elige red social (Facebook/Instagram/WhatsApp)
       ↓
  OAuth Flow → Backend
       ↓
  Crear cliente + sesión
       ↓
  Dashboard de ofertas
```

### 3. Ver Ofertas
```
Backend determina ofertas eligibles:
- Estado: activa
- Público objetivo (primera visita vs repetido)
- Número mínimo de visitas
       ↓
  Frontend muestra ofertas
       ↓
  Registra visualización/clicks
```

### 4. Notificación WhatsApp (automática)
```
Celery Task → Verifica cliente con teléfono
          ↓
  Twilio → Envía oferta por WhatsApp
          ↓
  Registra envío en BD
```

## 🔌 Integración MikroTik

### Configurar Portal Cautivo en MikroTik

```bash
# Vía SSH o WinBox:

1. IP → Hotspot → Hotspot Profiles
   - Crear nuevo perfil
   - Login Page URL: https://tu-dominio.com/

2. IP → Hotspot → Hotspot Users
   - Crear usuario para portal: hotspot_user

3. IP → Service → API
   - Activar API REST en puerto 8728
```

### Parámetros URL hacia el Portal

MikroTik enviará al portal estos parámetros:
```
?mac=XX:XX:XX:XX:XX:XX
&ip=192.168.1.100
&username=hotspot_user
```

Tu aplicación debe capturarlos en `SplashPage.jsx` para sincronizar con la sesión.

## 📊 API Endpoints

### Autenticación
```
POST /api/clients/register_from_oauth/
- Registrar cliente desde OAuth
- Body: {social_id, social_platform, email, full_name, phone, mac_address}

POST /api/token-auth/
- Obtener token para requests autenticados
```

### Clientes
```
GET /api/clients/
- Listar clientes (admin)

GET /api/clients/{id}/
- Detalle de cliente

GET /api/clients/{id}/statistics/
- Estadísticas de cliente

GET /api/clients/{id}/sessions/
- Sesiones de cliente
```

### Sesiones
```
POST /api/sessions/create_session/
- Crear nueva sesión de conexión

POST /api/sessions/{id}/disconnect/
- Marcar fin de sesión
```

### Ofertas
```
GET /api/offers/
- Listar ofertas activas

GET /api/offers/for_client/?client_id=1
- Ofertas recomendadas para cliente

POST /api/offers/{id}/track_view/
- Registrar visualización

POST /api/offers/{id}/track_click/
- Registrar click

POST /api/offers/{id}/redeem/
- Registrar redención
```

## 📈 Admin Dashboard (Django)

Accede en `http://localhost:8000/admin/`

- Gestionar clientes y sesiones
- Crear productos y categorías
- Crear y editar ofertas
- Ver estadísticas
- Revisar redenciones

## 🐳 Deployment en Railway

### 1. Conectar GitHub

```bash
# Crear repo en GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin <github-repo>
git push -u origin main
```

### 2. Crear Proyecto en Railway

1. Ir a https://railway.app
2. New Project → GitHub Repository
3. Seleccionar este repo

### 3. Configurar Variables de Entorno

En Railway Dashboard:
- Variables → Agregar todas las del `.env.example`
- Database → Agregar PostgreSQL plugin
- Redis → Agregar Redis plugin

### 4. Deploy

Railway automáticamente:
1. Construye la imagen Docker
2. Ejecuta migraciones (Procfile migrate)
3. Colecta archivos estáticos
4. Inicia servidor Gunicorn

URL final será: `https://hotspot-marketing-production.railway.app/`

## 🧪 Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm run test
```

## 📝 Estructura de Carpetas

```
hotspot-marketing/
├── backend/
│   ├── config/          # Configuración Django
│   ├── apps/
│   │   ├── clients/     # Gestión de clientes
│   │   ├── products/    # Productos y ofertas
│   │   ├── notifications/  # WhatsApp/Email
│   │   ├── mikrotik/    # Integración MikroTik
│   │   └── analytics/   # Estadísticas
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── pages/       # Componentes de página
│   │   ├── components/  # Componentes reutilizables
│   │   ├── services/    # API services
│   │   ├── styles/      # CSS global
│   │   └── context/     # React Context
│   ├── public/
│   └── package.json
├── .env.example
├── Procfile
└── README.md
```

## 🔐 Seguridad

- CORS configurado para dominios permitidos
- CSRF protection habilitado
- HTTPS en producción (Railway)
- Tokens de autenticación almacenados en localStorage
- Datos sensibles en variables de entorno

## 🐛 Troubleshooting

### Error "PostgreSQL connection refused"
```bash
# Iniciar PostgreSQL
# Linux/Mac: brew services start postgresql
# Windows: Buscar PostgreSQL en servicios
```

### Error OAuth "Redirect URI mismatch"
- Verificar callback URL en Facebook/Instagram Developers
- Debe ser: `https://tu-dominio.com/callback/facebook`

### Error WhatsApp "Invalid phone number"
- Verificar formato: +56912345678 (con código país)
- Activar en Twilio: Account → Phone Numbers → Verified

## 📞 Contacto & Soporte

Para dudas sobre la implementación:
1. Revisar documentación API
2. Verificar logs en Railway dashboard
3. Consultar Django admin para estado de datos

## 📄 Licencia

MIT

---

**Creado con ❤️ para retail y restaurantes**
