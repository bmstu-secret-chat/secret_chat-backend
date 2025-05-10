import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .choices import ChatTypeChoices
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from .utils import clear_chat, create_secret_chat, validate_chat_creation

User = get_user_model()


@api_view(["GET"])
def chats_view(request):
    """
    Получение всех чатов пользователя.
    """
    user = User.objects.get(id=request.user_id)
    chats = user.get_chats()
    serializer = ChatSerializer(chats, context={"user": user}, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_secret_chat_view(request):
    """
    Создание секретного чата.
    """
    user_id = request.user_id
    chat_id = uuid.uuid4()
    with_user_id = request.data.get("with_user_id")
    chat_type = ChatTypeChoices.SECRET

    try:
        with_user = validate_chat_creation(user_id, with_user_id)
    except ValidationError as e:
        return Response({"error": e.detail.get("error")}, status=e.detail.get("status"))

    if not with_user.is_online:
        return Response({"error": "Собеседник не в сети"}, status=status.HTTP_423_LOCKED)

    existing_chat = Chat.objects.filter(type=chat_type, users__id=user_id).filter(users__id=with_user_id).first()

    if existing_chat:
        return Response({"id": existing_chat.id}, status=status.HTTP_200_OK)

    user = User.objects.get(id=user_id)
    chat = Chat.objects.create(id=chat_id, type=chat_type)
    chat.users.add(user, with_user)

    response = create_secret_chat(str(chat_id), request.user_id, with_user_id, chat_type)

    if response.status_code != 201:
        chat.delete()
        return Response({"error": response.text}, status=response.status_code)

    return Response({}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def create_chat_view(request):
    """
    Создание чата.
    """
    user_id = request.user_id
    with_user_id = request.data.get("with_user_id")
    chat_type = ChatTypeChoices.DEFAULT

    try:
        with_user = validate_chat_creation(user_id, with_user_id)
    except ValidationError as e:
        return Response({"error": e.detail.get("error")}, status=e.detail.get("status"))

    user = User.objects.get(id=user_id)

    existing_chat = Chat.objects.filter(type=chat_type, users__id=user_id).filter(users__id=with_user_id).first()

    if existing_chat:
        serializer = ChatSerializer(existing_chat, context={"user": user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    chat_id = uuid.uuid4()
    chat = Chat.objects.create(id=chat_id, type=chat_type)
    chat.users.add(user, with_user)

    create_secret_chat(str(chat_id), request.user_id, with_user_id, chat_type)

    serializer = ChatSerializer(chat, context={"user": user})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def chat_view(request, chat_id):
    """
    Получение чата.
    """
    user_id = request.user_id
    user = User.objects.get(id=user_id)

    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({"error": f"Чат с таким id = {chat_id} не найден"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ChatSerializer(chat, context={"user": user})
    return Response(serializer.data, status=status.HTTP_200_OK)


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


@api_view(["GET", "DELETE"])
def messages_view(request, dialog_id):
    """
    Получение сообщений чата.
    """
    match request.method:
        case "GET":
            first_message_index = request.GET.get("first_message_index")
            count = request.GET.get("count")

            try:
                first_message_index = int(first_message_index) - 1
                count = int(count)

                if count <= 0:
                    return Response({"error": "count должен быть больше нуля"})

                if first_message_index < 0:
                    first_message_index = 0

            except (TypeError, ValueError):
                return Response({"error": "Параметры должны быть типа int"}, status=status.HTTP_400_BAD_REQUEST)

            last_message_index = first_message_index + count

            messages = Message.objects.filter(dialog_id=dialog_id).order_by("serial_number")[
                first_message_index:last_message_index
            ]
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        case "DELETE":
            Message.objects.filter(dialog_id=dialog_id).delete()
            clear_chat(dialog_id)
            return Response({}, status=status.HTTP_200_OK)


@api_view(["POST"])
def message_view(request, dialog_id):
    """
    Создание сообщения.
    """
    id = request.data.get("id")
    payload = request.data.get("payload")

    if not payload:
        return Response({"error": "Не переданы данные сообщения"}, status=status.HTTP_400_BAD_REQUEST)

    user_id = payload.get("user_id")
    chat_type = payload.get("chat_type")
    message = payload.get("message")

    if not user_id:
        return Response({"error": "Не передан user_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uuid.UUID(user_id)
    except ValueError:
        return Response({"error": "user_id должен быть в формате uuid"}, status=status.HTTP_400_BAD_REQUEST)

    if not message:
        return Response({"error": "Не передано сообщение"}, status=status.HTTP_400_BAD_REQUEST)

    content = message.get("content")
    time = message.get("time")

    if chat_type:
        try:
            dialog_type_model = ContentType.objects.get_for_model(Chat)
            dialog_id = dialog_id
        except Chat.DoesNotExist:
            return Response({"error": "Чат с таким id не существует"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"error": "chat_id не передан"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": f"Пользователь с id = {user_id} не найден"}, status=status.HTTP_404_NOT_FOUND)

    Message.objects.create(
        id=id, user=user, dialog_type=dialog_type_model, dialog_id=dialog_id, content=content, time_create=time
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
def delete_chat_view(request, chat_id):
    """
    Удаление чата из реалтайма.
    """
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({"error": f"Чат с таким id = {chat_id} не найден"}, status=status.HTTP_404_NOT_FOUND)

    chat.delete()
    return Response(status=status.HTTP_200_OK)
