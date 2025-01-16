import re

from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


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
            "password",
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
        if self.instance and value != self.instance.username and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value

    def validate_phone(self, value):
        """
        Валидация номера телефона.
        """
        if self.instance and value != self.instance.phone and not re.fullmatch(r"8\d{10}", value):
            raise serializers.ValidationError("Номер телефона должен начинаться с 8 и содержать 11 цифр.")

        if self.instance and value != self.instance.phone and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером телефона уже существует.")

        return value

    def validate_email(self, value):
        """
        Валидация почты.
        """
        if self.instance and value != self.instance.email and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с такой почтой уже существует.")
        return value

    def create(self, validated_data):
        """
        Создание пользователя.
        """
        return User.objects.create_user(**validated_data)
