import environ
import requests

env = environ.Env()

INTERNAL_SECRET_KEY = env("INTERNAL_SECRET_KEY")

NGINX_URL = env("NGINX_URL")

REALTIME_PATH = "/api/realtime"


def create_secret_chat(chat_id, user_id, with_user_id, chat_type):
    """
    Запрос на реалтайм для создания секретного чата.
    """
    url = f"{NGINX_URL}{REALTIME_PATH}/messenger/secret-chat/create/"
    headers = {"X-Internal-Secret": INTERNAL_SECRET_KEY}
    data = {"chat_id": chat_id, "user_id": user_id, "with_user_id": with_user_id, "chat_type": chat_type}

    response = requests.post(url, headers=headers, json=data, verify=False)
    return response
