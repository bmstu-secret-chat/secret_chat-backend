from rest_framework import serializers

from users.serializers import ShortUserSerializer

from .models import Chat, Message


class ChatSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Chat.
    """
    user = serializers.SerializerMethodField()
    last_action_time = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ("id", "user", "type", "last_action_time")

    def get_user(self, obj):
        request_user = self.context["user"]
        users = obj.users.all()
        for user in users:
            if user != request_user:
                serializer = ShortUserSerializer(user)
                return serializer.data

    def get_last_action_time(self, obj):
        return str(obj.last_action_time)


class MessageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Message.
    """
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    time_create = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("id", "serial_number", "dialog_id", "user_id", "content", "time_create")

    def get_time_create(self, obj):
        return str(obj.time_create)
