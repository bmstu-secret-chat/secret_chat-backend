from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели пользователя.
    """
    def create_user(self, username, password):
        """
        Создаёт и возвращает обычного пользователя.
        """
        if not username:
            raise ValueError("У пользователя должно быть имя пользователя.")
        if not password:
            raise ValueError("У пользователя должен быть пароль.")

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user
