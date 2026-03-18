from django.utils.crypto import get_random_string


def get_random_slug(length=12):
    ALPHABET = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'

    slug = get_random_string(length, ALPHABET)

    return slug