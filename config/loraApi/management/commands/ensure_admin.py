import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create or update the single application administrator account.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('ADMIN_USERNAME', 'Admin')
        password = os.environ.get('ADMIN_PASSWORD', 'Tash1nga4182')
        admin, created = User.objects.get_or_create(username=username)
        admin.is_staff = True
        admin.is_superuser = True
        if created:
            admin.set_password(password)
        admin.save()
        action = 'created' if created else 'updated'
        self.stdout.write(self.style.SUCCESS(f'Administrator {username} {action}.'))
