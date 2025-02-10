import uuid

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils import create_secret_chat

User = get_user_model()


@api_view(["POST"])
def create_secret_chat_view(request):
    """
    Создание секретного чата.
    """
    with_user_id = request.POST.get("with_user_id")

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

    response = create_secret_chat(request.user_id, with_user_id)

    if response.status_code == 201:
        return Response({}, status=status.HTTP_201_CREATED)

    return Response({"error": response.text}, status=response.status_code)
