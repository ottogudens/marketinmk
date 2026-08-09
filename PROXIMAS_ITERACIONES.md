# 🚀 Próximas Iteraciones - Hotspot Marketing

Basado en tu experiencia constructiva iterativa (JARVIS, NurseCare, MecanIA), aquí están las funcionalidades que puedes agregar fase por fase.

---

## ⏳ Fase 1: MVP (Ya incluido en la descarga)

- ✅ Portal cautivo con OAuth
- ✅ Registro de clientes (Facebook, Instagram, WhatsApp)
- ✅ Dashboard de usuario con ofertas
- ✅ API REST para interacciones
- ✅ Notificaciones WhatsApp automáticas
- ✅ Integración MikroTik (lectura de usuarios)

---

## 🎯 Fase 2: Analytics & Engagement (Semana 1-2)

### Agregar al backend:

**1. Dashboard de Admin** (`apps/analytics/views.py`):

```python
from django.db.models import Count, Sum, Q
from datetime import timedelta
from django.utils import timezone

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False)
    def overview(self, request):
        """Dashboard principal de stats"""
        
        # Últimos 7 días
        seven_days = timezone.now() - timedelta(days=7)
        
        stats = {
            'total_clients': Client.objects.count(),
            'active_clients': Client.objects.filter(
                last_seen__gte=seven_days
            ).count(),
            'total_sessions': Session.objects.count(),
            'total_offers': Offer.objects.filter(status='active').count(),
            'total_redemptions': OfferRedemption.objects.filter(
                redeemed_at__gte=seven_days
            ).count(),
            'revenue': OfferRedemption.objects.filter(
                redeemed_at__gte=seven_days
            ).aggregate(Sum('amount_spent'))['amount_spent__sum'] or 0,
            
            # Engagement rate
            'engagement_rate': self._calculate_engagement_rate(),
            
            # Top offers
            'top_offers': Offer.objects.annotate(
                views=Count('views'),
                redemptions=Count('redemptions')
            ).order_by('-views')[:5],
            
            # Top clients
            'top_clients': Client.objects.annotate(
                visits=Count('sessions')
            ).order_by('-visits')[:10],
        }
        
        return Response(stats)
    
    @action(detail=False)
    def daily_stats(self, request):
        """Estadísticas por día (últimos 30 días)"""
        
        last_30 = timezone.now() - timedelta(days=30)
        
        daily = Session.objects.filter(
            connected_at__gte=last_30
        ).extra(
            select={'date': 'DATE(connected_at)'}
        ).values('date').annotate(
            sessions=Count('id'),
            total_data_mb=Sum(
                F('data_uploaded') + F('data_downloaded'),
                output_field=FloatField()
            ) / (1024*1024),
            avg_duration_min=Avg(
                F('duration_seconds'),
                output_field=FloatField()
            ) / 60
        ).order_by('date')
        
        return Response(daily, status=200)
```

**2. Guardar datos en Analytics model**:

```python
# apps/analytics/models.py

class DailyAnalytics(models.Model):
    date = models.DateField(unique=True)
    
    new_clients = models.IntegerField(default=0)
    active_clients = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    total_data_gb = models.FloatField(default=0)
    avg_session_duration = models.FloatField(default=0)
    
    offers_shown = models.IntegerField(default=0)
    offers_clicked = models.IntegerField(default=0)
    offers_redeemed = models.IntegerField(default=0)
    
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics {self.date}"
```

**3. Celery task para agregación diaria**:

```python
# apps/analytics/tasks.py

@shared_task
def aggregate_daily_stats():
    """Ejecutar cada medianoche"""
    
    yesterday = timezone.now().date() - timedelta(days=1)
    
    stats = {
        'date': yesterday,
        'new_clients': Client.objects.filter(
            first_seen__date=yesterday
        ).count(),
        'active_clients': Client.objects.filter(
            last_seen__date=yesterday
        ).count(),
        'total_sessions': Session.objects.filter(
            connected_at__date=yesterday
        ).count(),
        # ... más stats
    }
    
    DailyAnalytics.objects.update_or_create(
        date=yesterday,
        defaults=stats
    )
```

**4. Agregar a settings.py**:

```python
# Celery Beat Schedule
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'aggregate-daily-stats': {
        'task': 'apps.analytics.tasks.aggregate_daily_stats',
        'schedule': crontab(hour=0, minute=0),  # Cada medianoche
    },
    'send-whatsapp-offers': {
        'task': 'apps.notifications.tasks.send_whatsapp_offers',
        'schedule': crontab(hour='*/2'),  # Cada 2 horas
    },
}
```

### Agregar al frontend:

**1. Admin Dashboard** (`frontend/src/pages/AdminDashboard.jsx`):

