from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create a superuser if it doesn't exists"

    def handle(self, *args, **options):

        if not User.objects.filter(is_superuser=True).exists():

            User.objects.create_superuser(
                email="admin@admin.com",
                username="admin",
                password="admin"
            )

            self.stdout.write(self.style.SUCCESS("Superuser admin created successfully."))

        else:
            self.stdout.write(self.style.WARNING("Superuser already exists."))
