from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def get_chats(request):
    """Получение списка чатов"""
    return Response({"message": "Чаты успешно получены!"}, status=status.HTTP_200_OK)
