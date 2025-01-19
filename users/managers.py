from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели пользователя.
    """
    def create_user(self, username, phone, email, password):
        """
        Создаёт и возвращает обычного пользователя.
        """
        if not username:
            raise ValueError("У пользователя должно быть имя пользователя.")
        if not phone:
            raise ValueError("У пользователя должен быть номер телефона.")
        if not email:
            raise ValueError("У пользователя должна быть электронная почта.")
        if not password:
            raise ValueError("У пользователя должен быть пароль.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user
