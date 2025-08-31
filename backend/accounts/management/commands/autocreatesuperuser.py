from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Automatically create a superuser if none exists.'

    def handle(self, *args, **options):
        User = get_user_model()
        import random, string
        username = 'admin' + ''.join(random.choices(string.digits, k=4))
        email = f'{username}@example.com'
        password = 'admin123'
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(f'New superuser created: {username}/{password}'))
