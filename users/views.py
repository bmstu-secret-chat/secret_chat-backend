import json
import uuid

from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.utils.timezone import now

import environ
import requests
from django_prometheus.exports import ExportToDjangoView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .metrics import update_metrics
from .models import PublicKey
from .serializers import PublicKeySerializer, UserSerializer, ShortUserSerializer

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


@api_view(['GET'])
def user_by_name_view(request):
    """
    Получение пользователя по username.
    """
    username = request.GET.get("username")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "Пользователь с таким username не найден"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ShortUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


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


@api_view(['GET'])
def secret_chats_view(request, user_id):
    """
    Получение всех секретных чатов пользователя.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь с таким id не найден"}, status=status.HTTP_404_NOT_FOUND)

    secret_chat_ids = user.get_secret_chats().values_list("id", flat=True)
    return Response(secret_chat_ids, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def key_view(request, user_id):
    """
    Получение и сохранение публичного ключа пользователя.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь с таким id не найден"}, status=status.HTTP_404_NOT_FOUND)

    match request.method:
        case 'GET':
            try:
                public_key = PublicKey.objects.get(user=user)
                serializer = PublicKeySerializer(public_key)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PublicKey.DoesNotExist:
                return Response({"error": "Публичный ключ не найден"}, status=status.HTTP_404_NOT_FOUND)

        case 'POST':
            if PublicKey.objects.filter(user=user).exists():
                return Response({"error": "У пользователя уже есть публичный ключ"}, status=status.HTTP_400_BAD_REQUEST)

            public_key = request.data.get("public_key")
            PublicKey.objects.create(user=user, public_key=public_key)
            return Response({}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def private_key_get_view(request):
    """
    Получение приватного ключа пользователя.
    """
    username = request.GET.get("username")
    if not username:
        return Response({"error": "username обязательное поле"})

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "Пользователя с таким username не существует"})

    private_key = cache.get(f"user:{user.id}:key")

    if not private_key:
         return Response(
            {"error": "Код не найден, зайдите в профиль на авторизованном устройстве"}, status=status.HTTP_404_NOT_FOUND
        )

    return Response({"private_key": private_key}, status=status.HTTP_200_OK)


@api_view(['POST'])
def private_key_save_view(request):
    """
    Временное сохранение приватного ключа пользователя.
    """
    private_key = request.data.get("private_key")

    if not private_key:
        return Response({"error": "private_key обязательное поле"}, status=status.HTTP_400_BAD_REQUEST)

    cache.set(f"user:{request.user_id}:key", private_key, timeout=60)
    return Response({}, status=status.HTTP_200_OK)
