from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "phone",
            "email",
            "avatar",
            "about_me",
            "birthday",
        )
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

    def validate_phone(self, value):
        """
        Валидация номера телефона.
        """
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером телефона уже существует.")
        return value

    def validate_email(self, value):
        """
        Валидация почты.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с такой почтой уже существует.")
        return value

    def create(self, validated_data):
        """
        Создание пользователя.
        """
        return User.objects.create_user(**validated_data)
