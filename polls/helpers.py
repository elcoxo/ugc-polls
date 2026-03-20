from django.utils.crypto import get_random_string


def get_random_slug(length=12):
    ALPHABET = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'

    slug = get_random_string(length, ALPHABET)

    return slug


def get_next_question(session):
    answered_ids = session.responses.values_list('question_id', flat=True)
    return session.poll.questions.exclude(id__in=answered_ids).first()
