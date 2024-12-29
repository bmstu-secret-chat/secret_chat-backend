import json

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

import environ
import requests
from rest_framework import status

env = environ.Env(
    NGINX_URL=(str),
)

NGINX_URL = env("NGINX_URL")

AUTH_PATH = "api/auth"


class TokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware для проверки авторизации пользователя.
    """
    ALLOWED_PATHS = [
        "/api/backend/users/create/",
        "/api/backend/users/check/",
        "/api/backend/users/exists/",
    ]

    def process_request(self, request):
        if any(request.path_info.startswith(path) for path in self.ALLOWED_PATHS):
            return None

        access_token = request.COOKIES.get("access")

        if not access_token:
            return JsonResponse({"error": "Access токен не предоставлен"}, status=status.HTTP_401_UNAUTHORIZED)

        url = f"{NGINX_URL}/{AUTH_PATH}/check/"
        params = {"access": access_token}
        response = requests.get(url, params, verify=False)

        if response.status_code == 200:
            data = response.json()
            user_id = data.get("user_id")
            request.user_id = user_id
        else:
            return JsonResponse(json.loads(response.text), status=response.status_code)
