import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

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

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone"]

    def __str__(self):
        return f"{self.username}"

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()
