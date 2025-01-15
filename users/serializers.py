from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_username(self, value):
        """
        Валидация имени пользователя.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value

    def create(self, validated_data):
        """
        Создание пользователя.
        """
        return User.objects.create_user(**validated_data)
