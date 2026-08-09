"""
Management command: create_superadmin

Crea un superusuario por defecto si no existe ninguno.
Las credenciales se leen desde variables de entorno con fallback seguros.

Uso:
    python manage.py create_superadmin

Variables de entorno (opcionales):
    DJANGO_SUPERUSER_USERNAME  → default: admin
    DJANGO_SUPERUSER_EMAIL     → default: admin@marketinmk.com
    DJANGO_SUPERUSER_PASSWORD  → default: Admin1234! (cambiar en producción)
"""

import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea un superusuario por defecto si no existe ninguno"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@marketinmk.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Admin1234!")

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Ya existe un superusuario. No se creó ninguno nuevo."
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Superusuario creado:\n"
                f"   Usuario:    {username}\n"
                f"   Email:      {email}\n"
                f"   Contraseña: {password}\n"
                f"   ⚠️  Cambia la contraseña después del primer login!"
            )
        )
