from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_platform', models.CharField(choices=[('facebook', 'Facebook'), ('instagram', 'Instagram'), ('whatsapp', 'WhatsApp')], max_length=20)),
                ('social_id', models.CharField(max_length=255, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('full_name', models.CharField(max_length=255)),
                ('profile_picture', models.URLField(blank=True, null=True)),
                ('mac_address', models.CharField(blank=True, max_length=17, null=True, unique=True)),
                ('first_location', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('active', 'Activo'), ('inactive', 'Inactivo'), ('blocked', 'Bloqueado')], default='active', max_length=20)),
                ('total_visits', models.IntegerField(default=0)),
                ('total_time_connected', models.DurationField(default=datetime.timedelta(0))),
                ('total_data_consumed', models.BigIntegerField(default=0)),
                ('accepts_marketing', models.BooleanField(default=True)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'clients',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac_address', models.CharField(max_length=17)),
                ('ip_address', models.GenericIPAddressField()),
                ('connected_at', models.DateTimeField(auto_now_add=True)),
                ('disconnected_at', models.DateTimeField(blank=True, null=True)),
                ('data_uploaded', models.BigIntegerField(default=0)),
                ('data_downloaded', models.BigIntegerField(default=0)),
                ('saw_offers', models.BooleanField(default=False)),
                ('interacted_with_offer', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='clients.client')),
            ],
            options={
                'db_table': 'sessions',
                'ordering': ['-connected_at'],
            },
        ),
        migrations.CreateModel(
            name='ClientInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('view', 'Visualización'), ('click', 'Click'), ('dismiss', 'Descartado'), ('convert', 'Conversión')], max_length=20)),
                ('offer_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='clients.client')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='clients.session')),
            ],
            options={
                'db_table': 'client_interactions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['social_id'], name='clients_social__855eb0_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['phone'], name='clients_phone_87cbb8_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['mac_address'], name='clients_mac_add_7df854_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['last_seen'], name='clients_last_se_d4d588_idx'),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['client', 'connected_at'], name='sessions_client__13e002_idx'),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['mac_address'], name='sessions_mac_add_c10444_idx'),
        ),
    ]
