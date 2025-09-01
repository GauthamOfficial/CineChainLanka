from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test user for development'

    def handle(self, *args, **options):
        # Check if test user already exists
        if User.objects.filter(username='admin_user').exists():
            self.stdout.write(
                self.style.WARNING('Test user "admin_user" already exists')
            )
            return

        # Create test user
        user = User.objects.create_user(
            username='admin_user',
            email='admin@cinechainlanka.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            user_type='admin',
            is_staff=True,
            is_superuser=True
        )

        # Create user profile
        UserProfile.objects.create(user=user)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created test user:\n'
                f'Username: admin_user\n'
                f'Password: testpass123\n'
                f'Email: admin@cinechainlanka.com'
            )
        )

