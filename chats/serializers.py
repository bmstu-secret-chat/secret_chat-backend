from rest_framework import serializers

from users.serializers import ShortUserSerializer

from .models import Chat


class ChatSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Chat.
    """
    user = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ("id", "user", "type")

    def get_user(self, obj):
        request_user = self.context["request"].user
        users = obj.users.all()
        for user in users:
            if user != request_user:
                serializer = ShortUserSerializer(user)
                return serializer.data
