import uuid

from django.db import models

from .choices import ChatTypeChoices


class Chat(models.Model):
    """
    Модель чата.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField("users.User")
    type = models.CharField(max_length=8, choices=ChatTypeChoices.choices, default=ChatTypeChoices.DEFAULT)
