import uuid

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .choices import ChatTypeChoices
from .models import Chat
from .utils import create_secret_chat

User = get_user_model()


@api_view(["POST"])
def create_secret_chat_view(request):
    """
    Создание секретного чата.
    """
    chat_id = uuid.uuid4()
    with_user_id = request.data.get("with_user_id")
    chat_type = ChatTypeChoices.SECRET

    if not with_user_id:
        return Response({"error": "with_user_id отсутствует"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uuid.UUID(with_user_id)
    except ValueError:
        return Response({"error": "with_user_id должен быть в формате uuid"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with_user = User.objects.get(id=with_user_id)
    except User.DoesNotExist:
        return Response({"error": f"Пользователь с id = {with_user_id} не найден"}, status=status.HTTP_404_NOT_FOUND)

    if not with_user.is_online:
        return Response({"error": "Собеседник не в сети"}, status=status.HTTP_423_LOCKED)

    user = User.objects.get(id=request.user_id)
    chat = Chat.objects.create(id=chat_id, type=chat_type)
    chat.users.add(user, with_user)

    response = create_secret_chat(str(chat_id), request.user_id, with_user_id, chat_type)

    if response.status_code != 201:
        chat.delete()
        return Response({"error": response.text}, status=response.status_code)

    return Response({}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_chat_users_view(request, chat_id):
    """
    Получение пользователей чата.
    """
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({"error": f"Чат с таким id = {chat_id} не найден"}, status=status.HTTP_404_NOT_FOUND)

    user_ids = chat.users.values_list("id", flat=True)
    return Response(user_ids, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def chat_view(request, chat_id):
    """
    Удаление чата.
    """
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({"error": f"Чат с таким id = {chat_id} не найден"}, status=status.HTTP_404_NOT_FOUND)

    chat.delete()
    return Response(status=status.HTTP_200_OK)
