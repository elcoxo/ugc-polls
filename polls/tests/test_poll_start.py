from django.utils import timezone

from polls.models import PollSession


def test_start_creates_session_and_returns_first_question(auth_client, poll_with_questions):
    r = auth_client.post(f'/api/polls/{poll_with_questions.slug}/start/')
    assert r.status_code == 201
    assert 'session_slug' in r.data
    assert r.data['question']['text'] == 'Q1'


def test_repeated_start_returns_same_question(auth_client, poll_with_questions):
    auth_client.post(f'/api/polls/{poll_with_questions.slug}/start/')
    r = auth_client.post(f'/api/polls/{poll_with_questions.slug}/start/')
    assert r.status_code == 200
    assert r.data['question']['text'] == 'Q1'


def test_start_poll_without_questions_returns_400(auth_client, poll):
    r = auth_client.post(f'/api/polls/{poll.slug}/start/')
    assert r.status_code == 400


def test_start_finished_poll_returns_400(auth_client, user, poll_with_questions):
    PollSession.objects.create(user=user, poll=poll_with_questions, finished_at=timezone.now())
    r = auth_client.post(f'/api/polls/{poll_with_questions.slug}/start/')
    assert r.status_code == 400


def test_anonymous_cannot_start_poll(api_client, poll_with_questions):
    r = api_client.post(f'/api/polls/{poll_with_questions.slug}/start/')
    assert r.status_code == 403
