import factory
from django.contrib.auth import get_user_model

from polls.models import (AnswerOption, Poll, PollSession, Question,
                          UserResponse)

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password')


class PollFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Poll

    title = factory.Faker('sentence', nb_words=4, locale='ru_RU')
    user = factory.SubFactory(UserFactory)


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    poll = factory.SubFactory(PollFactory)
    text = factory.Faker('sentence', nb_words=6, locale='ru_RU')
    ordering = factory.Sequence(lambda n: n)


class AnswerOptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnswerOption

    question = factory.SubFactory(QuestionFactory)
    text = factory.Faker('word', locale='ru_RU')
    order = factory.Sequence(lambda n: n)


class PollSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PollSession

    user = factory.SubFactory(UserFactory)
    poll = factory.SubFactory(PollFactory)


class UserResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserResponse

    session = factory.SubFactory(PollSessionFactory)
    question = factory.LazyAttribute(lambda o: o.session.poll.questions.first())
    option = factory.LazyAttribute(lambda o: o.question.options.first())
