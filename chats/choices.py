from django.db import models


class ChatTypeChoices(models.TextChoices):
    """
    Типы для модели Chat.
    """
    DEFAULT = "default"
    SECRET = "secret"