```jsx
import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import api from '../services/api';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [dailyStats, setDailyStats] = useState([]);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    const overview = await api.get('/analytics/overview/');
    const daily = await api.get('/analytics/daily_stats/');
    
    setStats(overview.data);
    setDailyStats(daily.data);
  };

  if (!stats) return <div>Cargando...</div>;

  return (
    <div className="admin-dashboard">
      <h1>Dashboard de Analytics</h1>
      
      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPICard label="Clientes Totales" value={stats.total_clients} />
        <KPICard label="Clientes Activos (7d)" value={stats.active_clients} />
        <KPICard label="Ingresos (7d)" value={`$${stats.revenue}`} />
        <KPICard label="Tasa Engagement" value={`${stats.engagement_rate}%`} />
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="chart">
          <h3>Sesiones Diarias (últimos 30 días)</h3>
          <BarChart data={dailyStats}>
            <CartesianGrid />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="sessions" fill="#ff6b35" />
          </BarChart>
        </div>

        <div className="chart">
          <h3>Consumo de Datos (GB)</h3>
          <LineChart data={dailyStats}>
            <CartesianGrid />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="total_data_mb" stroke="#004e89" />
          </LineChart>
        </div>
      </div>

      {/* Top Clients */}
      <div className="top-clients">
        <h3>Top Clientes</h3>
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Visitas</th>
              <th>Última conexión</th>
              <th>Engagement</th>
            </tr>
          </thead>
          <tbody>
            {stats.top_clients?.map(client => (
              <tr key={client.id}>
                <td>{client.full_name}</td>
                <td>{client.total_visits}</td>
                <td>{new Date(client.last_seen).toLocaleDateString()}</td>
                <td>{client.engagement_score}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

---

## 💳 Fase 3: Sistema de Pagos & Coupones (Semana 2-3)

### Modelo de Cupones:

```python
# apps/products/models.py

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    max_uses = models.IntegerField()
    uses_count = models.IntegerField(default=0)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.offer.name}"

class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    
    redeemed_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    transaction_id = models.CharField(max_length=255, unique=True)
```

### API para validar cupones:

```python
@api_view(['POST'])
def validate_coupon(request):
    """
    POST /api/coupons/validate/
    {
        "code": "DESCUENTO20",
        "client_id": 1,
        "purchase_amount": 50.00
    }
    """
    
    code = request.data.get('code')
    client_id = request.data.get('client_id')
    amount = float(request.data.get('purchase_amount', 0))
    
    try:
        coupon = Coupon.objects.get(code=code)
        
        if not coupon.is_active:
            return Response({'valid': False, 'error': 'Cupón inactivo'})
        
        if coupon.uses_count >= coupon.max_uses:
            return Response({'valid': False, 'error': 'Cupón agotado'})
        
        if timezone.now() > coupon.valid_until:
            return Response({'valid': False, 'error': 'Cupón expirado'})
        
        discount = min(coupon.discount, amount)
        
        return Response({
            'valid': True,
            'discount': discount,
            'final_amount': amount - discount
        })
    
    except Coupon.DoesNotExist:
        return Response({'valid': False, 'error': 'Cupón no válido'})
```

### Integración con Flow (pasarela de pagos chilena):

```bash
pip install flow-sdk
```

```python
# Integración en apps/products/views.py

from flow.sdk import Flow

@api_view(['POST'])
def create_payment(request):
    """Crear pago con Flow"""
    
    client_id = request.data.get('client_id')
    amount = request.data.get('amount')
    coupon_code = request.data.get('coupon_code')
    
    # Validar cupón
    if coupon_code:
        coupon = Coupon.objects.get(code=coupon_code)
        amount = amount - coupon.discount
    
    # Crear pago en Flow
    flow = Flow(
        api_key=settings.FLOW_API_KEY,
        api_secret=settings.FLOW_API_SECRET
    )
    
    payment_data = {
        'amount': int(amount * 100),  # En centavos
        'currency': 'CLP',
        'subject': f'Compra Oferta',
        'email': request.data.get('email'),
        'return_url': 'https://tu-dominio.com/payment/success',
        'callback_url': 'https://tu-dominio.com/api/payment/webhook/',
    }
    
    response = flow.payment.create(**payment_data)
    
    # Guardar en BD
    Payment.objects.create(
        client_id=client_id,
        amount=amount,
        flow_token=response['token'],
        status='pending'
    )
    
    return Response({
        'redirect_url': f"https://sandbox.flow.cl/app/pay/{response['token']}"
    })

@api_view(['POST'])
def payment_webhook(request):
    """Recibir confirmación de pago desde Flow"""
    
    token = request.data.get('token')
    status = request.data.get('status')
    
    payment = Payment.objects.get(flow_token=token)
    
    if status == 'paid':
        payment.status = 'completed'
        
        # Registrar redención
        offer = payment.offer
        offer.uses_count += 1
        offer.save()
        
        # Crear redención
        OfferRedemption.objects.create(
            offer=offer,
            client=payment.client,
            amount_spent=payment.amount
        )
    else:
        payment.status = 'failed'
    
    payment.save()
    return Response({'status': 'ok'})
