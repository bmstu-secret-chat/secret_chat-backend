import json
import uuid

from django.contrib.auth import authenticate, get_user_model
from django.utils.timezone import now

import environ
import requests
from django_prometheus.exports import ExportToDjangoView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .metrics import update_metrics
from .serializers import UserSerializer

User = get_user_model()

env = environ.Env()

NGINX_URL = env("NGINX_URL")

AUTH_PATH = "/api/auth"


@api_view(['POST'])
def create_view(request):
    """
    Создание пользователя.
    """
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Пользователь успешно создан.", "user": serializer.data},
            status=status.HTTP_201_CREATED
        )

    errors = [str(e) for field_errors in serializer.errors.values() for e in field_errors]
    return Response({"error": "\n".join(errors)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_view(request):
    """
    Проверка пользователя.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Логин и пароль обязательны."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"error": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)

    if user.is_deleted:
        return Response({"error": "Пользователь удалён."}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(user)
    return Response({"message": "Данные верны.", "user": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def exists_view(request):
    """
    Проверка существования пользователя по id.
    """
    user_id = request.GET.get("user_id")

    if not user_id:
        return Response({"error": "Параметр user_id не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT', 'DELETE'])
def user_view(request, user_id):
    """
    Получение, обновление, удаление пользователя.
    """
    current_user_id = request.user_id
    current_user = User.objects.get(id=current_user_id)

    if request.method == 'GET':
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            return Response({"error": "id пользователя должно быть uuid"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        forbidden_fields = {"id", "password"}

        if any(field in forbidden_fields for field in request.data.keys()):
            return Response({"error": "Нельзя изменять поля id, password"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(current_user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({}, status=status.HTTP_200_OK)

        errors = [str(e) for field_errors in serializer.errors.values() for e in field_errors]
        return Response({"error": "\n".join(errors)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        refresh_token = request.COOKIES.get("refresh")

        url = f"{NGINX_URL}{AUTH_PATH}/logout/"
        cookies = {"refresh": refresh_token}
        response = requests.post(url, cookies=cookies, verify=False)

        if response.status_code == 200:
            current_user.delete()
        else:
            return Response(json.loads(response.text), status=response.status_code)

        response = Response({}, status=status.HTTP_200_OK)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


@api_view(['PATCH'])
def status_view(request):
    """
    Обновляет статус пользователя.
    """
    user_id = request.data.get("user_id")
    is_online = request.data.get("is_online")

    if user_id is None or is_online is None:
        return Response({"error": "Отсутствуют необходимые параметры"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(id=user_id)
    if not user.exists():
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    if is_online:
        user.update(is_online=is_online)
    else:
        user.update(is_online=is_online, last_online=int(now().timestamp()))

    return Response({"message": "Статус пользователя обновлён"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def metrics_view(request):
    update_metrics()
    return ExportToDjangoView(request)
