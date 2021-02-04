from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from hasker_posts.models import Questions, Tags, Answers


class Command(BaseCommand):
    help = "Creates an test question and answer and tag for testing"

    def handle(self, *args, **options):
        user_model = get_user_model()

        hasker_user, hasker_user_is_created = user_model.objects.get_or_create(email='hasker@test.com',
                                                                               password='hasker')

        tag, is_created = Tags.objects.get_or_create(tag='Awesome Django')

        question, question_is_created = Questions.objects.get_or_create(
            title="Awesome code",
            contains="Whats a really cool code",
            author=hasker_user,
            votes=10,
            tags=tag,
        )

        Answers.objects.get_or_create(
            question=question,
            contains="Im agree",
            author=hasker_user,
            votes=20
        )
