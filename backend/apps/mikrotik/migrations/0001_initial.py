from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MikroTikDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('host', models.GenericIPAddressField()),
                ('port', models.IntegerField(default=8728)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('hotspot_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('last_sync', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'mikrotik_devices',
            },
        ),
        migrations.CreateModel(
            name='MikroTikUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('mac_address', models.CharField(max_length=17, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client')),
                ('mikrotik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mikrotik.mikrotikdevice')),
            ],
            options={
                'db_table': 'mikrotik_users',
            },
        ),
        migrations.CreateModel(
            name='MikroTikLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_type', models.CharField(choices=[('sync_users', 'Sincronización de usuarios'), ('sync_sessions', 'Sincronización de sesiones'), ('get_bandwidth', 'Obtener ancho de banda'), ('error', 'Error')], max_length=20)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('success', 'Éxito'), ('error', 'Error')], max_length=20)),
                ('users_processed', models.IntegerField(default=0)),
                ('users_created', models.IntegerField(default=0)),
                ('users_updated', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('mikrotik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='mikrotik.mikrotikdevice')),
            ],
            options={
                'db_table': 'mikrotik_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BandwidthUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('upload_mb', models.FloatField(default=0)),
                ('download_mb', models.FloatField(default=0)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bandwidth_usage', to='clients.client')),
            ],
            options={
                'db_table': 'bandwidth_usage',
                'ordering': ['-date'],
                'unique_together': {('client', 'date')},
            },
        ),
    ]
