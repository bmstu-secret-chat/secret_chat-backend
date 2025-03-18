import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from chats.choices import ChatTypeChoices
from chats.models import Chat, Message

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Базовая модель пользователя.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    avatar = models.URLField(blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    birthday = models.CharField(max_length=10, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    last_online = models.BigIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    sync_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone"]

    def __str__(self):
        return f"{self.username}"

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def get_chats(self):
        """
        Получить все чаты пользователя.
        """
        result = []
        chats = Chat.objects.filter(users=self).order_by("-last_action_time")
        for chat in chats:
            if chat.type == ChatTypeChoices.DEFAULT:
                messages = Message.objects.filter(dialog_id=chat.id)
                if messages:
                    result.append(chat)
            else:
                result.append(chat)

        return result

    def get_secret_chats(self):
        """
        Получить все секретные чаты пользователя.
        """
        return Chat.objects.filter(users=self, type=ChatTypeChoices.SECRET)


class UniqueUserStats(models.Model):
    """
    Модель для сбора статистики уникальных пользователей.
    """
    date = models.DateField(unique=True)
    daily_users = models.IntegerField(default=0)
    monthly_users = models.IntegerField(default=0)
