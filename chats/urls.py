from django.urls import path

from .views import chat_view, create_secret_chat_view, get_chat_users_view

app_name = "chats"

urlpatterns = [
    path("secret-chat/create/", create_secret_chat_view, name="create-secret-chat"),
    path("<chat_id>/users/", get_chat_users_view, name="get_chat_users_view"),
    path("<chat_id>/", chat_view, name="chat_view"),
]
