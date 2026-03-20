import pytest
from django.utils import timezone

from polls.models import UserResponse


def test_returns_first_unanswered_question(auth_client, session):
    r = auth_client.get(f'/api/sessions/{session.slug}/question/')
    assert r.status_code == 200
    assert r.data['text'] == 'Q1'


def test_returns_next_question_after_answer(auth_client, session):
    q1 = session.poll.questions.order_by('ordering').first()
    option = q1.options.first()
    UserResponse.objects.create(session=session, question=q1, option=option)

    r = auth_client.get(f'/api/sessions/{session.slug}/question/')
    assert r.data['text'] == 'Q2'


def test_finished_session_returns_404(auth_client, session):
    session.finished_at = timezone.now()
    session.save()
    r = auth_client.get(f'/api/sessions/{session.slug}/question/')
    assert r.status_code == 404


def test_other_user_cannot_access_session(other_auth_client, session):
    r = other_auth_client.get(f'/api/sessions/{session.slug}/question/')
    assert r.status_code == 404
