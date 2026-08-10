from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.CharField(choices=[('whatsapp', 'WhatsApp'), ('email', 'Email'), ('sms', 'SMS'), ('push', 'Push')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('action_url', models.URLField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('sent', 'Enviado'), ('delivered', 'Entregado'), ('failed', 'Fallido')], default='pending', max_length=20)),
                ('external_id', models.CharField(blank=True, max_length=255, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='clients.client')),
                ('offer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.offer')),
            ],
            options={
                'db_table': 'notifications',
                'ordering': ['-created_at'],
            },
        ),
    ]
