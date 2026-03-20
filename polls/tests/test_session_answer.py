import pytest

from polls.models import AnswerOption, Poll, Question, UserResponse


def test_correct_answer_returns_next_question(auth_client, session):
    q1 = session.poll.questions.order_by('ordering').first()
    option = q1.options.first()
    r = auth_client.post(f'/api/sessions/{session.slug}/answer/', {'question': q1.id, 'option': option.id})
    assert r.status_code == 200
    assert r.data['text'] == 'Q2'


def test_last_answer_completes_poll(auth_client, session):
    questions = list(session.poll.questions.order_by('ordering'))
    for q in questions[:-1]:
        UserResponse.objects.create(session=session, question=q, option=q.options.first())

    last_q = questions[-1]
    option = last_q.options.first()
    r = auth_client.post(f'/api/sessions/{session.slug}/answer/', {'question': last_q.id, 'option': option.id})
    assert r.status_code == 200
    assert r.data == {'completed': True}
    session.refresh_from_db()
    assert session.finished_at is not None


def test_duplicate_answer_returns_400(auth_client, session):
    q1 = session.poll.questions.first()
    option = q1.options.first()
    UserResponse.objects.create(session=session, question=q1, option=option)
    r = auth_client.post(f'/api/sessions/{session.slug}/answer/', {'question': q1.id, 'option': option.id})
    assert r.status_code == 400


def test_wrong_option_for_question_returns_400(auth_client, session):
    q1 = session.poll.questions.order_by('ordering').first()
    q2 = session.poll.questions.order_by('ordering').last()
    wrong_option = q2.options.first()
    r = auth_client.post(f'/api/sessions/{session.slug}/answer/', {'question': q1.id, 'option': wrong_option.id})
    assert r.status_code == 400


def test_question_not_in_poll_returns_400(auth_client, user, session):
    other_poll = Poll.objects.create(title='Other', user=user)
    other_q = Question.objects.create(poll=other_poll, text='Other Q', ordering=0)
    other_opt = AnswerOption.objects.create(question=other_q, text='Opt', order=0)
    r = auth_client.post(f'/api/sessions/{session.slug}/answer/', {'question': other_q.id, 'option': other_opt.id})
    assert r.status_code == 400


def test_other_user_cannot_answer(other_auth_client, session):
    q1 = session.poll.questions.first()
    option = q1.options.first()
    r = other_auth_client.post(f'/api/sessions/{session.slug}/answer/', {'question': q1.id, 'option': option.id})
    assert r.status_code == 404
