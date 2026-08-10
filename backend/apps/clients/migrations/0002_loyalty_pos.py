from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoyaltyProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_points', models.IntegerField(default=0)),
                ('tier', models.CharField(choices=[('bronze', 'Bronce'), ('silver', 'Plata'), ('gold', 'Oro'), ('platinum', 'Platino')], default='bronze', max_length=20)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='loyalty_program', to='clients.client')),
            ],
            options={
                'db_table': 'loyalty_programs',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pos_terminal_id', models.CharField(blank=True, max_length=100, null=True)),
                ('transaction_reference', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='clients.client')),
            ],
            options={
                'db_table': 'purchases',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LoyaltyTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField()),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='clients.loyaltyprogram')),
            ],
            options={
                'db_table': 'loyalty_transactions',
                'ordering': ['-created_at'],
            },
        ),
    ]
