import uuid

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

import boto3
import environ
from botocore.exceptions import ClientError
from PIL import Image
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import UserSerializer

User = get_user_model()

env = environ.Env()

NGINX_URL = env("NGINX_URL")


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
    return Response({"error": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST)


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

    if User.objects.filter(id=user_id).exists():
        return Response({"user_id": user_id}, status=status.HTTP_200_OK)

    return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def user_view(request, user_id):
    """
    Получение пользователя по id.
    """
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


@api_view(['PUT', 'DELETE'])
def profile_view(request):
    """
    Обновление или удаление профиля пользователя.
    """
    user_id = request.user_id
    user = User.objects.get(id=user_id)

    if request.method == 'PUT':
        forbidden_fields = {"id", "password"}

        if any(field in forbidden_fields for field in request.data.keys()):
            return Response({"error": "Нельзя изменять поля id, password"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({}, status=status.HTTP_200_OK)

        errors = [str(e) for field_errors in serializer.errors.values() for e in field_errors]
        return Response({"error": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_avatar_view(request):
    """
    Загрузка аватара в MinIO.
    """
    file = request.FILES["file"]

    try:
        image = Image.open(file)
        image.verify()
    except (IOError, SyntaxError):
        return Response({"error": "Файл не является изображением"}, status=status.HTTP_400_BAD_REQUEST)

    filename = f"{uuid.uuid4()}_{file.name}"

    s3 = boto3.client(
        "s3",
        endpoint_url=NGINX_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        verify=False,
    )

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3.create_bucket(Bucket=bucket_name)

    s3.upload_fileobj(file, bucket_name, filename)

    url = f"{NGINX_URL}/{bucket_name}/{filename}"
    return Response({"url": url}, status=status.HTTP_200_OK)
