from django.core.management.base import BaseCommand
from accounts.models import User  # Adjust if your user model is different

class Command(BaseCommand):
    help = 'Create an admin user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Admin username')
        parser.add_argument('--email', type=str, required=True, help='Admin email')
        parser.add_argument('--password', type=str, required=True, help='Admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User {username} already exists.'))
            return
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='admin'
        )
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Admin user {username} created successfully.'))