from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mikrotik', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mikrotikdevice',
            name='use_wireguard',
            field=models.BooleanField(default=True, help_text='Conectar a través del túnel VPN Wireguard'),
        ),
        migrations.AddField(
            model_name='mikrotikdevice',
            name='wireguard_ip',
            field=models.GenericIPAddressField(blank=True, help_text='IP asignada al router en la red Wireguard (ej: 10.8.0.2)', null=True),
        ),
        migrations.AddField(
            model_name='mikrotikdevice',
            name='wireguard_public_key',
            field=models.CharField(blank=True, help_text='Clave pública Wireguard del RouterOS', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='mikrotikdevice',
            name='wireguard_preshared_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='mikrotikdevice',
            name='host',
            field=models.GenericIPAddressField(help_text='IP pública o IP VPN Wireguard del Router'),
        ),
    ]
