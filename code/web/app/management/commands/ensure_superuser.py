import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Creates an admin user non-interactively if it doesn't exist"

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username=os.environ.get("DJANGO_SUPERUSER_USERNAME")).exists():
            User.objects.create_superuser(
                first_name=os.environ.get("DJANGO_SUPERUSER_FIRST_NAME"),
                last_name=os.environ.get("DJANGO_SUPERUSER_LAST_NAME"),
                username=os.environ.get("DJANGO_SUPERUSER_USERNAME"),
                email=os.environ.get("DJANGO_SUPERUSER_EMAIL"),
                password=os.environ.get("DJANGO_SUPERUSER_PASSWORD")
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully created superuser '{os.environ.get('DJANGO_SUPERUSER_USERNAME')}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{os.environ.get('DJANGO_SUPERUSER_USERNAME')}' already exists"))