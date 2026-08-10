from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='DailyAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('new_clients', models.IntegerField(default=0)),
                ('active_clients', models.IntegerField(default=0)),
                ('total_sessions', models.IntegerField(default=0)),
                ('total_data_gb', models.FloatField(default=0)),
                ('avg_session_duration_min', models.FloatField(default=0)),
                ('offers_shown', models.IntegerField(default=0)),
                ('offers_clicked', models.IntegerField(default=0)),
                ('offers_redeemed', models.IntegerField(default=0)),
                ('revenue', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'daily_analytics',
                'ordering': ['-date'],
            },
        ),
    ]
