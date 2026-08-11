from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mikrotik', '0002_wireguard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mikrotikdevice',
            name='host',
            field=models.CharField(
                help_text='IP pública, IP VPN Wireguard o Dominio DDNS (mynetname.net) del Router',
                max_length=255
            ),
        ),
    ]
