from django.conf import settings
from django.db import models

from common.base_model import BaseModel
from polls.helpers import get_random_slug


class Poll(BaseModel):
    title = models.CharField('Title', max_length=255)
    slug = models.SlugField(max_length=32, db_index=True, unique=True, default=get_random_slug)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='polls',
    )

    class Meta:
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'

    def __str__(self):
        return f'Poll #{self.id}: {self.title}'


class Question(BaseModel):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    text = models.CharField('Question text', max_length=500)
    is_multiple = models.BooleanField('Multiple choice', default=False)
    ordering = models.PositiveIntegerField('Ordering', null=True, blank=True, default=0)


    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['ordering']

    def __str__(self):
        return f'Question #{self.id}: {self.text}'


class AnswerOption(BaseModel):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
    )
    text = models.CharField('Answer option text', max_length=255)
    order = models.PositiveIntegerField('Order', default=0)

    class Meta:
        verbose_name = 'Answer Option'
        verbose_name_plural = 'Answer Options'
        ordering = ['order']

    def __str__(self):
        return f'Option #{self.id}: {self.text}'


class UserResponse(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses',
    )
    option = models.ForeignKey(
        AnswerOption,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'User Response'
        verbose_name_plural = 'User Responses'
        unique_together = ('user', 'question')

    def __str__(self):
        return f'Response by User #{self.user_id} on Question #{self.question_id}'
