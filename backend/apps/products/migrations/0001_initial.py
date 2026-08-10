from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('icon', models.URLField(blank=True, null=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.URLField()),
                ('short_description', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.category')),
            ],
            options={
                'db_table': 'products',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('offer_type', models.CharField(choices=[('discount', 'Descuento %'), ('fixed', 'Precio fijo'), ('bogo', 'Compra 1 Lleva 2'), ('combo', 'Combo'), ('loyalty', 'Programa de puntos')], max_length=20)),
                ('discount_value', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('discount_type', models.CharField(choices=[('percent', '%'), ('fixed', '$')], default='percent', max_length=10)),
                ('banner_image', models.URLField()),
                ('cta_text', models.CharField(default='Ver oferta', max_length=100)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('draft', 'Borrador'), ('active', 'Activa'), ('paused', 'Pausada'), ('expired', 'Expirada')], default='draft', max_length=20)),
                ('min_purchase', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('max_uses', models.IntegerField(blank=True, null=True)),
                ('uses_count', models.IntegerField(default=0)),
                ('target_all', models.BooleanField(default=True)),
                ('target_first_time', models.BooleanField(default=False)),
                ('target_repeat', models.BooleanField(default=False)),
                ('min_visits', models.IntegerField(default=1)),
                ('show_on_splash', models.BooleanField(default=True)),
                ('send_whatsapp', models.BooleanField(default=True)),
                ('whatsapp_delay_minutes', models.IntegerField(default=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('products', models.ManyToManyField(related_name='offers', to='products.product')),
            ],
            options={
                'db_table': 'offers',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_type', models.CharField(choices=[('percent', '%'), ('fixed', '$')], default='fixed', max_length=10)),
                ('max_uses', models.IntegerField(default=100)),
                ('uses_count', models.IntegerField(default=0)),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid_until', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to='products.offer')),
            ],
            options={
                'db_table': 'coupons',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OfferRedemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redeemed_at', models.DateTimeField(auto_now_add=True)),
                ('value_applied', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('amount_spent', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('notes', models.TextField(blank=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redeemed_offers', to='clients.client')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemptions', to='products.offer')),
            ],
            options={
                'db_table': 'offer_redemptions',
                'ordering': ['-redeemed_at'],
            },
        ),
        migrations.CreateModel(
            name='OfferView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('clicked', models.BooleanField(default=False)),
                ('clicked_at', models.DateTimeField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seen_offers', to='clients.client')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='products.offer')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.session')),
            ],
            options={
                'db_table': 'offer_views',
                'ordering': ['-viewed_at'],
            },
        ),
        migrations.CreateModel(
            name='CouponRedemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redeemed_at', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_id', models.CharField(max_length=255, unique=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon_redemptions', to='clients.client')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemptions', to='products.coupon')),
            ],
            options={
                'db_table': 'coupon_redemptions',
                'ordering': ['-redeemed_at'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('flow_token', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('completed', 'Completado'), ('failed', 'Fallido')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='clients.client')),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.coupon')),
                ('offer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.offer')),
            ],
            options={
                'db_table': 'payments',
                'ordering': ['-created_at'],
            },
        ),
    ]
