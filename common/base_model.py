from django.db import models


class BaseModel(models.Model):
    """Base model with created and updated datetime"""

    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)

    class Meta:
        abstract = True
