import json

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

import environ
import requests
from rest_framework import status

env = environ.Env()

INTERNAL_SECRET_KEY = env("INTERNAL_SECRET_KEY")

NGINX_URL = env("NGINX_URL")

AUTH_PATH = "/api/auth"


class TokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware для проверки авторизации пользователя.
    """
    ALLOWED_PATHS = [
        "/metrics",
        "/api/backend/users/create/",
        "/api/backend/users/check/",
        "/api/backend/users/exists/",
    ]

    ALLOWED_SECRET_PATHS = [
        "/api/backend/users/status/",
    ]

    def process_request(self, request):
        if any(request.path_info.startswith(path) for path in self.ALLOWED_PATHS):
            return None

        if any(request.path_info.startswith(path) for path in self.ALLOWED_SECRET_PATHS):
            secret_key = request.headers.get("X-Internal-Secret")

            if secret_key == INTERNAL_SECRET_KEY:
                return None
            else:
                return JsonResponse({"error": "Отсутствует секретный ключ"}, status=status.HTTP_403_FORBIDDEN)

        access_token = request.COOKIES.get("access")

        if not access_token:
            return JsonResponse({"error": "Access токен не предоставлен"}, status=status.HTTP_401_UNAUTHORIZED)

        url = f"{NGINX_URL}{AUTH_PATH}/check/"
        cookies = {"access": access_token}
        response = requests.get(url, cookies=cookies, verify=False)

        if response.status_code == 200:
            data = response.json()
            user_id = data.get("id")
            request.user_id = user_id
        else:
            return JsonResponse(json.loads(response.text), status=response.status_code)
