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
        ordering = ['created_at']

    def __str__(self):
        return f'Poll #{self.id}: {self.title}'


class Question(BaseModel):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    text = models.CharField('Question text', max_length=500)
    ordering = models.PositiveIntegerField('Ordering', default=0)

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


class PollSession(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='sessions',
    )
    slug = models.SlugField(max_length=32, db_index=True, unique=True, default=get_random_slug)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Poll Session'
        verbose_name_plural = 'Poll Sessions'
        unique_together = ('user', 'poll')

    def __str__(self):
        return f'Session by User #{self.user_id} on Poll #{self.poll_id}'

    @property
    def is_finished(self):
        return self.finished_at is not None


class UserResponse(BaseModel):
    session = models.ForeignKey(
        PollSession,
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
        unique_together = ('session', 'question')

    def __str__(self):
        return f'Response: Session #{self.session_id}, Question #{self.question_id}'
