from django.utils import timezone

from polls.models import Poll, PollSession


def test_anonymous_can_list_polls(api_client, poll):
    r = api_client.get('/api/polls/')
    assert r.status_code == 200
    assert len(r.data['results']) == 1


def test_anonymous_has_no_is_finished(api_client, poll):
    r = api_client.get('/api/polls/')
    assert r.data['results'][0]['is_finished'] is None


def test_authenticated_has_is_finished_false(auth_client, poll):
    r = auth_client.get('/api/polls/')
    assert r.data['results'][0]['is_finished'] is False


def test_is_finished_true_when_completed(auth_client, user, poll_with_questions):
    PollSession.objects.create(user=user, poll=poll_with_questions, finished_at=timezone.now())
    r = auth_client.get('/api/polls/')
    assert r.data['results'][0]['is_finished'] is True


def test_anonymous_cannot_create_poll(api_client):
    r = api_client.post('/api/polls/', {'title': 'New Poll'})
    assert r.status_code == 403


def test_authenticated_can_create_poll(auth_client, user):
    r = auth_client.post('/api/polls/', {'title': 'New Poll'})
    assert r.status_code == 201
    assert Poll.objects.filter(user=user, title='New Poll').exists()


def test_author_set_automatically_on_create(auth_client, user):
    r = auth_client.post('/api/polls/', {'title': 'My Poll'})
    assert r.data['user'] == user.username


def test_author_can_update_poll(auth_client, poll):
    r = auth_client.patch(f'/api/polls/{poll.slug}/', {'title': 'Updated'})
    assert r.status_code == 200
    poll.refresh_from_db()
    assert poll.title == 'Updated'


def test_non_author_cannot_update_poll(other_auth_client, poll):
    r = other_auth_client.patch(f'/api/polls/{poll.slug}/', {'title': 'Hacked'})
    assert r.status_code == 404


def test_author_can_delete_poll(auth_client, poll):
    r = auth_client.delete(f'/api/polls/{poll.slug}/')
    assert r.status_code == 204
    assert not Poll.objects.filter(pk=poll.pk).exists()


def test_non_author_cannot_delete_poll(other_auth_client, poll):
    r = other_auth_client.delete(f'/api/polls/{poll.slug}/')
    assert r.status_code == 404
