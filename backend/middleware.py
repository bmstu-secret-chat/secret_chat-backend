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

AUTH_PATH = "/api/auth"

BACK_PATH = "/api/backend"


class TokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware для проверки авторизации пользователя.
    """
    ALLOWED_PATHS = [
        "/users/create/",
        "/users/check/",
        "/users/exists/",
    ]

    def process_request(self, request):
        if any(request.path_info.startswith(BACK_PATH + path) for path in self.ALLOWED_PATHS):
            return None

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
