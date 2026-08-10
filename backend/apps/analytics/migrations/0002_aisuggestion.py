from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
        ('clients', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AISuggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('reasoning', models.TextField(blank=True, help_text='Justificación de la IA para esta recomendación')),
                ('suggested_discount_percent', models.IntegerField(default=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_dismissed', models.BooleanField(default=False)),
                ('is_accepted', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_suggestions', to='clients.client')),
                ('suggested_offer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.offer')),
            ],
            options={
                'db_table': 'ai_suggestions',
                'ordering': ['-created_at'],
            },
        ),
    ]
