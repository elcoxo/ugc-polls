import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.transaction import atomic
from django.utils import timezone

from polls.models import Poll

User = get_user_model()


class Command(BaseCommand):
    help = 'First start local project'

    def handle(self, *args, **options):
        with atomic():
            self.create_user()
            self.create_base_poll()
            self.create_test_users()
            self.create_polls()

    def create_user(self):
        """Create admin user if not exists"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@admin.ru', 'admin')

    def create_base_poll(self):
        from polls.models import AnswerOption, Poll, Question

        admin = User.objects.get(username='admin')
        poll = Poll.objects.create(title='Овощи', user=admin)

        questions = [
            ('Ты любишь буратту с помидорами?', ['Да', 'Нет', 'У меня непереносимость лактозы']),
            ('Ты любишь огурцы?', ['Да', 'Нет', 'Только в коктейлях']),
            ('Ты любишь помидоры?', ['Да', 'Нет', 'Только если гаспаччо']),
            ('Ты любишь огуречный салат?', ['Да', 'Нет', 'Только с уксусом']),
        ]

        for ordering, (text, options) in enumerate(questions):
            question = Question.objects.create(poll=poll, text=text, ordering=ordering)
            for order, option_text in enumerate(options):
                AnswerOption.objects.create(question=question, text=option_text, order=order)

    def create_test_users(self):
        from polls.factories import UserFactory

        for i in range(1, 4):
            if not User.objects.filter(username=f'user{i}').exists():
                UserFactory(username=f'user{i}')

    def create_polls(self):
        from polls.factories import (AnswerOptionFactory, PollFactory,
                                     PollSessionFactory, QuestionFactory,
                                     UserResponseFactory)

        admin = User.objects.get(username='admin')
        users = list(User.objects.filter(username__in=['user1', 'user2', 'user3']))

        for _ in range(3):
            poll = PollFactory(user=admin)
            for _ in range(4):
                question = QuestionFactory(poll=poll)
                for _ in range(3):
                    AnswerOptionFactory(question=question)

        polls = list(Poll.objects.filter(user=admin))

        for user in users:
            for poll in polls:
                session = PollSessionFactory(user=user, poll=poll)
                for question in poll.questions.prefetch_related('options'):
                    option = random.choice(list(question.options.all()))
                    UserResponseFactory(session=session, question=question, option=option)
                session.finished_at = timezone.now() + timedelta(seconds=random.randint(5, 15))
                session.save(update_fields=['finished_at'])
