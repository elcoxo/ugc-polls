import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from polls.models import AnswerOption, Poll, PollSession, Question

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='temets', password='123')


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username='user', password='123')


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def other_auth_client(api_client, other_user):
    api_client.force_authenticate(user=other_user)
    return api_client


@pytest.fixture
def poll(db, user):
    return Poll.objects.create(title='Test Poll', user=user)


@pytest.fixture
def poll_with_questions(poll):
    q1 = Question.objects.create(poll=poll, text='Q1', ordering=0)
    q2 = Question.objects.create(poll=poll, text='Q2', ordering=1)
    AnswerOption.objects.create(question=q1, text='Yes', order=0)
    AnswerOption.objects.create(question=q1, text='No', order=1)
    AnswerOption.objects.create(question=q2, text='Maybe', order=0)
    return poll


@pytest.fixture
def session(db, user, poll_with_questions):
    return PollSession.objects.create(user=user, poll=poll_with_questions)
