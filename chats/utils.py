import time
import uuid

import environ
import requests
from rest_framework import status
from rest_framework.exceptions import ValidationError

env = environ.Env()

INTERNAL_SECRET_KEY = env("INTERNAL_SECRET_KEY")

NGINX_URL = env("NGINX_URL")

REALTIME_PATH = "/api/realtime"


def get_unix_timestamp():
    """
    Получение текущего времени в timestamp.
    """
    return int(time.time())


def validate_chat_creation(user_id, with_user_id):
    """
    Валидация создания чата.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if not with_user_id:
        raise ValidationError({"error": "with_user_id отсутствует", "status": status.HTTP_400_BAD_REQUEST})

    try:
        uuid.UUID(with_user_id)
    except ValueError:
        raise ValidationError(
            {"error": "with_user_id должен быть в формате uuid", "status": status.HTTP_400_BAD_REQUEST}
        )

    if user_id == with_user_id:
        raise ValidationError({"error": "Нельзя создать чат с самим собой", "status": status.HTTP_400_BAD_REQUEST})

    try:
        with_user = User.objects.get(id=with_user_id)
    except User.DoesNotExist:
        raise ValidationError(
            {"error": f"Пользователь с id = {with_user_id} не найден", "status": status.HTTP_404_NOT_FOUND}
        )

    return with_user


def create_secret_chat(chat_id, user_id, with_user_id, chat_type):
    """
    Запрос на реалтайм для создания чата.
    """
    url = f"{NGINX_URL}{REALTIME_PATH}/messenger/chat/create/"
    headers = {"X-Internal-Secret": INTERNAL_SECRET_KEY}
    data = {"chat_id": chat_id, "user_id": user_id, "with_user_id": with_user_id, "chat_type": chat_type}

    response = requests.post(url, headers=headers, json=data, verify=False)
    return response