```

---

## 📱 Fase 4: App Móvil (React Native) (Semana 3-4)

Usar Expo para crear versión móvil rápidamente:

```bash
npx create-expo-app hotspot-mobile
cd hotspot-mobile
npm install axios react-navigation expo-auth-session
```

La mayoría del código (`services/api.js`, `context/AuthContext.jsx`) se puede reutilizar.

---

## 🤖 Fase 5: AI Triage Agent (Similar a JARVIS) (Semana 4-5)

Agregar Claude API para generar ofertas personalizadas:

```python
# apps/analytics/tasks.py

import anthropic

@shared_task
def generate_personalized_offers(client_id):
    """Usar Claude para generar oferta personalizada"""
    
    client = Client.objects.get(id=client_id)
    
    # Recopilar datos del cliente
    sessions = client.sessions.all()
    interactions = client.interactions.all()
    
    prompt = f"""
    Cliente: {client.full_name}
    Teléfono: {client.phone}
    Visitas: {client.total_visits}
    Última conexión: {client.last_seen}
    Datos consumidos: {client.total_data_consumed} bytes
    
    Ofertas vistas: {client.interactions.filter(interaction_type='view').count()}
    Ofertas clicadas: {client.interactions.filter(interaction_type='click').count()}
    
    Disponible en la tienda:
    {json.dumps([o.name for o in Offer.objects.filter(status='active')])}
    
    Genera 1-2 ofertas personalizadas para este cliente que aumenten su probabilidad de compra.
    Considera su patrón de comportamiento y engagement.
    """
    
    client_api = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    response = client_api.messages.create(
        model="claude-opus-4-20250805",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Guardar sugerencia
    Suggestion.objects.create(
        client=client,
        content=response.content[0].text,
        source='ai_agent'
    )
    
    return response.content[0].text
```

---

## 🔄 Fase 6: Integraciones Avanzadas (Semana 5-6)

### 1. WhatsApp Business API (no Twilio)

Conectar directamente a WhatsApp Business:

```python
from whatsapp_business_sdk import Client as WAClient

@task
def send_whatsapp_template():
    wa = WAClient(
        phone_number_id=settings.WA_PHONE_NUMBER_ID,
        access_token=settings.WA_ACCESS_TOKEN
    )
    
    wa.send_template(
        recipient_phone=client.phone,
        template_name='offer_notification',
        template_language='es',
        template_parameters={
            'name': client.full_name,
            'offer_name': offer.name,
            'discount': offer.discount_value
        }
    )
```

### 2. Integración con TPV/POS

Sincronizar ventas directamente:

```python
# Webhook para recibir ventas del TPV
@api_view(['POST'])
def pos_webhook(request):
    """Recibir venta desde TPV fiskal"""
    
    mac_address = request.data.get('mac_address')
    amount = request.data.get('total')
    
    try:
        client = Client.objects.get(mac_address=mac_address)
        
        # Registrar compra
        Purchase.objects.create(
            client=client,
            amount=amount,
            timestamp=timezone.now()
        )
        
        # Enviar promoción post-venta
        send_whatsapp.delay(
            client.id,
            "¡Gracias por tu compra! Aquí va un cupón de 10% para tu próxima visita"
        )
        
    except Client.DoesNotExist:
        pass
    
    return Response({'status': 'ok'})
```

### 3. Programa de Lealtad

```python
class LoyaltyProgram(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    
    total_points = models.IntegerField(default=0)
    tier = models.CharField(
        max_length=20,
        choices=[('bronze', 'Bronce'), ('silver', 'Plata'), ('gold', 'Oro')],
        default='bronze'
    )
    
    @property
    def points_needed_next_tier(self):
        return {
            'bronze': 500,
            'silver': 1500,
            'gold': 3000
        }.get(self.tier, 0) - self.total_points

class LoyaltyTransaction(models.Model):
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 📋 Checklist Implementación

### Para cada fase:

- [ ] Crear rama Git: `git checkout -b feature/fase-X`
- [ ] Agregar modelos en `models.py`
- [ ] Crear migraciones: `python manage.py makemigrations`
- [ ] Crear tests
- [ ] Crear serializers y viewsets
- [ ] Agregar URLs en `urls.py`
- [ ] Actualizar frontend
- [ ] Deployment test en Railway
- [ ] Pull request y merge a `main`

---

## 🎓 Tips para Iterar Rápido

Basándome en tu workflow (JARVIS → NurseCare → MecanIA):

1. **Prototype First**: Implementa la API primero, UI después
2. **Modular Backend**: Cada `app` debe ser independiente
3. **Reutiliza código**: Serializers, Views, Services pueden copiarse entre apps
4. **Database First**: Diseña modelos antes de API
5. **Test Diario**: No dejes que bugs se acumulen
6. **Commits frecuentes**: Cada feature = 1 commit
7. **Documentación**: README + docstrings en funciones críticas

---

¡A construir! 🚀
