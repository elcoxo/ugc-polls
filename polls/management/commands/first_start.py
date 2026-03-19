from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

User = get_user_model()


class Command(BaseCommand):
    help = 'First start local project'

    def handle(self, *args, **options):
        with atomic():
            self.create_user()

    def create_user(self):
        """Create admin user if not exists"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@admin.ru', 'admin')
