from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Creates an admin & user"

    def handle(self, *args, **options):
        user_model = get_user_model()
        admin = user_model.objects.filter(email='admin@admin.com')
        user = user_model.objects.filter(email='test_user@notadmin.com')

        if not admin.exists():
            user_model.objects.create_superuser(email='admin@admin.com', password='nimda')

        if not user.exists():
            user_model.objects.create_user(email='test_user@notadmin.com', password='test_user')