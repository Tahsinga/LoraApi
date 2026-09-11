import json

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from loraApi.state_store import load_state, save_state


class Command(BaseCommand):
    help = 'Restore users and cancelled invoice count from the JSON state file.'

    def handle(self, *args, **options):
        state = load_state()
        User = get_user_model()

        for user_data in state.get('users', []):
            username = str(user_data.get('username', '')).strip()
            password = str(user_data.get('password', '')).strip()
            if not username or not password:
                continue

            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = False
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'Updated user: {username}'))

        self.stdout.write(self.style.SUCCESS('State restore complete.'))
